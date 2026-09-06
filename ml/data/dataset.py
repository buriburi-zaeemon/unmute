"""
UNMUTE - PyTorch Dataset & DataLoader Abstractions
Supports both ASL (109-dim features) and ISL (228-dim features) static sign recognition.
"""

import os
import sys
from typing import Tuple, Dict, Optional, Callable, List
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import SignLanguage, get_classes


class StaticSignDataset(Dataset):
    """
    PyTorch Dataset wrapping preprocessed landmark feature arrays and labels.
    Compatible with both ASL (109-dim single-hand) and ISL (228-dim dual-hand) representations.
    """

    def __init__(
        self,
        npz_path: Optional[str] = None,
        features: Optional[np.ndarray] = None,
        labels: Optional[np.ndarray] = None,
        classes: Optional[List[str]] = None,
        transform: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
    ):
        """
        Initialize dataset from an .npz file or directly from numpy arrays.
        """
        if npz_path is not None:
            if not os.path.exists(npz_path):
                raise FileNotFoundError(f"Dataset archive not found: {npz_path}")
            data = np.load(npz_path, allow_pickle=True)
            self.features = torch.from_numpy(data["features"].astype(np.float32))
            self.labels = torch.from_numpy(data["labels"].astype(np.int64))
            self.classes = list(data["classes"]) if "classes" in data else []
        elif features is not None and labels is not None:
            self.features = torch.from_numpy(features.astype(np.float32)) if isinstance(features, np.ndarray) else features.float()
            self.labels = torch.from_numpy(labels.astype(np.int64)) if isinstance(labels, np.ndarray) else labels.long()
            self.classes = classes or []
        else:
            raise ValueError("Either npz_path or both (features, labels) must be provided.")

        self.transform = transform

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        x = self.features[idx]
        y = self.labels[idx]

        if self.transform is not None:
            x = self.transform(x)

        return x, y

    @property
    def feature_dim(self) -> int:
        """Returns the dimensionality of feature vectors (e.g. 109 for ASL, 228 for ISL)."""
        return int(self.features.shape[1]) if len(self.features) > 0 else 0

    @property
    def num_classes(self) -> int:
        """Returns total distinct classes recorded or max label + 1."""
        if self.classes:
            return len(self.classes)
        return int(self.labels.max().item() + 1) if len(self.labels) > 0 else 0


def get_dataloaders(
    data_dir: str,
    language: SignLanguage = SignLanguage.ASL,
    batch_size: int = 64,
    num_workers: int = 0,
    pin_memory: bool = False,
    train_transform: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
) -> Dict[str, DataLoader]:
    """
    Constructs PyTorch DataLoaders for train, validation, and test splits
    from the target data directory for the given sign language.
    """
    lang_prefix = language.value.lower()
    train_path = os.path.join(data_dir, f"{lang_prefix}_train.npz")
    val_path = os.path.join(data_dir, f"{lang_prefix}_val.npz")
    test_path = os.path.join(data_dir, f"{lang_prefix}_test.npz")

    for path in [train_path, val_path, test_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing dataset split archive: {path}. "
                f"Please run 'ml/data/prepare_dataset.py --language {language.value} --output-dir {data_dir}' first."
            )

    train_ds = StaticSignDataset(npz_path=train_path, transform=train_transform)
    val_ds = StaticSignDataset(npz_path=val_path)
    test_ds = StaticSignDataset(npz_path=test_path)

    loaders = {
        "train": DataLoader(
            train_ds,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
        "val": DataLoader(
            val_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
        "test": DataLoader(
            test_ds,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
    }

    return loaders
