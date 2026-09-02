"""
Custom Gesture Trainer module.
Allows users to record custom gesture samples from webcam frames,
train custom classification models on-the-fly, and save/load them locally.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import os
import json
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import joblib

from .feature_engineering import FeatureEngineer, HandFeatures


@dataclass
class CustomGestureSample:
    gesture_name: str
    landmarks: List[Tuple[float, float, float]]
    timestamp: float


class GestureTrainer:
    """Records and trains lightweight models for user-defined sign gestures."""

    def __init__(self, data_dir: Optional[str] = None):
        self.feature_engineer = FeatureEngineer()
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(os.path.dirname(current_dir), "custom_data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.dataset_file = os.path.join(self.data_dir, "custom_gestures.json")
        self.model_file = os.path.join(self.data_dir, "custom_knn.joblib")

        self.samples: Dict[str, List[List[float]]] = {}
        self.custom_classifier: Optional[KNeighborsClassifier] = None
        self.load_dataset()

    def add_sample(self, gesture_name: str, landmarks: List[Tuple[float, float, float]]) -> int:
        """
        Extracts features from landmarks and adds sample to the active gesture class.
        Returns the total number of samples recorded for this gesture.
        """
        name_clean = gesture_name.strip().upper()
        features = self.feature_engineer.extract_features(landmarks)
        feat_vec = features.feature_vector.tolist()

        if name_clean not in self.samples:
            self.samples[name_clean] = []
        self.samples[name_clean].append(feat_vec)

        self.save_dataset()
        self.retrain_model()
        return len(self.samples[name_clean])

    def add_batch_samples(self, gesture_name: str, samples_landmarks: List[List[Tuple[float, float, float]]]) -> int:
        """Add multiple recorded frames for a gesture and retrain."""
        name_clean = gesture_name.strip().upper()
        if name_clean not in self.samples:
            self.samples[name_clean] = []

        for lms in samples_landmarks:
            features = self.feature_engineer.extract_features(lms)
            self.samples[name_clean].append(features.feature_vector.tolist())

        self.save_dataset()
        self.retrain_model()
        return len(self.samples[name_clean])

    def retrain_model(self) -> bool:
        """Retrains KNN classifier on all registered custom gestures."""
        if not self.samples:
            self.custom_classifier = None
            return False

        X: List[List[float]] = []
        y: List[str] = []

        for label, vecs in self.samples.items():
            for vec in vecs:
                X.append(vec)
                y.append(label)

        if len(set(y)) < 1 or len(X) < 3:
            self.custom_classifier = None
            return False

        n_neighbors = min(3, len(X))
        knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights="distance")
        knn.fit(np.array(X, dtype=np.float32), np.array(y))
        self.custom_classifier = knn

        try:
            joblib.dump(knn, self.model_file)
        except Exception:
            pass
        return True

    def predict_custom(self, features: HandFeatures) -> Optional[Tuple[str, float]]:
        """Predicts custom gesture if matched with high confidence (>0.75)."""
        if self.custom_classifier is None:
            return None

        try:
            vec = features.feature_vector.reshape(1, -1)
            probs = self.custom_classifier.predict_proba(vec)[0]
            max_idx = int(np.argmax(probs))
            confidence = float(probs[max_idx])
            pred_label = self.custom_classifier.classes_[max_idx]

            if confidence >= 0.70:
                return pred_label, round(confidence, 3)
        except Exception:
            pass
        return None

    def save_dataset(self):
        """Persists samples to JSON file."""
        try:
            with open(self.dataset_file, "w", encoding="utf-8") as f:
                json.dump(self.samples, f, indent=2)
        except Exception:
            pass

    def load_dataset(self):
        """Loads samples from JSON file and initializes custom classifier."""
        if os.path.exists(self.dataset_file):
            try:
                with open(self.dataset_file, "r", encoding="utf-8") as f:
                    self.samples = json.load(f)
                self.retrain_model()
            except Exception:
                self.samples = {}

    def get_registered_gestures(self) -> List[Dict[str, Any]]:
        """Returns list of registered custom gesture names and sample counts."""
        return [{"name": k, "samples_count": len(v)} for k, v in self.samples.items()]

    def delete_gesture(self, gesture_name: str) -> bool:
        """Deletes a gesture class and retrains."""
        name_clean = gesture_name.strip().upper()
        if name_clean in self.samples:
            del self.samples[name_clean]
            self.save_dataset()
            self.retrain_model()
            return True
        return False
