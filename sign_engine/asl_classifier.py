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
        joint angles, orientation vectors, and fingertip distances across all 26 ASL alphabet
        letters (A-Z) and static phrases.
        """
        pts = np.array(landmarks, dtype=np.float32)  # 21 points
        palm_size = float(np.linalg.norm(pts[9] - pts[0]))
        if palm_size < 1e-4:
            palm_size = 1.0

        # Extract scale and rotation invariant geometric features
        feats = self.feature_engineer.extract_features(landmarks)
        ext = feats.finger_extensions  # [thumb, index, middle, ring, pinky] [0..1]
        angles = feats.joint_angles   # 15 angles

        # Hand & finger vectors in image plane
        v_hand = pts[9] - pts[0]
        hand_len = np.linalg.norm(v_hand)
        v_hand_unit = v_hand / (hand_len if hand_len > 1e-6 else 1.0)
        v_idx = pts[8] - pts[5]
        v_mid = pts[12] - pts[9]
        v_th = pts[4] - pts[1]

        # -------------------------------------------------------------
        # 1. INDIVIDUAL FINGER EXTENSION & ORIENTATION STATES
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

        # Directional checks
        d_mcp5_t8 = float(np.linalg.norm(pts[8] - pts[5]) / palm_size)
        d_mcp9_t12 = float(np.linalg.norm(pts[12] - pts[9]) / palm_size)

        # Straight finger extended downwards (in Y direction, > 0.70 palm_size)
        index_extended_down = ((pts[8][1] - pts[5][1]) > 0.70 * palm_size) and (v_idx[1] > 0.06)
        middle_extended_down = ((pts[12][1] - pts[9][1]) > 0.70 * palm_size) and (v_mid[1] > 0.06)
        index_horizontal = abs(pts[8][0] - pts[5][0]) > 1.1 * abs(pts[8][1] - pts[5][1])
        middle_horizontal = abs(pts[12][0] - pts[9][0]) > 1.1 * abs(pts[12][1] - pts[9][1])

        # Hooked index check (X sign): PIP angle between 40 deg and 138 deg, tip higher than MCP
        index_pip_angle = angles[4]  # Index PIP angle
        index_hooked = (40.0 <= index_pip_angle <= 138.0) and (pts[8][1] < pts[5][1] + 0.04) and (not index_up)

        # -------------------------------------------------------------
        # 2. THUMB STATES & DISTANCES (Normalized by palm size)
        # -------------------------------------------------------------
        d_t4_mcp5 = float(np.linalg.norm(pts[4] - pts[5]) / palm_size)
        d_t4_mcp9 = float(np.linalg.norm(pts[4] - pts[9]) / palm_size)
        d_t4_mcp13 = float(np.linalg.norm(pts[4] - pts[13]) / palm_size)
        d_t4_mcp17 = float(np.linalg.norm(pts[4] - pts[17]) / palm_size)
        d_t4_pip6 = float(np.linalg.norm(pts[4] - pts[6]) / palm_size)
        d_t4_pip10 = float(np.linalg.norm(pts[4] - pts[10]) / palm_size)

        d_t4_t8 = float(np.linalg.norm(pts[4] - pts[8]) / palm_size)
        d_t4_t12 = float(np.linalg.norm(pts[4] - pts[12]) / palm_size)
        d_t4_t16 = float(np.linalg.norm(pts[4] - pts[16]) / palm_size)
        d_t4_t20 = float(np.linalg.norm(pts[4] - pts[20]) / palm_size)

        d_t8_t12 = float(np.linalg.norm(pts[8] - pts[12]) / palm_size)
        d_t12_t16 = float(np.linalg.norm(pts[12] - pts[16]) / palm_size)
        d_t16_t20 = float(np.linalg.norm(pts[16] - pts[20]) / palm_size)

        # Thumb extension criteria
        thumb_extended = (d_t4_mcp5 > 0.38) or (d_t4_mcp17 > 0.60) or (ext[0] > 0.60) or (d_t4_t8 > 0.40 and not index_up)
        thumb_high_up = (pts[4][1] < pts[5][1] - 0.10) and (pts[4][1] < pts[2][1] - 0.04)

        # Palm facing forward / towards camera check
        palm_facing_camera = feats.palm_orientation.get("facing_camera", 0.0) > 0.5 or (pts[0][2] - pts[9][2] > 0.02)

        candidates: List[Tuple[str, float]] = []

        # -------------------------------------------------------------
        # 3. ANATOMICAL PATTERN MATCHING RULES (A-Z & STATIC PHRASES)
        # -------------------------------------------------------------

        # === 3A. 'P' & 'K' FAMILY (Index extended, Middle angled/down, Thumb at middle joint) ===
        # 'P' (Index pointing horizontally forward, Middle pointing DOWN ~90 deg, Thumb resting on middle knuckle)
        if (ext[1] > 0.45 or index_horizontal or index_up) and middle_extended_down and not ring_up and not pinky_up and (d_t4_pip10 < 0.40 or d_t4_mcp9 < 0.40):
            candidates.append(("P", 0.96))
            candidates.append(("K", 0.82))

        # 'K' (Index extended straight UP, Middle angled forward/up ~45 deg, Thumb upright between index & middle knuckles)
        elif index_up and (ext[2] > 0.50 or pts[12][1] < pts[9][1]) and not middle_extended_down and not ring_up and not pinky_up and (d_t4_mcp9 < 0.38 or d_t4_pip10 < 0.38) and (pts[4][1] < pts[2][1] and pts[4][1] < pts[5][1] + 0.02):
            candidates.append(("K", 0.96))
            candidates.append(("P", 0.85))
            candidates.append(("V", 0.82))

        # === 3B. 'L', 'Q', 'G', 'H' (Single/Double finger with extended thumb or horizontal) ===
        # 'Q' (Downward 'G': Index and Thumb pointing straight downward parallel to each other)
        elif index_extended_down and pts[4][1] > pts[1][1] and not middle_up and not ring_up and not pinky_up and not middle_extended_down:
            candidates.append(("Q", 0.95))
            candidates.append(("G", 0.80))
            candidates.append(("P", 0.75))

        # 'L' (Thumb and Index UP at 90 deg right angle, Middle/Ring/Pinky curled into fist)
        elif thumb_extended and index_up and not middle_up and not ring_up and not pinky_up and not middle_extended_down:
            if d_t4_t8 > 0.35:
                candidates.append(("L", 0.96))
                candidates.append(("D", 0.85))
            else:
                candidates.append(("D", 0.90))
                candidates.append(("L", 0.85))

        # 'G' (Index and Thumb pointing horizontally sideways parallel, other fingers curled)
        elif index_horizontal and not index_hooked and not middle_horizontal and not middle_up and not ring_up and not pinky_up:
            candidates.append(("G", 0.95))
            candidates.append(("H", 0.80))
            candidates.append(("Q", 0.75))

        # 'H' (Index and Middle fingers pointing horizontally sideways parallel together)
        elif index_horizontal and middle_horizontal and not ring_up and not pinky_up:
            candidates.append(("H", 0.95))
            candidates.append(("G", 0.82))

        # === 3C. 'X', 'D', '1' (Single index digit variations) ===
        # 'X' (Index finger hooked/bent at middle PIP joint, remaining fingers curled)
        elif index_hooked and not middle_up and not ring_up and not pinky_up:
            candidates.append(("X", 0.95))
            candidates.append(("D", 0.78))
            candidates.append(("1", 0.75))

        # 'D' vs '1' (Single upright index finger)
        elif index_up and not middle_up and not ring_up and not pinky_up and not thumb_extended and not middle_extended_down:
            if d_t4_t12 < 0.32 or d_t4_t16 < 0.35:
                candidates.append(("D", 0.96))
                candidates.append(("1", 0.88))
            else:
                candidates.append(("1", 0.95))
                candidates.append(("D", 0.88))

        # === 3D. 'I LOVE YOU', 'Y', 'I', 'J' (Pinky extended families) ===
        # 'I LOVE YOU' (Thumb, Index, Pinky UP simultaneously, Middle & Ring DOWN)
        elif thumb_extended and index_up and pinky_up and not middle_up and not ring_up:
            candidates.append(("I LOVE YOU", 0.97))
            candidates.append(("Y", 0.82))

        # 'Y' (Thumb and Pinky extended wide in opposite directions, Index/Middle/Ring curled)
        elif thumb_extended and pinky_up and not index_up and not middle_up and not ring_up:
            candidates.append(("Y", 0.96))
            candidates.append(("I LOVE YOU", 0.80))

        # 'I' and 'J' static base (Pinky UP only, Thumb folded across curled fingers)
        elif pinky_up and not index_up and not middle_up and not ring_up and not thumb_extended:
            candidates.append(("I", 0.96))
            candidates.append(("J", 0.82))  # Static candidate for J

        # === 3E. 'V', 'PEACE', 'U', 'R', '2' (Two upright fingers: Index + Middle) ===
        elif index_up and middle_up and not ring_up and not pinky_up and not middle_extended_down:
            # Crossed fingers test for 'R'
            is_crossed = (pts[8][0] > pts[12][0] + 0.01) if handedness == "Right" else (pts[8][0] < pts[12][0] - 0.01)
            if is_crossed:
                candidates.append(("R", 0.95))
                candidates.append(("U", 0.85))
                candidates.append(("V", 0.80))
            elif d_t8_t12 < 0.16:
                # 'U' (Index and Middle pressed tightly together side-by-side)
                candidates.append(("U", 0.95))
                candidates.append(("V", 0.82))
                candidates.append(("2", 0.80))
            else:
                # 'V' / 'PEACE' / '2' (Index and Middle spread apart in 'V')
                candidates.append(("V", 0.95))
                candidates.append(("PEACE", 0.94))
                candidates.append(("2", 0.92))
                candidates.append(("U", 0.82))

        # === 3F. 'W', '3' (Three upright fingers: Index, Middle, Ring) ===
        elif index_up and middle_up and ring_up and not pinky_up:
            candidates.append(("W", 0.95))
            candidates.append(("3", 0.92))

        elif thumb_extended and index_up and middle_up and not ring_up and not pinky_up:
            candidates.append(("3", 0.95))
            candidates.append(("W", 0.86))

        # === 3G. PINCH & LOOP GESTURES: 'F', 'OKAY', '9', 'O', 'C' ===
        elif d_t4_t8 < 0.26:
            if middle_up and ring_up and pinky_up:
                candidates.append(("F", 0.96))
                candidates.append(("OKAY", 0.95))
                candidates.append(("9", 0.92))
            elif not middle_up and not ring_up and not pinky_up:
                candidates.append(("O", 0.95))
                candidates.append(("0", 0.92))
                candidates.append(("C", 0.82))

        elif 0.26 <= d_t4_t8 < 0.52 and not index_up and not middle_up and not ring_up and not pinky_up and not index_extended_down and not middle_extended_down:
            # 'C' (Smooth open arc between curved fingers and thumb)
            candidates.append(("C", 0.94))
            candidates.append(("O", 0.85))

        # === 3H. FOUR OR FIVE FINGERS UP: 'B', '4', '5', 'STOP', 'THANK YOU', 'HELLO', 'PLEASE' ===
        elif index_up and middle_up and ring_up and pinky_up:
            if thumb_extended or d_t4_mcp5 > 0.38:
                if palm_facing_camera:
                    candidates.append(("STOP", 0.95))
                candidates.append(("5", 0.90))
                candidates.append(("THANK YOU", 0.75))
                candidates.append(("HELLO", 0.70))
                candidates.append(("PLEASE", 0.65))
            else:
                if d_t8_t12 < 0.15 and d_t12_t16 < 0.15:
                    candidates.append(("B", 0.96))
                    candidates.append(("4", 0.88))
                else:
                    candidates.append(("4", 0.94))
                    candidates.append(("B", 0.88))

        # === 3I. FIST FAMILY: 'A', 'S', 'E', 'T', 'M', 'N', 'THUMBS UP', 'THUMBS DOWN', 'YES' ===
        elif not index_up and not middle_up and not ring_up and not pinky_up:
            if thumb_high_up:
                candidates.append(("THUMBS UP", 0.97))
                candidates.append(("YES", 0.75))
            elif pts[4][1] > pts[0][1] + 0.12 and thumb_extended and not index_extended_down:
                candidates.append(("THUMBS DOWN", 0.96))
            else:
                # Disambiguate closed fist letters based on thumb placement:
                is_lateral = (pts[4][0] <= pts[5][0] + 0.02) if handedness == "Right" else (pts[4][0] >= pts[5][0] - 0.02)

                # 'E': Fingertips resting directly on folded thumb pad
                if (d_t4_t8 < 0.65 and d_t4_t12 < 0.65) and pts[4][1] >= pts[2][1] - 0.05 and not is_lateral:
                    candidates.append(("E", 0.95))
                    candidates.append(("S", 0.82))
                    candidates.append(("A", 0.80))
                # 'T': Thumb tucked poking up between index (5) and middle (9) knuckles
                elif d_t4_mcp5 < 0.28 and d_t4_mcp9 < 0.28 and pts[4][1] < pts[5][1] + 0.01:
                    candidates.append(("T", 0.95))
                    candidates.append(("S", 0.82))
                    candidates.append(("A", 0.80))
                # 'N': Thumb tucked under 2 fingers (pokes up between middle 9 and ring 13 knuckles)
                elif d_t4_mcp9 < 0.32 and d_t4_mcp13 < 0.35 and pts[4][1] < pts[9][1] + 0.01:
                    candidates.append(("N", 0.94))
                    candidates.append(("M", 0.85))
                    candidates.append(("T", 0.82))
                # 'M': Thumb tucked under 3 fingers (reaches across to ring 13 / pinky 17 knuckle, poking up)
                elif (d_t4_mcp13 < 0.35 or d_t4_mcp17 < 0.48) and pts[4][1] < pts[13][1] + 0.01:
                    candidates.append(("M", 0.94))
                    candidates.append(("N", 0.85))
                    candidates.append(("S", 0.80))
                # 'A': Thumb vertical along outer lateral edge of index knuckle (pointing up)
                elif ((pts[4][0] <= pts[5][0] + 0.02) if handedness == "Right" else (pts[4][0] >= pts[5][0] - 0.02)) and pts[4][1] < pts[5][1] + 0.01 and pts[4][1] < pts[2][1]:
                    candidates.append(("A", 0.95))
                    candidates.append(("S", 0.85))
                    candidates.append(("YES", 0.70))
                # 'S': Thumb wrapped horizontally across front of middle knuckles
                else:
                    candidates.append(("S", 0.94))
                    candidates.append(("A", 0.84))
                    candidates.append(("YES", 0.70))

        # Fallback catch-all
        if not candidates:
            up_count = sum([index_up, middle_up, ring_up, pinky_up])
            if up_count >= 4:
                candidates.append(("B", 0.75))
                candidates.append(("STOP", 0.70))
            elif up_count == 0:
                candidates.append(("A", 0.75))
                candidates.append(("S", 0.70))
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
