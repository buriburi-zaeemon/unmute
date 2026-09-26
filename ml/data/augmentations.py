"""
UNMUTE - Data Augmentation Pipeline for Static Sign Features
Provides stochastic coordinate perturbations and channel dropout transforms
specifically designed for 109-dim (ASL) and 228-dim (ISL) normalized feature representations.
Transforms execute on-the-fly during training without leaking into validation/test splits.
"""

from typing import List, Callable, Optional, Tuple
import torch


class GaussianLandmarkJitter:
    """
    Injects zero-mean Gaussian jitter to feature vectors.
    Simulates sensor noise, micro-tremors, and landmark estimation jitter.
    """

    def __init__(self, sigma: float = 0.012, p: float = 0.7):
        self.sigma = sigma
        self.p = p

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if torch.rand(1).item() < self.p:
            noise = torch.randn_like(x) * self.sigma
            return x + noise
        return x


class FeatureScalePerturbation:
    """
    Applies small isotropic scale variations to simulate hand-to-camera distance variance.
    """

    def __init__(self, scale_range: Tuple[float, float] = (0.95, 1.05), p: float = 0.5):
        self.min_scale, self.max_scale = scale_range
        self.p = p

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if torch.rand(1).item() < self.p:
            scale = torch.empty(1).uniform_(self.min_scale, self.max_scale).item()
            return x * scale
        return x


class FeatureChannelDropout:
    """
    Randomly masks individual feature dimensions with zeros with probability drop_rate.
    Simulates intermittent tracking occlusions and noisy sensor dropout.
    """

    def __init__(self, drop_rate: float = 0.04, p: float = 0.4):
        self.drop_rate = drop_rate
        self.p = p

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if torch.rand(1).item() < self.p:
            mask = (torch.rand_like(x) > self.drop_rate).float()
            return x * mask
        return x


class ComposeTransforms:
    """Chains multiple feature transforms sequentially."""

    def __init__(self, transforms: List[Callable[[torch.Tensor], torch.Tensor]]):
        self.transforms = transforms

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        for t in self.transforms:
            x = t(x)
        return x


def get_default_train_transform() -> ComposeTransforms:
    """
    Constructs the recommended data augmentation pipeline for UNMUTE static recognition models.
    """
    return ComposeTransforms([
        GaussianLandmarkJitter(sigma=0.012, p=0.7),
        FeatureScalePerturbation(scale_range=(0.96, 1.04), p=0.5),
        FeatureChannelDropout(drop_rate=0.03, p=0.35),
    ])
