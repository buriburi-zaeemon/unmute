"""
Automated unit and integration tests for UNMUTE static model evaluation pipeline:
- Classification metric computations (accuracy, macro/weighted precision, recall, F1)
- Confusion matrix array structure and properties
- High-resolution heatmap rendering to disk
- evaluate_model_on_dataset batch inference execution
- JSON evaluation report validation and structure
"""

import os
import sys
import json
import pytest
import numpy as np
import torch
import torch.nn as nn

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import SignLanguage, get_classes
from ml.data.dataset import StaticSignDataset
from ml.models.static_mlp import StaticASL_MLP
from ml.evaluation.evaluate_static import (
    compute_classification_metrics,
    plot_confusion_matrix,
    evaluate_model_on_dataset,
    evaluate_static_checkpoint,
)


class TestMetricCalculations:
    """Tests accuracy, precision, recall, F1, and confusion matrix computations."""

    def test_perfect_classification_metrics(self):
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 1, 2])
        class_names = ["A", "B", "C"]

        metrics = compute_classification_metrics(y_true, y_pred, class_names=class_names)
        assert metrics["total_samples"] == 6
        assert metrics["accuracy"] == 1.0
        assert metrics["macro_precision"] == 1.0
        assert metrics["macro_recall"] == 1.0
        assert metrics["macro_f1"] == 1.0
        assert metrics["weighted_f1"] == 1.0
        assert "A" in metrics["per_class"]
        assert "B" in metrics["per_class"]
        assert "C" in metrics["per_class"]
        cm_array = np.array(metrics["confusion_matrix"])
        assert np.array_equal(cm_array, np.diag([2, 2, 2]))

    def test_imbalanced_classification_metrics(self):
        y_true = [0, 0, 0, 1, 1, 2]
        y_pred = [0, 0, 1, 1, 0, 2]
        class_names = ["Class0", "Class1", "Class2"]

        metrics = compute_classification_metrics(y_true, y_pred, class_names=class_names)
        assert metrics["total_samples"] == 6
        assert 0.0 < metrics["accuracy"] < 1.0
        assert "per_class" in metrics
        cm_array = np.array(metrics["confusion_matrix"])
        assert cm_array.shape == (3, 3)

    def test_torch_tensor_inputs(self):
        y_true = torch.tensor([0, 1, 1, 2])
        y_pred = torch.tensor([0, 1, 0, 2])
        metrics = compute_classification_metrics(y_true, y_pred)
        assert metrics["total_samples"] == 4
        assert metrics["accuracy"] == 0.75


class TestHeatmapGeneration:
    """Tests confusion matrix plotting and disk rendering."""

    def test_plot_confusion_matrix_creation(self, tmp_path):
        cm = np.array([[10, 2], [1, 15]])
        classes = ["YES", "NO"]
        out_png = str(tmp_path / "test_cm.png")

        result_path = plot_confusion_matrix(cm, class_names=classes, output_path=out_png, title="Test CM")
        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 1000  # valid image file


class TestModelInferenceEvaluation:
    """Tests batch inference and dataset evaluation."""

    def test_evaluate_model_on_dataset_synthetic(self):
        input_dim = 109
        num_classes = 5
        num_samples = 20

        # Simple linear model
        model = nn.Linear(input_dim, num_classes)
        features = np.random.randn(num_samples, input_dim).astype(np.float32)
        labels = np.random.randint(0, num_classes, size=(num_samples,)).astype(np.int64)

        dataset = StaticSignDataset(features=features, labels=labels)
        metrics, y_true, y_pred = evaluate_model_on_dataset(
            model, dataset, device=torch.device("cpu"), class_names=[f"C{i}" for i in range(num_classes)]
        )

        assert metrics["total_samples"] == num_samples
        assert len(y_true) == num_samples
        assert len(y_pred) == num_samples
        cm_array = np.array(metrics["confusion_matrix"])
        assert cm_array.shape == (num_classes, num_classes)


class TestGeneratedEvaluationReports:
    """Verifies that generated evaluation reports conform to production specifications."""

    def test_asl_report_schema(self):
        asl_report_path = os.path.join(REPO_ROOT, "reports", "asl_evaluation_report.json")
        assert os.path.exists(asl_report_path), "ASL evaluation report should exist"

        with open(asl_report_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == "ASL"
        assert "total_test_samples" in data
        assert data["total_test_samples"] > 0
        assert "accuracy" in data
        assert "macro_f1" in data
        assert "weighted_f1" in data
        assert "per_class_metrics" in data
        assert os.path.exists(os.path.join(REPO_ROOT, data["confusion_matrix_image"]))

    def test_isl_report_schema(self):
        isl_report_path = os.path.join(REPO_ROOT, "reports", "isl_evaluation_report.json")
        assert os.path.exists(isl_report_path), "ISL evaluation report should exist"

        with open(isl_report_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["language"] == "ISL"
        assert "total_test_samples" in data
        assert data["total_test_samples"] > 0
        assert "accuracy" in data
        assert "macro_f1" in data
        assert "weighted_f1" in data
        assert "per_class_metrics" in data
        assert os.path.exists(os.path.join(REPO_ROOT, data["confusion_matrix_image"]))
