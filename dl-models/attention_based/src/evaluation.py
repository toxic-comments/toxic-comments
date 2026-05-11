import numpy as np
import torch
from sklearn.metrics import classification_report, average_precision_score

from .dataset import CommentsDataset, CommentsTokenizer, build_dataloader
from .models import ToxicityClassifier


def get_predictions(model: ToxicityClassifier,
                    eval_dataset: CommentsDataset,
                    tokenizer: CommentsTokenizer,
                    criterion: torch.nn.Module = None,
                    ) -> tuple[list[int], list[float], float]:
    dataloader = build_dataloader(eval_dataset, 128 + 64, tokenizer, use_sampling=False)
    model.eval()
    cum_loss = 0
    all_predicted_probas = []
    all_true_labels = []
    with torch.inference_mode():
        for texts, lengths, labels in dataloader:
            texts = texts.to(device=model.device)
            lengths = lengths.to(device=model.device)
            labels = labels.to(device=model.device)
            logits = model(texts, lengths)
            if criterion is not None:
                cum_loss += criterion(logits, labels).item() * labels.size(0)
            pred_probas = torch.nn.functional.softmax(logits, dim=1).detach()
            all_predicted_probas.extend(pred_probas.cpu().numpy())
            all_true_labels.extend(labels.cpu().tolist())
    return all_true_labels, all_predicted_probas, cum_loss / len(dataloader)


def evaluate_model(model: ToxicityClassifier,
                   eval_dataset: CommentsDataset,
                   tokenizer: CommentsTokenizer,
                   criterion: torch.nn.Module = None,
                   ) -> dict[str, float | None]:
    true_labels, pred_probas, loss = get_predictions(model, eval_dataset, tokenizer, criterion)
    report = classification_report(
        true_labels,
        np.array(pred_probas).argmax(axis=1),
        labels=eval_dataset.label_idx,
        target_names=eval_dataset.label_names,
        output_dict=True,
        zero_division=0.0
    )
    ap_per_label = average_precision_score(true_labels, pred_probas, average=None)

    eval_result = {}
    if criterion is not None:
        eval_result["loss"] = loss
    eval_result["macro_f1_score"] = report["macro avg"]["f1-score"]
    for label_idx, label_name in zip(eval_dataset.label_idx, eval_dataset.label_names):
        eval_result[f"{label_name}-f1-score"] = report[label_name]["f1-score"]
        eval_result[f"{label_name}-PR-AUC"] = ap_per_label[label_idx]

    return eval_result
