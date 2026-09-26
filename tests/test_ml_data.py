"""
Automated unit tests for UNMUTE ML Data Pipeline:
- Label mappings (ASL 41 classes, ISL 44 classes)
- Feature extraction & dimensionality (109 dims ASL, 228 dims ISL)
- Zero-leakage stratified data partitioning
- PyTorch Dataset & DataLoader pipeline
"""

import os
import sys
import pytest
import numpy as np
import torch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import (
    SignLanguage,
    SignType,
    get_classes,
    get_num_classes,
    label_to_id,
    id_to_label,
    get_sign_type,
    is_dynamic_token,
    is_bimanual_sign,
    ASL_CLASSES,
    ISL_CLASSES,
)
from sign_engine.feature_engineering import FeatureEngineer, DualHandFeatures
from ml.data.prepare_dataset import (
    partition_zero_leakage_splits,
    extract_sample_features,
    generate_benchmark_dataset,
)
from ml.data.dataset import StaticSignDataset, get_dataloaders


class TestLabelMappings:
    """Tests label dictionary consistency, bidirectional mappings, and token categorization."""

    def test_asl_class_count_and_continuity(self):
        classes = get_classes(SignLanguage.ASL)
        assert len(classes) == 41
        assert get_num_classes(SignLanguage.ASL) == 41

        # Verify continuous IDs from 0 to 40
        for idx, label in enumerate(classes):
            assert label_to_id(label, SignLanguage.ASL) == idx
            assert id_to_label(idx, SignLanguage.ASL) == label

    def test_isl_class_count_and_continuity(self):
        classes = get_classes(SignLanguage.ISL)
        assert len(classes) == 44
        assert get_num_classes(SignLanguage.ISL) == 44

        # Verify continuous IDs from 0 to 43
        for idx, label in enumerate(classes):
            assert label_to_id(label, SignLanguage.ISL) == idx
            assert id_to_label(idx, SignLanguage.ISL) == label

    def test_sign_type_categorization(self):
        # Letters
        assert get_sign_type("A", SignLanguage.ASL) == SignType.LETTER
        assert get_sign_type("Z", SignLanguage.ISL) == SignType.LETTER

        # Numerals
        assert get_sign_type("0", SignLanguage.ASL) == SignType.NUMBER
        assert get_sign_type("9", SignLanguage.ISL) == SignType.NUMBER

        # Static Phrases
        assert get_sign_type("STOP", SignLanguage.ASL) == SignType.STATIC_PHRASE
        assert get_sign_type("NAMASTE", SignLanguage.ISL) == SignType.STATIC_PHRASE

        # Dynamic Signs
        assert get_sign_type("HELLO", SignLanguage.ASL) == SignType.DYNAMIC
        assert get_sign_type("WATER", SignLanguage.ISL) == SignType.DYNAMIC

        # Control Signs
        assert get_sign_type("SPACE", SignLanguage.ASL) == SignType.CONTROL

    def test_dynamic_token_reservations(self):
        # J and Z are dynamic in ASL
        assert is_dynamic_token("J", SignLanguage.ASL) is True
        assert is_dynamic_token("Z", SignLanguage.ASL) is True
        assert is_dynamic_token("A", SignLanguage.ASL) is False

        # In ISL, all 26 letters are standard bimanual static configurations
        assert is_dynamic_token("J", SignLanguage.ISL) is False
        assert is_dynamic_token("Z", SignLanguage.ISL) is False

    def test_bimanual_signs(self):
        # ASL static signs are unimanual
        assert is_bimanual_sign("A", SignLanguage.ASL) is False

        # ISL letters and phrases are bimanual (except single-handed numerals)
        assert is_bimanual_sign("A", SignLanguage.ISL) is True
        assert is_bimanual_sign("NAMASTE", SignLanguage.ISL) is True
        assert is_bimanual_sign("5", SignLanguage.ISL) is False


