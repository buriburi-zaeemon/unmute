"""
Video Processor Module for pre-recorded video file translation.
Processes MP4, WebM, MOV, AVI videos frame-by-frame, extracts hand landmarks,
aggregates continuous gestures into time-stamped subtitle events, and generates SRT/VTT/JSON transcripts.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Callable
import os
import time
import cv2
import numpy as np

from .landmark_extractor import LandmarkExtractor, HandResult
from .feature_engineering import FeatureEngineer
from .asl_classifier import ASLClassifier
from .temporal_tracker import TemporalGestureTracker
from .gesture_trainer import GestureTrainer


@dataclass
class SubtitleSegment:
    index: int
    start_time: float  # in seconds
    end_time: float  # in seconds
    text: str
    confidence: float
    sign_type: str = "alphabet"

    @property
    def start_time_srt(self) -> str:
        return self._format_timestamp(self.start_time, separator=",")

    @property
    def end_time_srt(self) -> str:
        return self._format_timestamp(self.end_time, separator=",")

    @property
    def start_time_vtt(self) -> str:
        return self._format_timestamp(self.start_time, separator=".")

    @property
    def end_time_vtt(self) -> str:
        return self._format_timestamp(self.end_time, separator=".")

    @staticmethod
    def _format_timestamp(seconds: float, separator: str = ",") -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}{separator}{millis:03d}"


@dataclass
class VideoProcessingResult:
    video_id: str
    duration_seconds: float
    total_frames: int
    fps: float
    processed_frames: int
    segments: List[SubtitleSegment] = field(default_factory=list)
    full_transcript: str = ""
    annotated_video_path: Optional[str] = None
    srt_content: str = ""
    vtt_content: str = ""


class VideoProcessor:
    """Processes video files asynchronously for sign language detection and subtitles."""

    def __init__(
        self,
        landmark_extractor: Optional[LandmarkExtractor] = None,
        classifier: Optional[ASLClassifier] = None,
        gesture_trainer: Optional[GestureTrainer] = None,
    ):
        self.extractor = landmark_extractor or LandmarkExtractor()
        self.classifier = classifier or ASLClassifier()
        self.gesture_trainer = gesture_trainer or GestureTrainer()
        self.feature_engineer = FeatureEngineer()

    def process_video(
        self,
        video_path: str,
        output_annotated_video: bool = False,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> VideoProcessingResult:
        """
        Processes video file and returns synchronized translation transcript and segments.
        Args:
            video_path: Local path to video file.
            output_annotated_video: If True, writes annotated video with skeleton overlays.
            progress_callback: Optional callback receiving (progress_percentage, status_text).
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Unable to open video stream from {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps

        temporal_tracker = TemporalGestureTracker(window_size=20)

        # Raw frame predictions: List of (timestamp, predicted_sign, confidence, sign_type)
        frame_predictions: List[Tuple[float, str, float, str]] = []

        writer = None
        annotated_path = None
        if output_annotated_video:
            base_dir = os.path.dirname(video_path)
            annotated_path = os.path.join(base_dir, f"annotated_{os.path.basename(video_path)}")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(annotated_path, fourcc, fps, (width, height))

        frame_idx = 0

        # Sample every 1 or 2 frames for speed and accuracy
        frame_step = 1 if total_frames < 300 else 2

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                current_time = frame_idx / fps

                if frame_idx % frame_step == 0:
                    hand_result = self.extractor.extract(frame)

                    if hand_result.has_hands:
                        primary_hand = hand_result.hands[0]
                        feats = self.feature_engineer.extract_features(primary_hand.landmarks)

                        # Check dynamic motion
                        dyn_sign = temporal_tracker.update(
                            primary_hand.landmarks,
                            feats.finger_extensions,
                            feats.fingertip_distances["thumb_index"],
                            timestamp=current_time,
                        )

                        # Check custom gesture
                        custom_pred = self.gesture_trainer.predict_custom(feats)
                        if custom_pred:
                            pred_sign, conf = custom_pred
                            s_type = "custom"
                        else:
                            rec_result = self.classifier.classify_hand(primary_hand, dynamic_sign=dyn_sign)
                            pred_sign = rec_result.predicted_sign
                            conf = rec_result.confidence
                            s_type = rec_result.sign_type

                        # Filter out noise / non-signs
                        if pred_sign not in ("UNKNOWN", "NONE") and conf >= 0.55:
                            frame_predictions.append((current_time, pred_sign, conf, s_type))

                        if writer is not None:
                            annotated = self.extractor.draw_landmarks_on_image(frame, hand_result)
                            cv2.putText(
                                annotated,
                                f"Sign: {pred_sign} ({conf:.2f})",
                                (30, 50),
                                cv2.FONT_HERSHEY_DUPLEX,
                                1.0,
                                (0, 240, 255),
                                2,
                                cv2.LINE_AA,
                            )
                            writer.write(annotated)
                    else:
                        temporal_tracker.clear()
                        if writer is not None:
                            writer.write(frame)

                frame_idx += 1

                if progress_callback and frame_idx % 15 == 0:
                    pct = min(100.0, (frame_idx / total_frames) * 100.0)
                    progress_callback(pct, f"Analyzing frame {frame_idx}/{total_frames}...")

        finally:
            cap.release()
            if writer is not None:
                writer.release()

        # Aggregate raw frame predictions into consolidated subtitle segments
        segments = self._aggregate_segments(frame_predictions, min_duration=0.3)
        full_transcript = " ".join([s.text for s in segments])

        srt_content = self._generate_srt(segments)
        vtt_content = self._generate_vtt(segments)

        if progress_callback:
            progress_callback(100.0, "Translation complete!")

        return VideoProcessingResult(
            video_id=os.path.basename(video_path),
            duration_seconds=round(duration, 2),
            total_frames=total_frames,
            fps=round(fps, 2),
            processed_frames=frame_idx,
            segments=segments,
            full_transcript=full_transcript,
            annotated_video_path=annotated_path,
            srt_content=srt_content,
            vtt_content=vtt_content,
        )

    def _aggregate_segments(
        self,
        frame_preds: List[Tuple[float, str, float, str]],
        min_duration: float = 0.25,
        max_gap: float = 0.6,
    ) -> List[SubtitleSegment]:
        """Merges frame-by-frame predictions into coherent continuous timed segments."""
        if not frame_preds:
            return []

        segments: List[SubtitleSegment] = []
        cur_sign = frame_preds[0][1]
        cur_type = frame_preds[0][3]
        start_t = frame_preds[0][0]
        last_t = frame_preds[0][0]
        confs = [frame_preds[0][2]]

        for t, sign, conf, s_type in frame_preds[1:]:
            # If same sign and time gap is small, continue current segment
            if sign == cur_sign and (t - last_t) <= max_gap:
                last_t = t
                confs.append(conf)
            else:
                # Close current segment if meets minimum duration
                seg_dur = last_t - start_t
                if seg_dur >= min_duration or len(confs) >= 3:
                    segments.append(
                        SubtitleSegment(
                            index=len(segments) + 1,
                            start_time=round(start_t, 2),
                            end_time=round(max(last_t, start_t + 0.5), 2),
                            text=cur_sign,
                            confidence=round(float(np.mean(confs)), 2),
                            sign_type=cur_type,
                        )
                    )
                # Start new segment
                cur_sign = sign
                cur_type = s_type
                start_t = t
                last_t = t
                confs = [conf]

        # Final segment
        if (last_t - start_t) >= min_duration or len(confs) >= 3:
            segments.append(
                SubtitleSegment(
                    index=len(segments) + 1,
                    start_time=round(start_t, 2),
                    end_time=round(max(last_t, start_t + 0.5), 2),
                    text=cur_sign,
                    confidence=round(float(np.mean(confs)), 2),
                    sign_type=cur_type,
                )
            )

        return segments

    def _generate_srt(self, segments: List[SubtitleSegment]) -> str:
        """Generates standard SRT subtitle formatting."""
        lines = []
        for seg in segments:
            lines.append(str(seg.index))
            lines.append(f"{seg.start_time_srt} --> {seg.end_time_srt}")
            lines.append(seg.text)
            lines.append("")
        return "\n".join(lines)

    def _generate_vtt(self, segments: List[SubtitleSegment]) -> str:
        """Generates WebVTT subtitle formatting."""
        lines = ["WEBVTT", ""]
        for seg in segments:
            lines.append(str(seg.index))
            lines.append(f"{seg.start_time_vtt} --> {seg.end_time_vtt}")
            lines.append(seg.text)
            lines.append("")
        return "\n".join(lines)
