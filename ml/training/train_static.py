"""
UNMUTE - Modular Static MLP Training Pipeline
Trains StaticASL_MLP and StaticISL_MLP models using PyTorch, CrossEntropyLoss, AdamW,
and learning rate scheduling with best validation checkpointing.
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, Optional, Tuple
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ml.data.labels import SignLanguage, get_num_classes, get_classes
from ml.data.dataset import get_dataloaders
from ml.models.static_mlp import StaticASL_MLP, StaticISL_MLP, create_static_model


def train_one_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: torch.device,
) -> Tuple[float, float]:
    """Runs a single training epoch and returns (average_loss, accuracy)."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for batch_x, batch_y in dataloader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        optimizer.zero_grad()
        logits = model(batch_x)
        loss = criterion(logits, batch_y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * batch_x.size(0)
        preds = torch.argmax(logits, dim=-1)
        correct += (preds == batch_y).sum().item()
        total += batch_x.size(0)

    avg_loss = total_loss / (total if total > 0 else 1)
    acc = correct / (total if total > 0 else 1)
    return avg_loss, acc


@torch.no_grad()
def evaluate_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, float]:
    """Evaluates model on validation or test split and returns (average_loss, accuracy)."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    for batch_x, batch_y in dataloader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        logits = model(batch_x)
        loss = criterion(logits, batch_y)

        total_loss += loss.item() * batch_x.size(0)
        preds = torch.argmax(logits, dim=-1)
        correct += (preds == batch_y).sum().item()
        total += batch_x.size(0)

    avg_loss = total_loss / (total if total > 0 else 1)
    acc = correct / (total if total > 0 else 1)
    return avg_loss, acc


def train_static_model(
    language: SignLanguage = SignLanguage.ASL,
    data_dir: str = "data",
    checkpoint_dir: str = "models",
    epochs: int = 25,
    batch_size: int = 32,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    device: Optional[torch.device] = None,
) -> Dict[str, Any]:
    """
    Complete end-to-end training procedure for static sign recognition.
    Saves the best model checkpoint based on validation loss.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    lang_prefix = language.value.lower()
    os.makedirs(checkpoint_dir, exist_ok=True)
    checkpoint_file = os.path.join(checkpoint_dir, f"{lang_prefix}_static_mlp.pt")
    history_file = os.path.join(checkpoint_dir, f"{lang_prefix}_training_history.json")

    print("\n" + "=" * 60)
    print(f"UNMUTE — Static MLP Training: {language.value}")
    print("=" * 60)
    print(f"Device:           {device}")
    print(f"Data Directory:   {data_dir}")
    print(f"Epochs:           {epochs}")
    print(f"Batch Size:       {batch_size}")
    print(f"Learning Rate:    {lr}")
    print(f"Checkpoint Path:  {checkpoint_file}")

    # Load zero-leakage DataLoaders
    loaders = get_dataloaders(data_dir=data_dir, language=language, batch_size=batch_size)
    num_classes = get_num_classes(language)
    classes = get_classes(language)

    # Initialize model
    model = create_static_model(language).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=3)

    history = {
        "language": language.value,
        "epochs": epochs,
        "batch_size": batch_size,
        "train_loss": [],
        "train_acc": [],
        "val_loss": [],
        "val_acc": [],
        "best_epoch": 0,
        "best_val_loss": float("inf"),
        "best_val_acc": 0.0,
    }

    start_time = time.time()
    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        t_loss, t_acc = train_one_epoch(model, loaders["train"], criterion, optimizer, device)
        v_loss, v_acc = evaluate_epoch(model, loaders["val"], criterion, device)
        scheduler.step(v_loss)

        history["train_loss"].append(round(t_loss, 4))
        history["train_acc"].append(round(t_acc, 4))
        history["val_loss"].append(round(v_loss, 4))
        history["val_acc"].append(round(v_acc, 4))

        is_best = v_loss < best_val_loss
        if is_best:
            best_val_loss = v_loss
            history["best_epoch"] = epoch
            history["best_val_loss"] = round(v_loss, 4)
            history["best_val_acc"] = round(v_acc, 4)

            # Save checkpoint
            metadata = {
                "epoch": epoch,
                "val_loss": v_loss,
                "val_acc": v_acc,
                "classes": classes,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            model.save_checkpoint(checkpoint_file, metadata=metadata)

        print(
            f"Epoch [{epoch:02d}/{epochs:02d}] "
            f"Train Loss: {t_loss:.4f} Acc: {t_acc*100:5.1f}% | "
            f"Val Loss: {v_loss:.4f} Acc: {v_acc*100:5.1f}% "
            f"{'* (Best)' if is_best else ''}"
        )

    total_time = time.time() - start_time
    history["training_time_seconds"] = round(total_time, 2)

    # Final evaluation on held-out Test split
    test_loss, test_acc = evaluate_epoch(model, loaders["test"], criterion, device)
    history["test_loss"] = round(test_loss, 4)
    history["test_acc"] = round(test_acc, 4)

    print("-" * 60)
    print(f"Training Complete in {total_time:.1f}s")
    print(f"Best Validation Loss: {history['best_val_loss']:.4f} (Acc: {history['best_val_acc']*100:.1f}%)")
    print(f"Held-Out Test Loss:   {history['test_loss']:.4f} (Acc: {history['test_acc']*100:.1f}%)")
    print("=" * 60 + "\n")

    # Export training history JSON
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    return history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UNMUTE Static MLP Training")
    parser.add_argument("--language", choices=["ASL", "ISL"], default="ASL", help="Target sign language")
    parser.add_argument("--data-dir", default="data", help="Directory containing dataset .npz archives")
    parser.add_argument("--checkpoint-dir", default="models", help="Directory to save model checkpoints")
    parser.add_argument("--epochs", type=int, default=20, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=1e-3, help="Initial learning rate")
    args = parser.parse_args()

    lang = SignLanguage.ASL if args.language == "ASL" else SignLanguage.ISL
    train_static_model(
        language=lang,
        data_dir=args.data_dir,
        checkpoint_dir=args.checkpoint_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )
