"""
UNMUTE - Static Sign Recognition MLP Architectures
Provides beginner-friendly, student-viva explainable PyTorch Multi-Layer Perceptrons:
- StaticASL_MLP: 109 input features -> 41 output classes (unimanual ASL)
- StaticISL_MLP: 228 input features -> 44 output classes (bimanual ISL)
"""

import os
from typing import Dict, Any, Optional, Tuple, Union
import torch
import torch.nn as nn
import torch.nn.functional as F

from ml.data.labels import SignLanguage, get_num_classes


class StaticASL_MLP(nn.Module):
    """
    Static Multi-Layer Perceptron for American Sign Language (ASL).
    Takes a 109-dimensional invariant geometric feature vector and classifies into 41 static classes.
    """

    def __init__(
        self,
        input_dim: int = 109,
        hidden_dim1: int = 256,
        hidden_dim2: int = 128,
        num_classes: int = 41,
        dropout_rate: float = 0.3,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.BatchNorm1d(hidden_dim1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.BatchNorm1d(hidden_dim2),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.67),
            nn.Linear(hidden_dim2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Computes raw unnormalized classification logits."""
        # Handle single unbatched sample (1D -> 2D)
        if x.dim() == 1:
            was_training = self.training
            self.eval()
            logits = self.network(x.unsqueeze(0)).squeeze(0)
            if was_training:
                self.train()
            return logits
        return self.network(x)

    @torch.no_grad()
    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Computes normalized softmax class probabilities."""
        self.eval()
        logits = self.forward(x)
        return F.softmax(logits, dim=-1)

    @torch.no_grad()
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Computes the index of the highest probability class."""
        probs = self.predict_proba(x)
        return torch.argmax(probs, dim=-1)

    def save_checkpoint(self, checkpoint_path: str, metadata: Optional[Dict[str, Any]] = None):
        """Saves model state dictionary along with configuration metadata."""
        os.makedirs(os.path.dirname(os.path.abspath(checkpoint_path)), exist_ok=True)
        checkpoint = {
            "model_type": "StaticASL_MLP",
            "language": "ASL",
            "input_dim": self.input_dim,
            "num_classes": self.num_classes,
            "state_dict": self.state_dict(),
            "metadata": metadata or {},
        }
        torch.save(checkpoint, checkpoint_path)

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str, map_location: Optional[Union[str, torch.device]] = None) -> "StaticASL_MLP":
        """Loads and instantiates model from saved checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=map_location or "cpu")
        model = cls(
            input_dim=checkpoint.get("input_dim", 109),
            num_classes=checkpoint.get("num_classes", 41),
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        return model


class StaticISL_MLP(nn.Module):
    """
    Static Multi-Layer Perceptron for Indian Sign Language (ISL).
    Takes a 228-dimensional dual-hand invariant feature vector and classifies into 44 static classes.
    """

    def __init__(
        self,
        input_dim: int = 228,
        hidden_dim1: int = 512,
        hidden_dim2: int = 256,
        num_classes: int = 44,
        dropout_rate: float = 0.3,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.BatchNorm1d(hidden_dim1),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.BatchNorm1d(hidden_dim2),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate * 0.67),
            nn.Linear(hidden_dim2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Computes raw unnormalized classification logits."""
        if x.dim() == 1:
            was_training = self.training
            self.eval()
            logits = self.network(x.unsqueeze(0)).squeeze(0)
            if was_training:
                self.train()
            return logits
        return self.network(x)

    @torch.no_grad()
    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Computes normalized softmax class probabilities."""
        self.eval()
        logits = self.forward(x)
        return F.softmax(logits, dim=-1)

    @torch.no_grad()
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """Computes the index of the highest probability class."""
        probs = self.predict_proba(x)
        return torch.argmax(probs, dim=-1)

    def save_checkpoint(self, checkpoint_path: str, metadata: Optional[Dict[str, Any]] = None):
        """Saves model state dictionary along with configuration metadata."""
        os.makedirs(os.path.dirname(os.path.abspath(checkpoint_path)), exist_ok=True)
        checkpoint = {
            "model_type": "StaticISL_MLP",
            "language": "ISL",
            "input_dim": self.input_dim,
            "num_classes": self.num_classes,
            "state_dict": self.state_dict(),
            "metadata": metadata or {},
        }
        torch.save(checkpoint, checkpoint_path)

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str, map_location: Optional[Union[str, torch.device]] = None) -> "StaticISL_MLP":
        """Loads and instantiates model from saved checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=map_location or "cpu")
        model = cls(
            input_dim=checkpoint.get("input_dim", 228),
            num_classes=checkpoint.get("num_classes", 44),
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        return model


def create_static_model(language: SignLanguage = SignLanguage.ASL) -> nn.Module:
    """Factory helper to instantiate the appropriate static recognition model for the target language."""
    if language == SignLanguage.ASL:
        return StaticASL_MLP()
    elif language == SignLanguage.ISL:
        return StaticISL_MLP()
    else:
        raise ValueError(f"Unsupported language: {language}")
