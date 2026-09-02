"""
High-Precision ASL Recognition Engine.
Combines geometric anatomical heuristics, invariant finger curl states,
inter-joint distance metrics, and dynamic motion tracking to classify ASL signs in real time.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from .feature_engineering import FeatureEngineer, HandFeatures
from .landmark_extractor import SingleHandData


@dataclass
class TopPrediction:
    label: str
    confidence: float


@dataclass
class RecognitionResult:
    predicted_sign: str
    confidence: float
    is_stable: bool
    top_predictions: List[TopPrediction] = field(default_factory=list)
    sign_type: str = "alphabet"
    handedness: str = "Right"
    finger_states: Dict[str, str] = field(default_factory=dict)


class ASLClassifier:
    """Robust geometric and heuristic classifier for real-time sign recognition."""

    def __init__(self, model_dir: Optional[str] = None, stability_threshold: int = 2):
        self.feature_engineer = FeatureEngineer()
        self.stability_threshold = stability_threshold
        self._history: List[str] = []
        self._confidence_history: List[float] = []

    def classify_landmarks(self, landmarks: List[Tuple[float, float, float]], handedness: str = "Right") -> Tuple[str, float, List[TopPrediction]]:
        """
        Anatomical sign classifier evaluating physical finger extensions,
        joint angles, and fingertip distances.
        """
        pts = np.array(landmarks, dtype=np.float32)  # 21 points
        palm_size = float(np.linalg.norm(pts[9] - pts[0]))
        if palm_size < 1e-4:
            palm_size = 1.0

        v_hand = pts[9] - pts[0]
        hand_len = np.linalg.norm(v_hand)
        v_hand_unit = v_hand / (hand_len if hand_len > 1e-6 else 1.0)

        # -------------------------------------------------------------
        # 1. EXTENSION OF 4 MAIN FINGERS (INDEX, MIDDLE, RING, PINKY)
        # -------------------------------------------------------------
        def is_finger_up(tip_i: int, dip_i: int, pip_i: int, mcp_i: int) -> bool:
            d_tip = np.linalg.norm(pts[tip_i] - pts[0])
            d_pip = np.linalg.norm(pts[pip_i] - pts[0])
            proj_tip = np.dot(pts[tip_i] - pts[0], v_hand_unit)
            proj_pip = np.dot(pts[pip_i] - pts[0], v_hand_unit)
            y_check = pts[tip_i][1] < pts[pip_i][1] + 0.05
            return (d_tip > d_pip * 1.05) and (proj_tip > proj_pip) and y_check

        index_up = is_finger_up(8, 7, 6, 5)
        middle_up = is_finger_up(12, 11, 10, 9)
        ring_up = is_finger_up(16, 15, 14, 13)
        pinky_up = is_finger_up(20, 19, 18, 17)

        # -------------------------------------------------------------
        # 2. THUMB STATES
        # -------------------------------------------------------------
        d_t4_mcp5 = float(np.linalg.norm(pts[4] - pts[5]) / palm_size)
        d_t4_mcp17 = float(np.linalg.norm(pts[4] - pts[17]) / palm_size)
        d_t4_t8 = float(np.linalg.norm(pts[4] - pts[8]) / palm_size)
        d_t4_t12 = float(np.linalg.norm(pts[4] - pts[12]) / palm_size)
        d_t8_t12 = float(np.linalg.norm(pts[8] - pts[12]) / palm_size)

        # Thumb is extended if far from knuckles
        thumb_extended = (d_t4_mcp5 > 0.38) or (d_t4_mcp17 > 0.62) or (d_t4_t8 > 0.40 and not index_up)

        # Thumb pointing straight up (higher than knuckle by clear margin)
        thumb_high_up = (pts[4][1] < pts[5][1] - 0.12) and (pts[4][1] < pts[2][1] - 0.05)

        candidates: List[Tuple[str, float]] = []

        # -------------------------------------------------------------
        # 3. PATTERN MATCHING RULES
        # -------------------------------------------------------------

        # === 3A. MULTI-FINGER PHRASES & SPECIAL COMBINATIONS ===
        # 'I LOVE YOU' (Thumb, Index, Pinky UP)
        if thumb_extended and index_up and pinky_up and not middle_up and not ring_up:
            candidates.append(("I LOVE YOU", 0.96))

        # 'Y' (Thumb and Pinky UP, Index/Middle/Ring DOWN)
        elif thumb_extended and pinky_up and not index_up and not middle_up and not ring_up:
            candidates.append(("Y", 0.95))

        # 'I' (Pinky UP only, Thumb folded)
        elif pinky_up and not index_up and not middle_up and not ring_up and not thumb_extended:
            candidates.append(("I", 0.95))

        # 'L' (Thumb and Index UP at 90 deg, Middle/Ring/Pinky DOWN)
        elif thumb_extended and index_up and not middle_up and not ring_up and not pinky_up:
            if d_t4_t8 > 0.35:
                candidates.append(("L", 0.96))
            else:
                candidates.append(("D", 0.88))

        # === 3B. TWO FINGERS UP: 'V', 'PEACE', 'U', 'R', '2' ===
        elif index_up and middle_up and not ring_up and not pinky_up:
            if d_t8_t12 > 0.20:
                candidates.append(("V", 0.95))
                candidates.append(("PEACE", 0.94))
                candidates.append(("2", 0.90))
            else:
                # Crossed test for 'R'
                if pts[8][0] > pts[12][0] + 0.01:
                    candidates.append(("R", 0.92))
                    candidates.append(("U", 0.88))
                else:
                    candidates.append(("U", 0.94))
                    candidates.append(("V", 0.82))

        # === 3C. THREE FINGERS UP: 'W', '3' ===
        elif index_up and middle_up and ring_up and not pinky_up:
            candidates.append(("W", 0.94))
            candidates.append(("3", 0.92))

        elif thumb_extended and index_up and middle_up and not ring_up and not pinky_up:
            candidates.append(("3", 0.94))
            candidates.append(("W", 0.85))

        # === 3D. SINGLE INDEX UP: 'D', '1', 'X' ===
        elif index_up and not middle_up and not ring_up and not pinky_up and not thumb_extended:
            if d_t4_t12 < 0.35:
                candidates.append(("D", 0.95))
                candidates.append(("1", 0.88))
            else:
                candidates.append(("1", 0.94))
                candidates.append(("D", 0.88))

        # === 3E. PINCH / LOOP GESTURES: 'F', 'OKAY', '9', 'O', 'C' ===
        elif d_t4_t8 < 0.28:
            if middle_up and ring_up and pinky_up:
                candidates.append(("F", 0.96))
                candidates.append(("OKAY", 0.95))
                candidates.append(("9", 0.92))
            elif not middle_up and not ring_up and not pinky_up:
                candidates.append(("O", 0.94))
        elif d_t4_t8 < 0.45 and not index_up and not middle_up and not ring_up and not pinky_up:
            candidates.append(("C", 0.92))

        # === 3F. FOUR OR FIVE FINGERS UP: 'B', '4', '5', 'STOP', 'THANK YOU', 'HELLO', 'PLEASE' ===
        elif index_up and middle_up and ring_up and pinky_up:
            if thumb_extended or d_t4_mcp5 > 0.38:
                candidates.append(("STOP", 0.90))
                candidates.append(("5", 0.88))
                # Open palm handshape is also the canonical base for dynamic signs:
                candidates.append(("THANK YOU", 0.75))
                candidates.append(("HELLO", 0.70))
                candidates.append(("PLEASE", 0.65))
            else:
                candidates.append(("B", 0.94))
                candidates.append(("4", 0.90))

        # === 3G. FIST FAMILY: 'A', 'S', 'E', 'T', 'THUMBS UP', 'THUMBS DOWN', 'YES' ===
        elif not index_up and not middle_up and not ring_up and not pinky_up:
            if thumb_high_up:
                candidates.append(("THUMBS UP", 0.96))
            elif pts[4][1] > pts[0][1] + 0.15 and thumb_extended:
                candidates.append(("THUMBS DOWN", 0.94))
            else:
                # 'A': Thumb on side of index knuckle
                if d_t4_mcp5 < 0.35 and pts[4][1] < pts[5][1] + 0.08:
                    candidates.append(("A", 0.94))
                    candidates.append(("S", 0.85))
                    candidates.append(("YES", 0.70))
                else:
                    candidates.append(("S", 0.92))
                    candidates.append(("A", 0.82))
                    candidates.append(("YES", 0.70))

        # === 3H. SIDEWAYS GESTURES: 'G', 'H' ===
        dx_idx = abs(pts[8][0] - pts[5][0])
        dy_idx = abs(pts[8][1] - pts[5][1])
        if dx_idx > dy_idx and dx_idx > 0.15 and not pinky_up:
            if not middle_up:
                candidates.append(("G", 0.93))
            else:
                candidates.append(("H", 0.93))

        # Sort candidates
        if not candidates:
            up_count = sum([index_up, middle_up, ring_up, pinky_up])
            if up_count >= 4:
                candidates.append(("B", 0.75))
                candidates.append(("STOP", 0.70))
                candidates.append(("THANK YOU", 0.65))
            elif up_count == 0:
                candidates.append(("A", 0.75))
                candidates.append(("YES", 0.65))
            elif up_count == 1 and index_up:
                candidates.append(("D", 0.75))
            elif up_count == 2 and index_up and middle_up:
                candidates.append(("V", 0.75))
            elif up_count == 3:
                candidates.append(("W", 0.75))
            else:
                candidates.append(("UNKNOWN", 0.20))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top_sign, top_conf = candidates[0]
        top_list = [TopPrediction(label=s, confidence=round(c, 2)) for s, c in candidates[:5]]

        return top_sign, top_conf, top_list

    def classify_hand(
        self,
        hand_data: SingleHandData,
        dynamic_sign: Optional[str] = None,
        dynamic_likelihoods: Optional[Dict[str, float]] = None,
    ) -> RecognitionResult:
        """Classifies hand sign and updates stability buffer with dynamic motion integration."""
        top_sign, top_conf, top_list = self.classify_landmarks(hand_data.landmarks, hand_data.handedness)

        # Merge continuous dynamic likelihoods if available
        if dynamic_likelihoods:
            for dyn_label, dyn_score in dynamic_likelihoods.items():
                if dyn_score > 0.50:
                    # Boost or insert dynamic candidate
                    top_list = [p for p in top_list if p.label != dyn_label]
                    top_list.insert(0, TopPrediction(dyn_label, round(dyn_score, 2)))
                    if dyn_score > top_conf:
                        top_sign = dyn_label
                        top_conf = dyn_score

        # If a full dynamic gesture trigger occurred (e.g. THANK YOU, HELLO, YES, NO)
        if dynamic_sign:
            self._update_history(dynamic_sign, 0.97)
            dyn_preds = [TopPrediction(dynamic_sign, 0.97)]
            for p in top_list:
                if p.label != dynamic_sign:
                    dyn_preds.append(p)
            return RecognitionResult(
                predicted_sign=dynamic_sign,
                confidence=0.97,
                is_stable=True,
                top_predictions=dyn_preds[:5],
                sign_type="phrase",
                handedness=hand_data.handedness,
            )

        if top_sign in ("SPACE", "CLEAR", "BACKSPACE"):
            s_type = "action"
        elif top_sign in ("HELLO", "THANK YOU", "YES", "NO", "PLEASE", "I LOVE YOU", "PEACE", "OKAY", "THUMBS UP", "THUMBS DOWN", "STOP"):
            s_type = "phrase"
        elif top_sign.isdigit():
            s_type = "number"
        else:
            s_type = "alphabet"

        # Finger states breakdown
        pts = np.array(hand_data.landmarks, dtype=np.float32)
        finger_states = {
            "Thumb": "Extended" if pts[4][1] < pts[5][1] or np.linalg.norm(pts[4]-pts[5]) > 0.15 else "Curled",
            "Index": "Extended" if pts[8][1] < pts[6][1] else "Curled",
            "Middle": "Extended" if pts[12][1] < pts[10][1] else "Curled",
            "Ring": "Extended" if pts[16][1] < pts[14][1] else "Curled",
            "Pinky": "Extended" if pts[20][1] < pts[18][1] else "Curled",
        }

        is_stable = self._update_history(top_sign, top_conf)

        return RecognitionResult(
            predicted_sign=top_sign,
            confidence=round(top_conf, 2),
            is_stable=is_stable,
            top_predictions=top_list,
            sign_type=s_type,
            handedness=hand_data.handedness,
            finger_states=finger_states,
        )

    def _update_history(self, pred: str, conf: float) -> bool:
        if pred == "UNKNOWN":
            return False

        self._history.append(pred)
        self._confidence_history.append(conf)

        if len(self._history) > 6:
            self._history.pop(0)
            self._confidence_history.pop(0)

        if len(self._history) >= self.stability_threshold:
            recent = self._history[-self.stability_threshold:]
            if all(x == pred for x in recent) and conf >= 0.50:
                return True

        return False

    def reset_buffer(self):
        self._history.clear()
        self._confidence_history.clear()
