"""
Automated unit tests for Sign Recognition Engine.
Tests LandmarkExtractor, FeatureEngineer, ASLClassifier, TemporalGestureTracker, GestureTrainer, and VideoProcessor.
"""

import os
import sys
import numpy as np
import pytest

# Ensure sign_language_translator is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sign_engine.landmark_extractor import LandmarkExtractor, SingleHandData, HandResult
from sign_engine.feature_engineering import FeatureEngineer, HandFeatures
from sign_engine.asl_classifier import ASLClassifier
from sign_engine.temporal_tracker import TemporalGestureTracker
from sign_engine.gesture_trainer import GestureTrainer
from sign_engine.video_processor import VideoProcessor, SubtitleSegment


def test_feature_engineering_invariance():
    """Verify feature extractor handles joint angles, finger extension, and scale invariance."""
    fe = FeatureEngineer()

    # Generate synthetic hand landmarks (open palm '5' or 'B')
    lms = [(0.5, 0.8, 0.0)]  # Wrist
    for f in range(5):
        bx = 0.4 + f * 0.05
        lms.append((bx, 0.65, 0.0))  # MCP
        lms.append((bx, 0.50, 0.0))  # PIP
        lms.append((bx, 0.35, 0.0))  # DIP
        lms.append((bx, 0.20, 0.0))  # TIP

    feats = fe.extract_features(lms)

    assert len(feats.joint_angles) == 15
    assert len(feats.finger_extensions) == 5
    assert "thumb_index" in feats.fingertip_distances
    assert feats.feature_vector.shape[0] > 90
    # Fingers 1..4 are extended
    assert feats.finger_extensions[1] > 0.7
    assert feats.finger_extensions[2] > 0.7


def test_asl_classifier_rules():
    """Test geometric rule classification for key ASL signs."""
    classifier = ASLClassifier()

    # Create 'L' hand shape: Thumb & Index extended, Middle, Ring, Pinky folded
    lms_l = [(0.5, 0.8, 0.0)]  # Wrist
    # Thumb (extended sideways)
    lms_l.extend([(0.42, 0.75, 0.0), (0.35, 0.70, 0.0), (0.28, 0.65, 0.0), (0.20, 0.60, 0.0)])
    # Index (extended up)
    lms_l.extend([(0.48, 0.65, 0.0), (0.48, 0.50, 0.0), (0.48, 0.35, 0.0), (0.48, 0.20, 0.0)])
    # Middle (folded)
    lms_l.extend([(0.52, 0.65, 0.0), (0.52, 0.70, -0.05), (0.52, 0.72, -0.08), (0.52, 0.74, -0.1)])
    # Ring (folded)
    lms_l.extend([(0.56, 0.65, 0.0), (0.56, 0.70, -0.05), (0.56, 0.72, -0.08), (0.56, 0.74, -0.1)])
    # Pinky (folded)
    lms_l.extend([(0.60, 0.65, 0.0), (0.60, 0.70, -0.05), (0.60, 0.72, -0.08), (0.60, 0.74, -0.1)])

    hand_data = SingleHandData(
        landmarks=lms_l,
        world_landmarks=lms_l,
        handedness="Right",
        confidence=0.95,
        bbox=(0.2, 0.2, 0.6, 0.8),
        bbox_pixels=(128, 96, 384, 384),
    )

    result = classifier.classify_hand(hand_data)
    assert result.predicted_sign in ("L", "I LOVE YOU", "D")
    assert result.confidence > 0.5
    assert len(result.top_predictions) >= 1


def test_temporal_tracker_hello():
    """Test dynamic motion gesture detection for waving (HELLO)."""
    tracker = TemporalGestureTracker(window_size=20, cooldown_seconds=0.0)

    # Simulate 15 frames of hand moving left and right with open fingers
    for i in range(15):
        # Oscillate X position: 0.4 -> 0.6 -> 0.4 -> 0.6
        x_val = 0.5 + 0.12 * np.sin(i * 0.8)
        lms = [(x_val, 0.5, 0.0)] * 21
        sign = tracker.update(
            landmarks=lms,
            finger_extensions=[0.8, 1.0, 1.0, 1.0, 1.0],  # Open hand
            thumb_index_dist=0.6,
            timestamp=i * 0.05,
        )
        if sign == "HELLO":
            break

    # Tracker should successfully identify oscillating motion
    assert sign == "HELLO" or tracker._detect_waving()


