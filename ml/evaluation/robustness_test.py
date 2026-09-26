"""
UNMUTE - Contributor 1: Comprehensive Model Robustness & Comparative Benchmark
Evaluates static recognition models under:
1. Feature Gaussian Noise Perturbations (sensor tremor, low-light tracking variance)
2. ISL Single-Hand Fallback & Secondary Hand Occlusion Scenarios
3. Comparative Benchmark against Legacy Random Forest Baseline
Exports findings to reports/model_comparison_report.json.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional
import numpy as np
import torch
import torch.nn as nn
import joblib

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import SignLanguage, get_classes
from ml.data.dataset import StaticSignDataset
from ml.models.static_mlp import StaticASL_MLP, StaticISL_MLP
from ml.evaluation.evaluate_static import compute_classification_metrics


def evaluate_noise_robustness(
    model: nn.Module,
    test_dataset: StaticSignDataset,
    sigmas: List[float] = [0.0, 0.01, 0.02, 0.05, 0.10],
    device: torch.device = torch.device("cpu"),
) -> Dict[str, Any]:
    """
    Evaluates model resilience under escalating Gaussian feature perturbations.
    """
    model.eval()
    model.to(device)

    base_features = test_dataset.features.clone()
    labels = test_dataset.labels.numpy()
    results = {}

    for sigma in sigmas:
        torch.manual_seed(42)
        if sigma > 0:
            noise = torch.randn_like(base_features) * sigma
            noisy_features = base_features + noise
        else:
            noisy_features = base_features

        with torch.no_grad():
            logits = model(noisy_features.to(device))
            preds = torch.argmax(logits, dim=-1).cpu().numpy()

        metrics = compute_classification_metrics(labels, preds)
        results[f"sigma_{sigma:.2f}"] = {
            "sigma": sigma,
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "weighted_f1": metrics["weighted_f1"],
        }

    return results


def evaluate_isl_single_hand_fallback(
    isl_model: StaticISL_MLP,
    isl_dataset: StaticSignDataset,
    device: torch.device = torch.device("cpu"),
) -> Dict[str, Any]:
    """
    Tests ISL bimanual model degradation when the secondary hand is occluded or not detected.
    Features:
      0..108:   Primary hand
      109..217: Secondary hand
      218..227: Inter-hand metrics
    """
    isl_model.eval()
    isl_model.to(device)

    features = isl_dataset.features.clone()
    labels = isl_dataset.labels.numpy()

    # 1. Full dual-hand baseline
    with torch.no_grad():
        logits_full = isl_model(features.to(device))
        preds_full = torch.argmax(logits_full, dim=-1).cpu().numpy()
    metrics_full = compute_classification_metrics(labels, preds_full)

    # 2. Secondary hand zeroed out (single-hand fallback scenario)
    features_fallback = features.clone()
    features_fallback[:, 109:] = 0.0  # Zero secondary hand + inter-hand metrics

    with torch.no_grad():
        logits_fallback = isl_model(features_fallback.to(device))
        preds_fallback = torch.argmax(logits_fallback, dim=-1).cpu().numpy()
    metrics_fallback = compute_classification_metrics(labels, preds_fallback)

    return {
        "full_dual_hand": {
            "accuracy": metrics_full["accuracy"],
            "macro_f1": metrics_full["macro_f1"],
        },
        "single_hand_fallback": {
            "accuracy": metrics_fallback["accuracy"],
            "macro_f1": metrics_fallback["macro_f1"],
        },
        "relative_retention": round(
            (metrics_fallback["accuracy"] / (metrics_full["accuracy"] + 1e-6)), 4
        ),
    }


def benchmark_against_legacy_rf(
    asl_mlp_model: StaticASL_MLP,
    asl_dataset: StaticSignDataset,
    rf_model_path: str = "models/asl_rf_model.joblib",
) -> Dict[str, Any]:
    """
    Compares the PyTorch ASL MLP against the legacy Random Forest baseline model.
    """
    X_test = asl_dataset.features.numpy()
    y_test = asl_dataset.labels.numpy()
    num_samples = len(X_test)

    # 1. Benchmark PyTorch ASL MLP
    asl_mlp_model.eval()
    t0 = time.perf_counter()
    with torch.no_grad():
        logits = asl_mlp_model(asl_dataset.features)
        mlp_preds = torch.argmax(logits, dim=-1).numpy()
    mlp_latency_ms = ((time.perf_counter() - t0) / num_samples) * 1000
    mlp_metrics = compute_classification_metrics(y_test, mlp_preds)

    mlp_params = sum(p.numel() for p in asl_mlp_model.parameters())

    mlp_summary = {
        "model_type": "StaticASL_MLP (PyTorch)",
        "parameter_count": mlp_params,
        "latency_ms_per_sample": round(mlp_latency_ms, 3),
        "accuracy": mlp_metrics["accuracy"],
        "macro_f1": mlp_metrics["macro_f1"],
        "weighted_f1": mlp_metrics["weighted_f1"],
    }

    # 2. Benchmark Legacy Random Forest
    rf_summary = {}
    if os.path.exists(rf_model_path):
        rf_model = joblib.load(rf_model_path)
        t0 = time.perf_counter()
        rf_preds_raw = rf_model.predict(X_test)
        rf_latency_ms = ((time.perf_counter() - t0) / num_samples) * 1000

        # RF classes might be strings or ints
        if isinstance(rf_preds_raw[0], str):
            classes = get_classes(SignLanguage.ASL)
            class_to_idx = {c: i for i, c in enumerate(classes)}
            rf_preds = np.array([class_to_idx.get(p, 0) for p in rf_preds_raw])
        else:
            rf_preds = rf_preds_raw.astype(int)

        rf_metrics = compute_classification_metrics(y_test, rf_preds)
        rf_file_size_mb = os.path.getsize(rf_model_path) / (1024 * 1024)

        rf_summary = {
            "model_type": "RandomForestClassifier (Scikit-Learn Baseline)",
            "file_size_mb": round(rf_file_size_mb, 2),
            "latency_ms_per_sample": round(rf_latency_ms, 3),
            "accuracy": rf_metrics["accuracy"],
            "macro_f1": rf_metrics["macro_f1"],
            "weighted_f1": rf_metrics["weighted_f1"],
        }
    else:
        rf_summary = {"status": "Legacy RF checkpoint not available at path."}

    return {
        "pytorch_asl_mlp": mlp_summary,
        "legacy_random_forest": rf_summary,
    }


def run_comprehensive_robustness_evaluation(
    output_path: str = "reports/model_comparison_report.json",
) -> Dict[str, Any]:
    """
    Executes all robustness evaluations and saves unified report.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load datasets
    asl_test_ds = StaticSignDataset(npz_path="data/asl_test.npz")
    isl_test_ds = StaticSignDataset(npz_path="data/isl_test.npz")

    # Load models
    asl_model = StaticASL_MLP.load_checkpoint("models/asl_static_mlp.pt", map_location=device)
    isl_model = StaticISL_MLP.load_checkpoint("models/isl_static_mlp.pt", map_location=device)

    print("--- Running Noise Robustness Evaluation (ASL) ---")
    asl_noise = evaluate_noise_robustness(asl_model, asl_test_ds, device=device)

    print("--- Running Noise Robustness Evaluation (ISL) ---")
    isl_noise = evaluate_noise_robustness(isl_model, isl_test_ds, device=device)

    print("--- Running ISL Single-Hand Fallback Evaluation ---")
    isl_fallback = evaluate_isl_single_hand_fallback(isl_model, isl_test_ds, device=device)

    print("--- Running Comparative Benchmark vs Legacy Random Forest ---")
    rf_comparison = benchmark_against_legacy_rf(asl_model, asl_test_ds, rf_model_path="models/asl_rf_model.joblib")

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "asl_noise_robustness": asl_noise,
        "isl_noise_robustness": isl_noise,
        "isl_single_hand_fallback": isl_fallback,
        "baseline_comparison": rf_comparison,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nRobustness and comparison report exported to: {output_path}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UNMUTE Robustness & Comparative Benchmark")
    parser.add_argument("--output", default="reports/model_comparison_report.json", help="Path to output report JSON")
    args = parser.parse_args()

    run_comprehensive_robustness_evaluation(output_path=args.output)
