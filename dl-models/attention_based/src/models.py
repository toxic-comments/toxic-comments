from typing import Literal
import math
import torch
from abc import ABC

from transformers import BertModel
from .dataset import CommentsTokenizer

class ToxicityClassifier(ABC, torch.nn.Module):

    @property
    def device(self):
        return next(self.parameters()).device

    def predict_proba(self, texts: str | list[str], tokenizer: CommentsTokenizer) -> torch.Tensor:
        if type(texts) == str:
            texts = [texts]
        tokens, lengths = tokenizer.encode(list(map(lambda text: text.lower(), texts)))
        tokens.to(device=self.device)
        lengths.to(device=self.device)
        logits = self(tokens, lengths)
        return torch.nn.functional.softmax(logits, dim=1).detach().cpu()


class GRUCommentsClassifier(ToxicityClassifier):

    def __init__(self,
                 embed_matrix: torch.Tensor,
                 padding_id: int,
                 hidden_dim: int,
                 bidirectional: bool,
                 num_layers: int,
                 frozen_embeds: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        vocab_dim, embed_dim = embed_matrix.size()

        self.embedding = torch.nn.Embedding.from_pretrained(
            embed_matrix.float(),
            freeze=frozen_embeds,
            padding_idx=padding_id
        )
        self.gru = torch.nn.GRU(

            batch_first=True,
            input_size=embed_dim,
            hidden_size=hidden_dim,
            bidirectional=bidirectional,
            num_layers=num_layers
        )
        self.linear = torch.nn.Linear(
            in_features=2 * hidden_dim if bidirectional else hidden_dim,
            out_features=4
        )

    def forward(self, x: torch.Tensor, lengths: torch.Tensor):
        # x is (batch, seq_len), lengths is (batch, )
        emb_output = self.embedding(x)  # (batch, seq_len, emb)
        gru_output, _ = self.gru(emb_output)  # (batch, seq_len, hidden x num_layers)
        return self.linear(gru_output[torch.arange(x.size(0)), lengths - 1])


def _build_attention_mask(lengths, max_seq_len, num_heads):
    not_padding_pos = torch.arange(max_seq_len, device=lengths.device).unsqueeze(0) < lengths.unsqueeze(1)
    attn_mask = torch.full((lengths.size(0), max_seq_len, max_seq_len), float("-inf"), device=lengths.device)
    attn_mask[not_padding_pos.unsqueeze(1).expand(-1, max_seq_len, -1)] = 0.0
    attn_mask = attn_mask.repeat_interleave(num_heads, dim=0)

    return attn_mask


class SimpleMHAClassifier(ToxicityClassifier):

    def __init__(self,
                 embed_matrix: torch.Tensor,
                 padding_id: int,
                 num_heads: int,
                 pooling: Literal["mean", "max"],
                 frozen_emb: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        vocab_dim, embed_dim = embed_matrix.size()

        self.embedding = torch.nn.Embedding.from_pretrained(
            embed_matrix.float(),
            freeze=frozen_emb,
            padding_idx=padding_id
        )
        self.attn = torch.nn.MultiheadAttention(
            batch_first=True,
            embed_dim=embed_dim,
            num_heads=num_heads
        )
        self.linear = torch.nn.Linear(
            in_features=embed_dim,
            out_features=4
        )

        self.pooling = pooling
        self.num_heads = num_heads

    def forward(self, x: torch.Tensor, lengths: torch.Tensor):
        attn_mask = _build_attention_mask(lengths, x.size(1), self.num_heads)

        emb_output = self.embedding(x)  # batch, seq_len, emb
        attn_output, _ = self.attn(emb_output, emb_output, emb_output, attn_mask=attn_mask)  # batch, seq_len, emb

        pooled = None
        if self.pooling == "mean":
            pooled = attn_output.mean(dim=1)
        else:
            pooled, _ = torch.max(attn_output, dim=1)

        return self.linear(pooled)


class SinusoidalPositionalEncoding(torch.nn.Module):

    def __init__(self, embed_dim: int, max_seq_length: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.embed_dim = embed_dim
        self.max_seq_length = max_seq_length

        pos_enc = torch.zeros(self.max_seq_length, self.embed_dim)

        # computational stability trick
        dim_term = torch.exp(
            torch.arange(0, self.embed_dim, 2) * (-math.log(10000.0) / self.embed_dim)
        )

        numerator = torch.arange(0, self.max_seq_length).unsqueeze(dim=1)
        pos_enc[:, 0::2] = torch.sin(numerator * dim_term)
        pos_enc[:, 1::2] = torch.cos(numerator * dim_term)

        self.register_buffer("pos_enc", pos_enc.unsqueeze(dim=0))  # 1, max_seq_len, emb_dim

    def forward(self, x):
        # input: batch, seq_len, emb
        return x + self.pos_enc[:, :x.size(1), :]


class PosEncMHAClassifier(ToxicityClassifier):

    def __init__(self,
                 embed_matrix: torch.Tensor,
                 padding_id: int,
                 num_heads: int,
                 frozen_emb: bool = False,
                 max_seq_len: int = 1000,
                 attn_window: int | None = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        vocab_dim, embed_dim = embed_matrix.size()
        self.embedding = torch.nn.Embedding.from_pretrained(
            embed_matrix.float(),
            freeze=frozen_emb,
            padding_idx=padding_id
        )
        self.pos_enc = SinusoidalPositionalEncoding(embed_dim, max_seq_len)
        self.attn = torch.nn.MultiheadAttention(batch_first=True, embed_dim=embed_dim, num_heads=num_heads)
        self.linear = torch.nn.Linear(
            in_features=embed_dim,
            out_features=4
        )

        self.attn_radius = None if attn_window is None else attn_window // 2
        self.num_heads = num_heads

    def forward(self, x, lengths):
        attn_mask = _build_attention_mask(lengths, x.size(1), self.num_heads)

        if self.attn_radius is not None:
            attn_mask = torch.full((x.size(1), x.size(1)), float("-inf"), device=x.device)
            for i in range(x.size(1)):
                left = max(0, i - self.attn_radius)
                right = min(x.size(1), i + self.attn_radius + 1)
                attn_mask[i, left:right] = 0.0

        emb_output = self.embedding(x)  # batch, seq_len, embed_dim
        pos_emb = self.pos_enc(emb_output)
        attn_output, _ = self.attn(pos_emb, pos_emb, pos_emb, attn_mask=attn_mask)  # batch, seq_len, embed_dim
        pooled, _ = torch.max(attn_output, dim=1)

        return self.linear(pooled)


class PretrainedBertClassifier(ToxicityClassifier):

    def __init__(self,
                 bert_name: str,
                 pooling: Literal["max", "mean"] | None = None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bert = BertModel.from_pretrained(bert_name)
        self.linear = torch.nn.Linear(in_features=self.bert.config.hidden_size, out_features=4)

        self.pooling = pooling

    def forward(self, x, attention_mask):

        bert_output = self.bert(input_ids=x, attention_mask=attention_mask)

        pooled = bert_output.pooler_output
        if self.pooling is not None:
            if self.pooling == "mean":
                pooled = bert_output.last_hidden_state.mean(dim=1)
            if self.pooling == "max":
                pooled, _ = torch.max(bert_output.last_hidden_state, dim=1)

        return self.linear(pooled)



