"""
UNMUTE - Static Sign Recognition Model Evaluation Pipeline
Evaluates StaticASL_MLP and StaticISL_MLP models against held-out test splits,
calculating overall Accuracy, Macro/Weighted Precision, Recall, F1-scores,
per-class classification metrics, and generating high-resolution confusion matrix heatmaps.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless reporting
import matplotlib.pyplot as plt
import seaborn as sns

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import SignLanguage, get_classes
from ml.data.dataset import StaticSignDataset
from ml.models.static_mlp import StaticASL_MLP, StaticISL_MLP


def compute_classification_metrics(
    y_true: Union[List[int], np.ndarray, torch.Tensor],
    y_pred: Union[List[int], np.ndarray, torch.Tensor],
    class_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Computes rigorous classification metrics without inventing metrics.

    Returns:
        Dictionary containing:
        - accuracy: float
        - macro_precision, macro_recall, macro_f1: float
        - weighted_precision, weighted_recall, weighted_f1: float
        - per_class: dict of {class_name: {precision, recall, f1-score, support}}
        - confusion_matrix: 2D list of integer counts
        - total_samples: int
    """
    if isinstance(y_true, torch.Tensor):
        y_true = y_true.detach().cpu().numpy()
    if isinstance(y_pred, torch.Tensor):
        y_pred = y_pred.detach().cpu().numpy()

    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))

    prec_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    # Per-class report dictionary
    labels_present = np.unique(np.concatenate([y_true, y_pred]))
    target_names = [class_names[i] if class_names and i < len(class_names) else str(i) for i in labels_present]
    
    report_dict = classification_report(
        y_true,
        y_pred,
        labels=labels_present,
        target_names=target_names,
        output_dict=True,
        zero_division=0,
    )

    # 2D Confusion matrix
    num_classes = len(class_names) if class_names else int(max(np.max(y_true), np.max(y_pred)) + 1)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))

    return {
        "accuracy": acc,
        "macro_precision": prec_macro,
        "macro_recall": rec_macro,
        "macro_f1": f1_macro,
        "weighted_precision": prec_weighted,
        "weighted_recall": rec_weighted,
        "weighted_f1": f1_weighted,
        "total_samples": int(len(y_true)),
        "per_class": report_dict,
        "confusion_matrix": cm.tolist(),
    }


def plot_confusion_matrix(
    cm: Union[np.ndarray, List[List[int]]],
    class_names: List[str],
    output_path: str,
    title: str = "Sign Language Static Recognition Confusion Matrix",
    figsize: Tuple[int, int] = (16, 14),
) -> str:
    """
    Renders and saves a publication-grade confusion matrix heatmap.
    """
    cm = np.asarray(cm)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    plt.figure(figsize=figsize)
    sns.set_theme(style="white", font_scale=0.75)

    # Plot normalized counts or raw values
    ax = sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=True,
        xticklabels=class_names,
        yticklabels=class_names,
        linewidths=0.5,
        linecolor="#e0e0e0",
    )

    plt.title(title, fontsize=14, fontweight="bold", pad=16)
    plt.xlabel("Predicted Class", fontsize=12, labelpad=10)
    plt.ylabel("Ground Truth Class", fontsize=12, labelpad=10)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()

    plt.savefig(output_path, dpi=200)
    plt.close()
    return output_path


@torch.no_grad()
def evaluate_model_on_dataset(
    model: nn.Module,
    dataset: Union[StaticSignDataset, torch.utils.data.DataLoader],
    device: torch.device = torch.device("cpu"),
    class_names: Optional[List[str]] = None,
) -> Tuple[Dict[str, Any], np.ndarray, np.ndarray]:
    """
    Runs model inference across the full evaluation dataset and computes metrics.
    """
    model.eval()
    model.to(device)

    if isinstance(dataset, StaticSignDataset):
        loader = torch.utils.data.DataLoader(dataset, batch_size=64, shuffle=False)
    else:
        loader = dataset

    all_preds = []
    all_targets = []

    for batch_x, batch_y in loader:
        batch_x = batch_x.to(device)
        logits = model(batch_x)
        preds = torch.argmax(logits, dim=-1)

        all_preds.extend(preds.cpu().numpy().tolist())
        all_targets.extend(batch_y.numpy().tolist())

    y_pred = np.array(all_preds, dtype=int)
    y_true = np.array(all_targets, dtype=int)

    metrics = compute_classification_metrics(y_true, y_pred, class_names=class_names)
    return metrics, y_true, y_pred


