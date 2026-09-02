"""
Landmark Extractor module using Google MediaPipe HandLandmarker.
Extracts 21 3D hand landmarks per hand, handedness, and bounding boxes.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

# Landmark indices reference:
# 0: WRIST
# 1-4: THUMB (CMC, MCP, IP, TIP)
# 5-8: INDEX (MCP, PIP, DIP, TIP)
# 9-12: MIDDLE (MCP, PIP, DIP, TIP)
# 13-16: RING (MCP, PIP, DIP, TIP)
# 17-20: PINKY (MCP, PIP, DIP, TIP)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm base
]


@dataclass
class SingleHandData:
    landmarks: List[Tuple[float, float, float]]  # Normalized (x, y, z) [0..1]
    world_landmarks: List[Tuple[float, float, float]]  # Metric (x, y, z) in meters
    handedness: str  # 'Left' or 'Right'
    confidence: float
    bbox: Tuple[float, float, float, float]  # (min_x, min_y, max_x, max_y) normalized
    bbox_pixels: Tuple[int, int, int, int]  # (min_x, min_y, max_x, max_y) in image pixels


@dataclass
class HandResult:
    hands: List[SingleHandData] = field(default_factory=list)
    has_hands: bool = False
    image_shape: Tuple[int, int, int] = (0, 0, 0)  # (height, width, channels)


class LandmarkExtractor:
    """Wrapper around MediaPipe HandLandmarker for unified single-frame and batch processing."""

    def __init__(self, model_path: Optional[str] = None, max_num_hands: int = 1, min_detection_confidence: float = 0.4):
        if model_path is None:
            # Default model path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            default_path = os.path.join(os.path.dirname(current_dir), "models", "hand_landmarker.task")
            if not os.path.exists(default_path):
                # Attempt to download if missing
                os.makedirs(os.path.dirname(default_path), exist_ok=True)
                import urllib.request
                url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
                urllib.request.urlretrieve(url, default_path)
            model_path = default_path

        self.model_path = model_path
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence

        base_opts = BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_opts,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=self.max_num_hands,
            min_hand_detection_confidence=self.min_detection_confidence,
            min_hand_presence_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_detection_confidence,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def extract(self, image: np.ndarray) -> HandResult:
        """
        Extract hand landmarks from an RGB or BGR numpy image array.
        Args:
            image: numpy.ndarray in BGR (OpenCV standard) or RGB.
        Returns:
            HandResult with extracted hand landmarks and metadata.
        """
        if image is None or image.size == 0:
            return HandResult()

        h, w = image.shape[:2]

        # Convert to RGB if needed
        if len(image.shape) == 2:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        else:
            # Assume BGR if 3 channels
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        detection_result = self.landmarker.detect(mp_image)

        hands_data: List[SingleHandData] = []

        if detection_result.hand_landmarks:
            for idx, raw_landmarks in enumerate(detection_result.hand_landmarks):
                # Normalized coordinates (21 landmarks)
                landmarks = [(lm.x, lm.y, lm.z) for lm in raw_landmarks]

                # World coordinates if available
                if detection_result.hand_world_landmarks and len(detection_result.hand_world_landmarks) > idx:
                    raw_world = detection_result.hand_world_landmarks[idx]
                    world_landmarks = [(lm.x, lm.y, lm.z) for lm in raw_world]
                else:
                    world_landmarks = landmarks

                # Handedness category
                handedness = "Right"
                confidence = 0.9
                if detection_result.handedness and len(detection_result.handedness) > idx:
                    categories = detection_result.handedness[idx]
                    if categories:
                        # Note: MediaPipe mirrors handedness for self-facing cameras
                        handedness = categories[0].category_name
                        confidence = float(categories[0].score)

                # Bounding box
                xs = [lm[0] for lm in landmarks]
                ys = [lm[1] for lm in landmarks]
                min_x = max(0.0, min(xs))
                max_x = min(1.0, max(xs))
                min_y = max(0.0, min(ys))
                max_y = min(1.0, max(ys))

                # Add padding
                pad_x = (max_x - min_x) * 0.1
                pad_y = (max_y - min_y) * 0.1
                bbox = (
                    max(0.0, min_x - pad_x),
                    max(0.0, min_y - pad_y),
                    min(1.0, max_x + pad_x),
                    min(1.0, max_y + pad_y),
                )
                bbox_pixels = (
                    int(bbox[0] * w),
                    int(bbox[1] * h),
                    int(bbox[2] * w),
                    int(bbox[3] * h),
                )

                hands_data.append(
                    SingleHandData(
                        landmarks=landmarks,
                        world_landmarks=world_landmarks,
                        handedness=handedness,
                        confidence=confidence,
                        bbox=bbox,
                        bbox_pixels=bbox_pixels,
                    )
                )

        return HandResult(
            hands=hands_data,
            has_hands=len(hands_data) > 0,
            image_shape=(h, w, 3 if len(image.shape) >= 3 else 1),
        )

    def draw_landmarks_on_image(self, rgb_image: np.ndarray, hand_result: HandResult) -> np.ndarray:
        """Render glowing skeleton HUD and landmarks onto an image."""
        annotated = rgb_image.copy()
        h, w = annotated.shape[:2]

        for hand in hand_result.hands:
            # Draw Connections
            for start_idx, end_idx in HAND_CONNECTIONS:
                p1 = (int(hand.landmarks[start_idx][0] * w), int(hand.landmarks[start_idx][1] * h))
                p2 = (int(hand.landmarks[end_idx][0] * w), int(hand.landmarks[end_idx][1] * h))
                cv2.line(annotated, p1, p2, (0, 240, 255), 2, cv2.LINE_AA)

            # Draw Landmark Points
            for idx, lm in enumerate(hand.landmarks):
                px = int(lm[0] * w)
                py = int(lm[1] * h)
                # Fingertips (4, 8, 12, 16, 20) in magenta/cyan, joints in white/teal
                if idx in (4, 8, 12, 16, 20):
                    cv2.circle(annotated, (px, py), 6, (255, 0, 200), -1, cv2.LINE_AA)
                    cv2.circle(annotated, (px, py), 8, (255, 255, 255), 1, cv2.LINE_AA)
                else:
                    cv2.circle(annotated, (px, py), 4, (0, 255, 128), -1, cv2.LINE_AA)

            # Draw Bounding Box
            bx1, by1, bx2, by2 = hand.bbox_pixels
            cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 240, 255), 1)
            label = f"{hand.handedness} Hand ({hand.confidence:.2f})"
            cv2.putText(annotated, label, (bx1, max(20, by1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 240, 255), 1, cv2.LINE_AA)

        return annotated
