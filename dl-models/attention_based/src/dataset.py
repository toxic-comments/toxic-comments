import os
from abc import ABC, abstractmethod
from typing import Literal, Iterable

import numpy as np
import polars as pl
import torch
from sentencepiece import SentencePieceTrainer, SentencePieceProcessor
from transformers import BertTokenizer

TEMP_FILES_DIRECTORY = "temp/"

class CommentsTokenizer(ABC):

    @abstractmethod
    def encode(self, texts: list[str]) -> tuple[torch.Tensor, torch.Tensor]:
        pass

    @abstractmethod
    def decode(self, id: int) -> str:
        pass

class SentencePieceTokenizer(CommentsTokenizer):

    def __init__(
            self,
            token_type: Literal["bpe", "unigram"],
            vocab_size: int,
            train_text: Iterable[str],
            directory: str = TEMP_FILES_DIRECTORY,
            unk_id: int  = 1,
            pad_id: int = 0
    ):
        self.vocab_size = vocab_size
        model_name = f"{token_type}_{vocab_size}"
        model_suffix = ".model"
        if not os.path.isfile(directory + model_name + model_suffix):
            SentencePieceTrainer.train(
                sentence_iterator=train_text,
                model_prefix=directory + model_name,
                model_type=token_type,
                vocab_size=vocab_size,
                unk_id=unk_id,
                pad_id=pad_id,
                bos_id=2,
                eos_id=3
            )
        self.tokenizer = SentencePieceProcessor(model_file=directory + model_name + model_suffix)
        self.pad_id = pad_id

    def encode(self, texts: list[str]):
        batch_tokens = []
        max_len = 0
        for text in texts:
            tokens = self.tokenizer.encode(text)
            if len(tokens) > max_len:
                max_len = len(tokens)
            batch_tokens.append(torch.tensor(tokens))
        padded = [
            torch.nn.functional.pad(tokens, (0, max_len - len(tokens)), value=self.pad_id)
            for tokens in batch_tokens
        ]
        real_lengths = torch.tensor([len(tokens) for tokens in batch_tokens])
        return torch.vstack(padded), real_lengths

    def decode(self, id: int):
        return self.tokenizer.decode(id)


class CommentsBertTokenizer(CommentsTokenizer):

    def __init__(self, model_name: str):
        self.tokenizer: BertTokenizer = BertTokenizer.from_pretrained(model_name)

    def encode(self, texts: list[str]):
        output = self.tokenizer(texts, padding=True, return_tensors="pt")
        return output["input_ids"], output["attention_mask"]

    def decode(self, id: int):
        return self.tokenizer.decode(id)


class CommentsDataset(torch.utils.data.Dataset):
    """
    Torch dataset for loading comments from a csv file
    """
    LABEL_MAPPING = {
        "NORMAL": 0,
        "INSULT": 1,
        "THREAT": 2,
        "OBSCENITY": 3
    }
    def __init__(self, filename: str):
        data_sorted = (
            pl.read_csv(filename)
            .sort(pl.col("comment").str.len_chars())
            .with_columns(pl.col("label").replace_strict(self.LABEL_MAPPING).alias("label"))
        )
        self.comments = data_sorted["comment"]
        self.labels = data_sorted["label"]

    def __len__(self):
        return len(self.comments)

    def __getitem__(self, idx):
        return self.comments[idx], self.labels[idx]

    @property
    def label_idx(self):
        return sorted(self.LABEL_MAPPING.values())

    @property
    def label_names(self):
        reverse = { value: key for key, value in self.LABEL_MAPPING.items() }
        return [reverse[id] for id in self.label_idx]


def pad_collate(batch: list[tuple[str, int]], tokenizer: CommentsTokenizer):
    """
    Pad to maximum length in a batch
    :returns Tuple with values:
    * tensor (batch_size, max_seq_len) -
    * tensor (batch_size, ) - real length of text sequencies
    * tensor (batch_size, ) - labels
    """
    comments, labels = zip(*batch)
    batch_tokenized, lengths = tokenizer.encode(comments)
    return batch_tokenized, lengths, torch.tensor(labels)

def build_dataloader(
        dataset: CommentsDataset,
        batch_size: int,
        tokenizer: CommentsTokenizer,
        use_sampling: bool
) -> torch.utils.data.DataLoader:

    sampler = None

    if use_sampling:
        class_counts = np.bincount(dataset.labels)
        sample_weights = torch.FloatTensor(1 / class_counts[dataset.labels])
        sampler = torch.utils.data.WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)

    return torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        collate_fn=lambda batch: pad_collate(batch, tokenizer),
        sampler=sampler
    )