def evaluate_static_checkpoint(
    checkpoint_path: str,
    test_data_path: str,
    language: SignLanguage = SignLanguage.ASL,
    output_dir: str = "reports",
) -> Dict[str, Any]:
    """
    High-level entrypoint: loads model checkpoint, evaluates on held-out test split,
    generates confusion matrix heatmap and JSON report.
    """
    class_names = get_classes(language)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model from checkpoint
    if language == SignLanguage.ASL:
        model = StaticASL_MLP.load_checkpoint(checkpoint_path, map_location=device)
    else:
        model = StaticISL_MLP.load_checkpoint(checkpoint_path, map_location=device)

    # Load held-out test split
    test_dataset = StaticSignDataset(npz_path=test_data_path)

    # Evaluate
    metrics, y_true, y_pred = evaluate_model_on_dataset(
        model, test_dataset, device=device, class_names=class_names
    )

    # Export paths
    os.makedirs(output_dir, exist_ok=True)
    lang_code = language.value.lower()
    cm_path = os.path.join(output_dir, f"{lang_code}_confusion_matrix.png")
    json_path = os.path.join(output_dir, f"{lang_code}_evaluation_report.json")

    # Plot confusion matrix
    plot_confusion_matrix(
        metrics["confusion_matrix"],
        class_names=class_names,
        output_path=cm_path,
        title=f"UNMUTE — {language.value} Static Recognition Confusion Matrix (Test Split)",
    )

    # Prepare report dict
    report_data = {
        "language": language.value,
        "checkpoint": os.path.relpath(checkpoint_path, REPO_ROOT),
        "test_dataset": os.path.relpath(test_data_path, REPO_ROOT),
        "total_test_samples": metrics["total_samples"],
        "accuracy": metrics["accuracy"],
        "macro_precision": metrics["macro_precision"],
        "macro_recall": metrics["macro_recall"],
        "macro_f1": metrics["macro_f1"],
        "weighted_precision": metrics["weighted_precision"],
        "weighted_recall": metrics["weighted_recall"],
        "weighted_f1": metrics["weighted_f1"],
        "per_class_metrics": metrics["per_class"],
        "confusion_matrix_image": os.path.relpath(cm_path, REPO_ROOT),
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    return report_data


def main():
    parser = argparse.ArgumentParser(description="Evaluate UNMUTE static recognition models.")
    parser.add_argument("--language", type=str, choices=["ASL", "ISL"], default="ASL", help="Sign language mode")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint (.pt)")
    parser.add_argument("--test-data", type=str, default=None, help="Path to held-out test split (.npz)")
    parser.add_argument("--output-dir", type=str, default="reports", help="Directory to save reports")
    args = parser.parse_args()

    lang = SignLanguage.ASL if args.language == "ASL" else SignLanguage.ISL
    ckpt = args.checkpoint or os.path.join("models", f"{lang.value.lower()}_static_mlp.pt")
    test_data = args.test_data or os.path.join("data", f"{lang.value.lower()}_test.npz")

    print(f"--- UNMUTE Static Model Evaluation ---")
    print(f"Language:   {lang.value}")
    print(f"Checkpoint: {ckpt}")
    print(f"Test Data:  {test_data}")

    report = evaluate_static_checkpoint(ckpt, test_data, language=lang, output_dir=args.output_dir)

    print(f"\n--- Results Summary ---")
    print(f"Overall Accuracy:  {report['accuracy'] * 100:.2f}%")
    print(f"Macro F1-Score:    {report['macro_f1'] * 100:.2f}%")
    print(f"Weighted F1-Score: {report['weighted_f1'] * 100:.2f}%")
    print(f"Evaluation report saved to: {os.path.join(args.output_dir, f'{lang.value.lower()}_evaluation_report.json')}")
    print(f"Confusion matrix saved to:  {os.path.join(args.output_dir, f'{lang.value.lower()}_confusion_matrix.png')}")


if __name__ == "__main__":
    main()