def test_custom_gesture_trainer(tmp_path):
    """Test recording, training, and predicting custom gestures."""
    data_dir = str(tmp_path / "custom_data")
    trainer = GestureTrainer(data_dir=data_dir)

    # Sample landmarks
    mock_lms = [(0.5, 0.8, 0.0)] * 21

    # Record 4 samples for 'CUSTOM_SIGN_A'
    for _ in range(4):
        trainer.add_sample("CUSTOM_SIGN_A", mock_lms)

    assert len(trainer.get_registered_gestures()) == 1
    assert trainer.get_registered_gestures()[0]["name"] == "CUSTOM_SIGN_A"

    fe = FeatureEngineer()
    feats = fe.extract_features(mock_lms)
    pred = trainer.predict_custom(feats)
    assert pred is not None
    assert pred[0] == "CUSTOM_SIGN_A"


def test_video_subtitle_formatting():
    """Verify SRT and WebVTT generation formatting."""
    vp = VideoProcessor()
    segments = [
        SubtitleSegment(
            index=1,
            start_time=1.5,
            end_time=3.2,
            text="HELLO",
            confidence=0.92,
            sign_type="phrase",
        ),
        SubtitleSegment(
            index=2,
            start_time=3.5,
            end_time=5.0,
            text="THANK YOU",
            confidence=0.88,
            sign_type="phrase",
        ),
    ]

    srt = vp._generate_srt(segments)
    assert "00:00:01,500 --> 00:00:03,200" in srt
    assert "HELLO" in srt
    assert "00:00:03,500 --> 00:00:05,000" in srt
    vtt = vp._generate_vtt(segments)
    assert "WEBVTT" in vtt
    assert "00:00:01.500 --> 00:00:03.200" in vtt


def test_temporal_tracker_thank_you():
    """Test dynamic motion gesture detection for THANK YOU (moving forward and downward from chin)."""
    tracker = TemporalGestureTracker(window_size=30, cooldown_seconds=0.0)

    detected = None
    # Simulate 16 frames of hand moving downward/forward from chin (y increases from 0.35 to 0.55)
    for i in range(16):
        y_pos = 0.35 + (i / 16.0) * 0.18
        # Mock hand with open fingers and wrist at y_pos
        lms = [(0.5, y_pos, 0.0)]
        for f in range(5):
            bx = 0.4 + f * 0.05
            lms.extend([(bx, y_pos - 0.10, 0.0), (bx, y_pos - 0.20, 0.0), (bx, y_pos - 0.28, 0.0), (bx, y_pos - 0.35, 0.0)])

        sign = tracker.update(
            landmarks=lms,
            finger_extensions=[0.8, 1.0, 1.0, 1.0, 1.0],  # Open flat hand
            thumb_index_dist=0.45,
            timestamp=i * 0.05,
        )
        if sign == "THANK YOU":
            detected = sign
            break

    assert detected == "THANK YOU" or tracker._detect_thank_you()


def test_temporal_tracker_yes():
    """Test dynamic motion gesture detection for YES (nodding fist)."""
    tracker = TemporalGestureTracker(window_size=30, cooldown_seconds=0.0)

    detected = None
    for i in range(20):
        y_pos = 0.5 + 0.08 * np.sin(i * 0.8)
        lms = [(0.5, y_pos, 0.0)] * 21
        sign = tracker.update(
            landmarks=lms,
            finger_extensions=[0.2, 0.1, 0.1, 0.1, 0.1],  # Closed fist
            thumb_index_dist=0.15,
            timestamp=i * 0.05,
        )
        if sign == "YES":
            detected = sign
            break

    assert detected == "YES" or tracker._detect_nodding_fist()

