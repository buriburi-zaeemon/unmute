"""
Temporal Gesture Tracker module for dynamic sign recognition.
Maintains a sliding window of hand positions, palm scale, and trajectory vectors to detect motion signs:
- 'HELLO' (Side-to-side waving motion of open hand)
- 'THANK YOU' (Hand starting near chin/mouth and sweeping forward/downward toward recipient)
- 'YES' (Fist nodding up and down at the wrist)
- 'NO' (Index and middle fingers snapping closed onto thumb)
- 'PLEASE' (Circular motion of flat open palm on chest)
- 'J' (Pinky tracing a 'J' downward hook trajectory)
- 'Z' (Index tracing a 'Z' three-stroke zigzag trajectory)
"""

from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import time
import numpy as np


@dataclass
class FrameState:
    timestamp: float
    wrist_pos: Tuple[float, float, float]  # (x, y, z)
    index_tip_pos: Tuple[float, float, float]
    middle_tip_pos: Tuple[float, float, float]
    pinky_tip_pos: Tuple[float, float, float]
    palm_scale: float  # Distance between wrist and middle MCP (measures proximity to camera)
    finger_extensions: List[float]  # [thumb, index, middle, ring, pinky] [0..1]
    thumb_index_dist: float
    thumb_middle_dist: float


