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


class ResidualBlock(nn.Module):
    """
    Residual dense block with batch normalization, ReLU activation, and dropout.
    Preserves gradient flow and stabilizes representation learning.
    """

    def __init__(self, dim: int, dropout_rate: float = 0.2):
        super().__init__()
        self.fc = nn.Linear(dim, dim)
        self.bn = nn.BatchNorm1d(dim)
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = x
        out = self.fc(x)
        out = self.bn(out)
        out = self.relu(out)
        out = self.dropout(out)
        return out + residual


class StaticASL_MLP(nn.Module):
    """
    Static Multi-Layer Perceptron for American Sign Language (ASL).
    Takes a 109-dimensional invariant geometric feature vector and classifies into 41 static classes.
    Supports optional residual skip block for deeper representation learning.
    """

    def __init__(
        self,
        input_dim: int = 109,
        hidden_dim1: int = 256,
        hidden_dim2: int = 128,
        num_classes: int = 41,
        dropout_rate: float = 0.3,
        use_residual: bool = False,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.use_residual = use_residual

        if use_residual:
            self.input_layer = nn.Sequential(
                nn.Linear(input_dim, hidden_dim1),
                nn.BatchNorm1d(hidden_dim1),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
            )
            self.res_block = ResidualBlock(hidden_dim1, dropout_rate=dropout_rate * 0.67)
            self.output_layer = nn.Sequential(
                nn.Linear(hidden_dim1, hidden_dim2),
                nn.BatchNorm1d(hidden_dim2),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate * 0.67),
                nn.Linear(hidden_dim2, num_classes),
            )
        else:
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
            logits = self.forward(x.unsqueeze(0)).squeeze(0)
            if was_training:
                self.train()
            return logits

        if self.use_residual:
            h = self.input_layer(x)
            h = self.res_block(h)
            return self.output_layer(h)
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
            "use_residual": self.use_residual,
            "state_dict": self.state_dict(),
            "metadata": metadata or {},
        }
        torch.save(checkpoint, checkpoint_path)

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str, map_location: Optional[Union[str, torch.device]] = None) -> "StaticASL_MLP":
        """Loads and instantiates model from saved checkpoint with full backward compatibility."""
        checkpoint = torch.load(checkpoint_path, map_location=map_location or "cpu")
        model = cls(
            input_dim=checkpoint.get("input_dim", 109),
            num_classes=checkpoint.get("num_classes", 41),
            use_residual=checkpoint.get("use_residual", False),
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        return model


class StaticISL_MLP(nn.Module):
    """
    Static Multi-Layer Perceptron for Indian Sign Language (ISL).
    Takes a 228-dimensional dual-hand invariant feature vector and classifies into 44 static classes.
    Supports optional residual skip block for deeper representation learning.
    """

    def __init__(
        self,
        input_dim: int = 228,
        hidden_dim1: int = 512,
        hidden_dim2: int = 256,
        num_classes: int = 44,
        dropout_rate: float = 0.3,
        use_residual: bool = False,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.use_residual = use_residual

        if use_residual:
            self.input_layer = nn.Sequential(
                nn.Linear(input_dim, hidden_dim1),
                nn.BatchNorm1d(hidden_dim1),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate),
            )
            self.res_block = ResidualBlock(hidden_dim1, dropout_rate=dropout_rate * 0.67)
            self.output_layer = nn.Sequential(
                nn.Linear(hidden_dim1, hidden_dim2),
                nn.BatchNorm1d(hidden_dim2),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout_rate * 0.67),
                nn.Linear(hidden_dim2, num_classes),
            )
        else:
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
            logits = self.forward(x.unsqueeze(0)).squeeze(0)
            if was_training:
                self.train()
            return logits

        if self.use_residual:
            h = self.input_layer(x)
            h = self.res_block(h)
            return self.output_layer(h)
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
            "use_residual": self.use_residual,
            "state_dict": self.state_dict(),
            "metadata": metadata or {},
        }
        torch.save(checkpoint, checkpoint_path)

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str, map_location: Optional[Union[str, torch.device]] = None) -> "StaticISL_MLP":
        """Loads and instantiates model from saved checkpoint with full backward compatibility."""
        checkpoint = torch.load(checkpoint_path, map_location=map_location or "cpu")
        model = cls(
            input_dim=checkpoint.get("input_dim", 228),
            num_classes=checkpoint.get("num_classes", 44),
            use_residual=checkpoint.get("use_residual", False),
        )
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()
        return model


def create_static_model(
    language: SignLanguage = SignLanguage.ASL,
    use_residual: bool = False,
) -> nn.Module:
    """Factory helper to instantiate the appropriate static recognition model for the target language."""
    if language == SignLanguage.ASL:
        return StaticASL_MLP(use_residual=use_residual)
    elif language == SignLanguage.ISL:
        return StaticISL_MLP(use_residual=use_residual)
    else:
        raise ValueError(f"Unsupported language: {language}")

