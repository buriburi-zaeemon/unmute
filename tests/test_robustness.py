"""
Automated unit and integration test suite for UNMUTE robustness, data augmentation,
and comparative baseline benchmarks:
- Gaussian landmark jitter, scale perturbation, channel dropout transforms
- Inverse-frequency class weighting properties
- Single-hand fallback inference stability for bimanual ISL models
- Noise perturbation degradation evaluation
- Model comparison report schema verification
"""

import os
import sys
import json
import pytest
import numpy as np
import torch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import SignLanguage
from ml.data.dataset import StaticSignDataset, compute_class_weights
from ml.data.augmentations import (
    GaussianLandmarkJitter,
    FeatureScalePerturbation,
    FeatureChannelDropout,
    get_default_train_transform,
)
from ml.models.static_mlp import StaticASL_MLP, StaticISL_MLP
from ml.evaluation.robustness_test import (
    evaluate_noise_robustness,
    evaluate_isl_single_hand_fallback,
    benchmark_against_legacy_rf,
)


class TestDataAugmentations:
    """Verifies that all augmentation transforms preserve shapes, types, and value bounds."""

    def test_gaussian_jitter_preserves_shape(self):
        jitter = GaussianLandmarkJitter(sigma=0.015, p=1.0)
        x = torch.ones(109, dtype=torch.float32)
        out = jitter(x)
        assert out.shape == (109,)
        assert out.dtype == torch.float32
        assert not torch.allclose(out, x)  # Noise was added

    def test_scale_perturbation_preserves_shape(self):
        scaler = FeatureScalePerturbation(scale_range=(0.95, 1.05), p=1.0)
        x = torch.ones(228, dtype=torch.float32)
        out = scaler(x)
        assert out.shape == (228,)
        assert out.dtype == torch.float32

    def test_channel_dropout_preserves_shape(self):
        dropout = FeatureChannelDropout(drop_rate=0.20, p=1.0)
        x = torch.ones(109, dtype=torch.float32)
        out = dropout(x)
        assert out.shape == (109,)
        # Some elements should be zeroed
        assert (out == 0.0).sum() > 0

    def test_composed_default_transform(self):
        transform = get_default_train_transform()
        x = torch.randn(109, dtype=torch.float32)
        out = transform(x)
        assert out.shape == (109,)
        assert not torch.isnan(out).any()


class TestClassImbalanceWeighting:
    """Tests class weight calculation properties."""

    def test_balanced_labels_yield_uniform_weights(self):
        labels = torch.tensor([0, 1, 2, 0, 1, 2])
        w = compute_class_weights(labels, num_classes=3)
        assert len(w) == 3
        assert torch.allclose(w, torch.ones(3), atol=1e-2)

    def test_imbalanced_labels_weighting(self):
        labels = torch.tensor([0, 0, 0, 0, 1, 2])
        w = compute_class_weights(labels, num_classes=3)
        # Class 0 has 4 samples, Class 1 and 2 have 1 sample each
        # Class 0 should receive lower weight than rare classes
        assert w[0] < w[1]
        assert w[0] < w[2]
        assert torch.all(w >= 0.25)
        assert torch.all(w <= 4.0)


class TestRobustnessPipelines:
    """Tests noise perturbation resilience and single-hand fallback."""

    def test_noise_robustness_execution(self):
        model = StaticASL_MLP(input_dim=109, num_classes=5)
        features = np.random.randn(20, 109).astype(np.float32)
        labels = np.random.randint(0, 5, size=(20,)).astype(np.int64)
        ds = StaticSignDataset(features=features, labels=labels)

        res = evaluate_noise_robustness(model, ds, sigmas=[0.0, 0.05])
        assert "sigma_0.00" in res
        assert "sigma_0.05" in res
        assert "accuracy" in res["sigma_0.00"]

    def test_isl_single_hand_fallback_graceful_degradation(self):
        model = StaticISL_MLP(input_dim=228, num_classes=5)
        features = np.random.randn(20, 228).astype(np.float32)
        labels = np.random.randint(0, 5, size=(20,)).astype(np.int64)
        ds = StaticSignDataset(features=features, labels=labels)

        fallback_res = evaluate_isl_single_hand_fallback(model, ds)
        assert "full_dual_hand" in fallback_res
        assert "single_hand_fallback" in fallback_res
        assert "relative_retention" in fallback_res
        assert not np.isnan(fallback_res["relative_retention"])


class TestComparisonReportSchema:
    """Verifies that the generated model comparison report meets all required schema criteria."""

    def test_comparison_report_exists_and_valid(self):
        report_path = os.path.join(REPO_ROOT, "reports", "model_comparison_report.json")
        assert os.path.exists(report_path), "model_comparison_report.json should exist"

        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "asl_noise_robustness" in data
        assert "isl_noise_robustness" in data
        assert "isl_single_hand_fallback" in data
        assert "baseline_comparison" in data
        assert "pytorch_asl_mlp" in data["baseline_comparison"]
        assert "legacy_random_forest" in data["baseline_comparison"]