class TestFeatureDimensions:
    """Tests 109-dim unimanual and 228-dim bimanual feature extraction."""

    @pytest.fixture
    def fe(self):
        return FeatureEngineer()

    def test_single_hand_109_dims(self, fe):
        landmarks = [(0.0, 0.0, 0.0)] * 21
        landmarks[9] = (0.0, 1.0, 0.0)  # non-zero palm scale
        features = fe.extract_features(landmarks)

        assert features.feature_vector.shape == (109,)
        assert features.feature_vector.dtype == np.float32

    def test_dual_hand_228_dims(self, fe):
        primary = [(0.0, 0.0, 0.0)] * 21
        primary[9] = (0.0, 1.0, 0.0)
        secondary = [(0.5, 0.0, 0.0)] * 21
        secondary[9] = (0.5, 1.0, 0.0)

        dual_features = fe.extract_dual_features(primary, secondary)
        assert isinstance(dual_features, DualHandFeatures)
        assert dual_features.feature_vector.shape == (228,)
        assert dual_features.feature_vector.dtype == np.float32
        assert dual_features.is_bimanual is True

    def test_dual_hand_fallback_single_hand(self, fe):
        primary = [(0.0, 0.0, 0.0)] * 21
        primary[9] = (0.0, 1.0, 0.0)

        dual_features = fe.extract_dual_features(primary, secondary_landmarks=None)
        assert dual_features.feature_vector.shape == (228,)
        assert dual_features.is_bimanual is False
        # Secondary 109 features should be zero
        assert np.allclose(dual_features.feature_vector[109:218], 0.0)
        # Spatial contact feature (index 218) should be 0.0 (no contact)
        assert dual_features.feature_vector[218] == 0.0


class TestDataSplitting:
    """Tests stratified zero-leakage 70/15/15 dataset partitioning."""

    def test_zero_leakage_split_ratios_and_stratification(self):
        X = np.random.randn(200, 109).astype(np.float32)
        y = np.array([i % 10 for i in range(200)], dtype=np.int64)

        splits = partition_zero_leakage_splits(
            X, y, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42
        )

        assert len(splits["train"][0]) == 140
        assert len(splits["val"][0]) == 30
        assert len(splits["test"][0]) == 30

        # Verify class balance across all splits (every class from 0 to 9 represented)
        for split_name, (_, y_split) in splits.items():
            unique_classes = set(y_split)
            assert len(unique_classes) == 10


class TestPyTorchDatasetAndLoader:
    """Tests StaticSignDataset and get_dataloaders integration."""

    def test_dataset_item_and_tensor_types(self):
        X = np.random.randn(50, 109).astype(np.float32)
        y = np.random.randint(0, 41, size=50).astype(np.int64)
        classes = ASL_CLASSES

        dataset = StaticSignDataset(features=X, labels=y, classes=classes)
        assert len(dataset) == 50
        assert dataset.feature_dim == 109
        assert dataset.num_classes == 41

        feat_tensor, label_tensor = dataset[0]
        assert isinstance(feat_tensor, torch.Tensor)
        assert isinstance(label_tensor, torch.Tensor)
        assert feat_tensor.shape == (109,)
        assert feat_tensor.dtype == torch.float32
        assert label_tensor.dtype == torch.int64

    def test_dataloaders_e2e(self, tmp_path):
        from ml.data.prepare_dataset import prepare_dataset_pipeline

        out_dir = str(tmp_path / "asl_data")
        prepare_dataset_pipeline(
            language=SignLanguage.ASL,
            output_dir=out_dir,
            samples_per_class=10,
            random_state=42,
        )

        loaders = get_dataloaders(
            data_dir=out_dir,
            language=SignLanguage.ASL,
            batch_size=32,
            num_workers=0,
        )

        assert "train" in loaders
        assert "val" in loaders
        assert "test" in loaders

        batch_x, batch_y = next(iter(loaders["train"]))
        assert batch_x.shape[1] == 109
        assert batch_y.dtype == torch.int64
        assert len(batch_x) <= 32
