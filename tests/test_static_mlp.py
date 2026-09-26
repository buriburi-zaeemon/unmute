"""
Automated unit tests for UNMUTE Static MLP models and training pipelines:
- StaticASL_MLP (109 dims -> 41 classes)
- StaticISL_MLP (228 dims -> 44 classes)
- Forward pass logits & softmax probabilities
- Checkpoint serialization and deserialization
- Optimization gradient updates
"""

import os
import sys
import pytest
import torch
import torch.nn as nn
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import SignLanguage, get_num_classes
from ml.models.static_mlp import StaticASL_MLP, StaticISL_MLP, create_static_model
from ml.training.train_static import train_one_epoch, evaluate_epoch


class TestStaticArchitectures:
    """Tests MLP layer definitions, output shapes, and forward behaviors."""

    def test_asl_mlp_dimensions_and_forward(self):
        model = StaticASL_MLP(input_dim=109, num_classes=41)
        assert model.input_dim == 109
        assert model.num_classes == 41

        # Batched input
        batch_x = torch.randn(8, 109)
        logits = model(batch_x)
        assert logits.shape == (8, 41)

        # Unbatched 1D input
        single_x = torch.randn(109)
        single_logits = model(single_x)
        assert single_logits.shape == (41,)

    def test_isl_mlp_dimensions_and_forward(self):
        model = StaticISL_MLP(input_dim=228, num_classes=44)
        assert model.input_dim == 228
        assert model.num_classes == 44

        batch_x = torch.randn(8, 228)
        logits = model(batch_x)
        assert logits.shape == (8, 44)

    def test_factory_function(self):
        asl_model = create_static_model(SignLanguage.ASL)
        assert isinstance(asl_model, StaticASL_MLP)
        assert asl_model.input_dim == 109

        isl_model = create_static_model(SignLanguage.ISL)
        assert isinstance(isl_model, StaticISL_MLP)
        assert isl_model.input_dim == 228

    def test_predict_proba_and_predict(self):
        model = StaticASL_MLP()
        batch_x = torch.randn(4, 109)

        probs = model.predict_proba(batch_x)
        assert probs.shape == (4, 41)
        # Sum of probabilities across classes should be close to 1.0
        sums = probs.sum(dim=-1)
        assert torch.allclose(sums, torch.ones(4), atol=1e-5)
        # Probability values between 0.0 and 1.0
        assert (probs >= 0.0).all() and (probs <= 1.0).all()

        preds = model.predict(batch_x)
        assert preds.shape == (4,)
        assert preds.dtype == torch.int64
        assert (preds >= 0).all() and (preds < 41).all()


class TestCheckpointing:
    """Tests saving and loading model checkpoints."""

    def test_asl_checkpoint_roundtrip(self, tmp_path):
        model = StaticASL_MLP()
        ckpt_path = str(tmp_path / "test_asl_mlp.pt")

        metadata = {"version": "1.0", "author": "Contributor 1"}
        model.save_checkpoint(ckpt_path, metadata=metadata)
        assert os.path.exists(ckpt_path)

        loaded_model = StaticASL_MLP.load_checkpoint(ckpt_path)
        assert loaded_model.input_dim == 109
        assert loaded_model.num_classes == 41

        # Check weights identical
        model.eval()
        test_x = torch.randn(2, 109)
        with torch.no_grad():
            orig_out = model(test_x)
            loaded_out = loaded_model(test_x)
        assert torch.allclose(orig_out, loaded_out, atol=1e-5)

    def test_isl_checkpoint_roundtrip(self, tmp_path):
        model = StaticISL_MLP()
        ckpt_path = str(tmp_path / "test_isl_mlp.pt")

        model.save_checkpoint(ckpt_path)
        loaded_model = StaticISL_MLP.load_checkpoint(ckpt_path)
        assert loaded_model.input_dim == 228
        assert loaded_model.num_classes == 44

        model.eval()
        test_x = torch.randn(2, 228)
        with torch.no_grad():
            orig_out = model(test_x)
            loaded_out = loaded_model(test_x)
        assert torch.allclose(orig_out, loaded_out, atol=1e-5)


class TestTrainingStep:
    """Tests backpropagation and optimization step."""

    def test_backward_gradient_flow(self):
        model = StaticASL_MLP()
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

        x = torch.randn(16, 109)
        y = torch.randint(0, 41, (16,))

        optimizer.zero_grad()
        out = model(x)
        loss = criterion(out, y)
        loss.backward()

        # Ensure parameters received gradients
        for param in model.parameters():
            if param.requires_grad:
                assert param.grad is not None
                assert not torch.isnan(param.grad).any()

        optimizer.step()
