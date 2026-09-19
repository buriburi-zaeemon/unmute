"""
UNMUTE - Machine Learning Evaluation Suite
Provides evaluation engines, metrics computation, and confusion matrix visualizers.
"""

from ml.evaluation.evaluate_static import (
    compute_classification_metrics,
    plot_confusion_matrix,
    evaluate_model_on_dataset,
    evaluate_static_checkpoint,
)

__all__ = [
    "compute_classification_metrics",
    "plot_confusion_matrix",
    "evaluate_model_on_dataset",
    "evaluate_static_checkpoint",
]