class TemporalGestureTracker:
    """Detects multi-frame dynamic gestures across a rolling time-window with high sensitivity and noise tolerance."""

    def __init__(self, window_size: int = 36, cooldown_seconds: float = 0.9):
        self.window_size = window_size
        self.cooldown_seconds = cooldown_seconds
        self._history: deque[FrameState] = deque(maxlen=window_size)
        self._last_detected_time: Dict[str, float] = {}

    def update(
        self,
        landmarks: List[Tuple[float, float, float]],
        finger_extensions: List[float],
        thumb_index_dist: float,
        timestamp: Optional[float] = None,
    ) -> Optional[str]:
        """
        Updates the temporal state and evaluates whether a dynamic sign was performed.
        Args:
            landmarks: 21 (x, y, z) hand landmarks.
            finger_extensions: [thumb, index, middle, ring, pinky] [0..1]
            thumb_index_dist: distance between thumb tip and index tip
            timestamp: frame timestamp in seconds (defaults to time.time())
        Returns:
            Detected gesture string (e.g. 'THANK YOU', 'HELLO', 'YES', 'NO', 'PLEASE', 'J', 'Z') or None.
        """
        if timestamp is None:
            timestamp = time.time()

        pts = np.array(landmarks, dtype=np.float32)
        wrist = (float(pts[0][0]), float(pts[0][1]), float(pts[0][2]))
        index_tip = (float(pts[8][0]), float(pts[8][1]), float(pts[8][2]))
        middle_tip = (float(pts[12][0]), float(pts[12][1]), float(pts[12][2]))
        pinky_tip = (float(pts[20][0]), float(pts[20][1]), float(pts[20][2]))

        # Palm scale: distance between wrist [0] and middle MCP [9]
        palm_scale = float(np.linalg.norm(pts[0] - pts[9]))

        # Distance between thumb tip [4] and middle tip [12]
        thumb_middle_dist = float(np.linalg.norm(pts[4] - pts[12]))

        state = FrameState(
            timestamp=timestamp,
            wrist_pos=wrist,
            index_tip_pos=index_tip,
            middle_tip_pos=middle_tip,
            pinky_tip_pos=pinky_tip,
            palm_scale=palm_scale,
            finger_extensions=finger_extensions,
            thumb_index_dist=thumb_index_dist,
            thumb_middle_dist=thumb_middle_dist,
        )
        self._history.append(state)

        if len(self._history) < 6:
            return None

        now = timestamp

        # Check dynamic gesture candidates in priority order
        # 1. THANK YOU: Moving forward/downward from mouth/chin with open palm
        if self._is_available("THANK YOU", now):
            if self._detect_thank_you():
                self._last_detected_time["THANK YOU"] = now
                return "THANK YOU"

        # 2. HELLO: Side-to-side waving motion of open hand
        if self._is_available("HELLO", now):
            if self._detect_waving():
                self._last_detected_time["HELLO"] = now
                return "HELLO"

        # 3. YES: Fist nodding up and down
        if self._is_available("YES", now):
            if self._detect_nodding_fist():
                self._last_detected_time["YES"] = now
                return "YES"

        # 4. NO: Pinching/snapping closure of index+middle onto thumb
        if self._is_available("NO", now):
            if self._detect_snapping_no():
                self._last_detected_time["NO"] = now
                return "NO"

        # 5. PLEASE: Circular trajectory of open hand
        if self._is_available("PLEASE", now):
            if self._detect_circular_motion():
                self._last_detected_time["PLEASE"] = now
                return "PLEASE"

        # 6. 'J': Tracing hook with pinky
        if self._is_available("J", now):
            if self._detect_j_curve():
                self._last_detected_time["J"] = now
                return "J"

        # 7. 'Z': Tracing Z with index
        if self._is_available("Z", now):
            if self._detect_z_stroke():
                self._last_detected_time["Z"] = now
                return "Z"

        return None

    def get_dynamic_likelihoods(self) -> Dict[str, float]:
        """Returns instantaneous likelihood scores [0..1] for dynamic gestures during continuous motion."""
        scores: Dict[str, float] = {}
        if len(self._history) < 6:
            return scores

        recent = list(self._history)
        avg_ext = np.mean([np.mean(s.finger_extensions[1:]) for s in recent[-6:]])

        # THANK YOU motion score
        if avg_ext >= 0.50:
            ys = [s.wrist_pos[1] for s in recent]
            scales = [s.palm_scale for s in recent]
            y_drop = max(ys) - min(ys)
            scale_grow = (scales[-1] - min(scales)) / (min(scales) + 1e-6)

            # Check if moving downward or forward
            if y_drop > 0.04 or scale_grow > 0.08:
                scores["THANK YOU"] = min(0.96, 0.50 + y_drop * 4.0 + scale_grow * 2.0)

        # HELLO motion score
        if avg_ext >= 0.50:
            xs = [s.wrist_pos[0] for s in recent]
            x_span = max(xs) - min(xs)
            if x_span > 0.05:
                scores["HELLO"] = min(0.96, 0.40 + x_span * 4.0)

        return scores

    def _is_available(self, gesture: str, now: float) -> bool:
        last_t = self._last_detected_time.get(gesture, 0.0)
        return (now - last_t) > self.cooldown_seconds

    def _detect_thank_you(self) -> bool:
        """
        Detects ASL 'THANK YOU':
        Hand starts near chin / face level and moves outward and forward/downward towards recipient.
        Key signals:
        1. Flat open hand (fingers 1..4 extended).
        2. Downward trajectory (Y increases in image coordinates) OR forward scale increase (hand closer to camera).
        """
        recent = list(self._history)
        if len(recent) < 6:
            return False

        # Open palm check across recent frames
        avg_ext = np.mean([np.mean(s.finger_extensions[1:]) for s in recent[-8:]])
        if avg_ext < 0.50:
            return False

        # Check sub-windows (from 6 frames up to full window)
        for w_len in (8, 12, 16, 20, len(recent)):
            if len(recent) < w_len:
                continue
            sub = recent[-w_len:]

            y_start = sub[0].wrist_pos[1]
            y_end = sub[-1].wrist_pos[1]
            dy = y_end - y_start

            scale_start = sub[0].palm_scale
            scale_end = sub[-1].palm_scale
            d_scale = (scale_end - scale_start) / (scale_start + 1e-6)

            ys = [s.wrist_pos[1] for s in sub]
            y_peak_to_trough = max(ys) - min(ys)

            # Condition 1: Direct downward sweep from chin (dy >= 0.045)
            # Condition 2: Forward push towards camera (d_scale >= 0.12)
            # Condition 3: Combined forward-downward arc (dy >= 0.03 and d_scale >= 0.06)
            if (dy >= 0.045 and y_peak_to_trough >= 0.045) or (d_scale >= 0.12) or (dy >= 0.03 and d_scale >= 0.06):
                return True

        return False

    def _detect_waving(self) -> bool:
        """Detects side-to-side oscillation of open palm (HELLO)."""
        recent = list(self._history)
        if len(recent) < 8:
            return False

        avg_ext = np.mean([np.mean(s.finger_extensions[1:]) for s in recent[-8:]])
        if avg_ext < 0.50:
            return False

        xs = [s.wrist_pos[0] for s in recent]
        dxs = np.diff(xs)

        # Smooth direction changes
        sign_changes = 0
        for i in range(len(dxs) - 1):
            if dxs[i] * dxs[i + 1] < -1e-6 and (abs(dxs[i]) + abs(dxs[i+1])) > 0.004:
                sign_changes += 1

        x_span = max(xs) - min(xs)
        return (sign_changes >= 1 and x_span > 0.06) or (sign_changes >= 2 and x_span > 0.04)

    def _detect_nodding_fist(self) -> bool:
        """Detects up-down oscillation of a fist (YES)."""
        recent = list(self._history)
        if len(recent) < 8:
            return False

        avg_ext = np.mean([np.mean(s.finger_extensions[1:]) for s in recent[-8:]])
        if avg_ext > 0.42:  # Must be fist-like
            return False

        ys = [s.wrist_pos[1] for s in recent]
        dys = np.diff(ys)

        sign_changes = 0
        for i in range(len(dys) - 1):
            if dys[i] * dys[i + 1] < -1e-6 and (abs(dys[i]) + abs(dys[i+1])) > 0.003:
                sign_changes += 1

        y_span = max(ys) - min(ys)
        return (sign_changes >= 1 and y_span > 0.05) or (sign_changes >= 2 and y_span > 0.035)

    def _detect_snapping_no(self) -> bool:
        """Detects rapid closing of index & middle fingers onto thumb (NO)."""
        recent = list(self._history)
        if len(recent) < 8:
            return False

        dists = [s.thumb_index_dist for s in recent]
        first_half = np.mean(dists[:max(3, len(dists) // 2)])
        second_half = np.mean(dists[-max(3, len(dists) // 2):])

        # Distance should decrease by at least 30% from open to pinched
        return first_half > 0.28 and second_half < 0.20 and (first_half - second_half) > 0.08

    def _detect_circular_motion(self) -> bool:
        """Detects circular trajectory of open palm on chest (PLEASE)."""
        recent = list(self._history)
        if len(recent) < 12:
            return False

        avg_ext = np.mean([np.mean(s.finger_extensions[1:]) for s in recent[-8:]])
        if avg_ext < 0.50:
            return False

        xs = [s.wrist_pos[0] for s in recent]
        ys = [s.wrist_pos[1] for s in recent]
        x_span = max(xs) - min(xs)
        y_span = max(ys) - min(ys)

        if x_span > 0.04 and y_span > 0.04:
            ratio = x_span / (y_span + 1e-6)
            return 0.35 < ratio < 2.8
        return False

    def _detect_j_curve(self) -> bool:
        """Detects pinky tracing down and curving left/up ('J')."""
        recent = list(self._history)
        if len(recent) < 8:
            return False

        # Only pinky extended
        if recent[-1].finger_extensions[4] < 0.55 or recent[-1].finger_extensions[1] > 0.45:
            return False

        pts = [s.pinky_tip_pos for s in recent]
        ys = [p[1] for p in pts]
        xs = [p[0] for p in pts]

        return (max(ys) - min(ys) > 0.06) and (max(xs) - min(xs) > 0.04)

    def _detect_z_stroke(self) -> bool:
        """Detects index tracing horizontal -> diagonal -> horizontal ('Z')."""
        recent = list(self._history)
        if len(recent) < 8:
            return False

        # Only index extended
        if recent[-1].finger_extensions[1] < 0.55 or recent[-1].finger_extensions[2] > 0.45:
            return False

        xs = [s.index_tip_pos[0] for s in recent]
        dxs = np.diff(xs)

        sign_changes = 0
        for i in range(len(dxs) - 1):
            if dxs[i] * dxs[i + 1] < -1e-6 and abs(dxs[i]) > 0.003:
                sign_changes += 1

        return sign_changes >= 1 and (max(xs) - min(xs) > 0.06)

    def clear(self):
        """Reset temporal state."""
        self._history.clear()
