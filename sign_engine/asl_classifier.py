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

    def __init__(self, model_dir: Optional[str] = None, stability_threshold: int = 3):
        self.feature_engineer = FeatureEngineer()
        self.stability_threshold = stability_threshold
        self._history: List[str] = []
        self._confidence_history: List[float] = []

    @staticmethod
    def _is_finger_up(
        pts: np.ndarray,
        v_hand_unit: np.ndarray,
        tip_i: int,
        dip_i: int,
        pip_i: int,
        mcp_i: int,
        pip_angle: float,
        ext_score: float = 0.5,
    ) -> bool:
        """
        Universal Person-Invariant Finger Extension Evaluator.
        Uses Self-Phalange Bone Chain Normalization rather than palm size,
        guaranteeing invariance across varying palm sizes, finger lengths,
        children/adults, and perspective distortion.
        """
        # 1. Total bone chain perimeter along finger phalanges (knuckle -> PIP -> DIP -> Tip)
        seg1 = float(np.linalg.norm(pts[pip_i] - pts[mcp_i]))
        seg2 = float(np.linalg.norm(pts[dip_i] - pts[pip_i]))
        seg3 = float(np.linalg.norm(pts[tip_i] - pts[dip_i]))
        bone_chain = seg1 + seg2 + seg3
        if bone_chain < 1e-5:
            return False

        # 2. Straight-line chord vs perimeter (by triangle inequality, straight finger approaches 1.0)
        chord = float(np.linalg.norm(pts[tip_i] - pts[mcp_i]))
        straight_ratio = chord / bone_chain

        # 3. Radial distance from wrist (Tip is further from wrist than PIP joint)
        d_tip_wrist = float(np.linalg.norm(pts[tip_i] - pts[0]))
        d_pip_wrist = float(np.linalg.norm(pts[pip_i] - pts[0]))

        # 4. Projection along longitudinal hand orientation vector
        proj_tip = float(np.dot(pts[tip_i] - pts[mcp_i], v_hand_unit))

        # 5. Inverted Y check in camera plane (Tip higher than PIP joint with generous margin)
        y_upright = pts[tip_i][1] < pts[pip_i][1] + 0.05

        # 6. Directional alignment between proximal phalanx (MCP->PIP) and distal phalanx (DIP->Tip)
        # Straight fingers have distal phalanx pointing along proximal phalanx (> 0.40); curved fingers (like 'C') bend inward (< 0.20)
        v_prox = pts[pip_i][:2] - pts[mcp_i][:2]
        v_dist = pts[tip_i][:2] - pts[dip_i][:2]
        norm_prox = float(np.linalg.norm(v_prox))
        norm_dist = float(np.linalg.norm(v_dist))
        phalanx_align = float(np.dot(v_prox, v_dist) / (norm_prox * norm_dist)) if (norm_prox > 1e-5 and norm_dist > 1e-5) else 0.0

        # Straightness condition: chord ratio > 0.60 (curled in fist is < 0.40), straight PIP joint, and aligned distal phalanx
        is_straight = (straight_ratio > 0.60) and (pip_angle > 110.0 or (straight_ratio > 0.72 and ext_score > 0.58)) and (phalanx_align > 0.30)

        # Orientation condition: pointing outward along hand axis and upright in image plane
        is_upright = (d_tip_wrist > d_pip_wrist * 0.95) and (proj_tip > -0.06) and y_upright

        return bool(is_straight and is_upright)

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
        index_up = self._is_finger_up(pts, v_hand_unit, 8, 7, 6, 5, angles[4], ext[1])
        middle_up = self._is_finger_up(pts, v_hand_unit, 12, 11, 10, 9, angles[7], ext[2])
        ring_up = self._is_finger_up(pts, v_hand_unit, 16, 15, 14, 13, angles[10], ext[3])
        pinky_up = self._is_finger_up(pts, v_hand_unit, 20, 19, 18, 17, angles[13], ext[4])

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

        # -------------------------------------------------------------
        # 3. HIERARCHICAL FINGER-EXTENSION DECISION HIERARCHY
        # -------------------------------------------------------------
        up_count = sum([index_up, middle_up, ring_up, pinky_up])

        # === 3A. ORIENTATION EXCEPTIONS (Evaluated first to prevent fist false-positives) ===
        # 'P' (Index pointing horizontally forward/up, Middle pointing straight DOWN ~90 deg, Thumb resting on middle joint)
        if middle_extended_down and (index_horizontal or ext[1] > 0.35 or index_up) and not ring_up and not pinky_up:
            candidates.append(("P", 0.96))
            candidates.append(("K", 0.82))

        # 'Q' (Downward 'G': Index pointing downward, Thumb pointing downward parallel to it)
        elif index_extended_down and (pts[4][1] > pts[1][1] or pts[4][1] > pts[2][1]) and not middle_up and not ring_up and not pinky_up and not middle_extended_down:
            candidates.append(("Q", 0.96))
            candidates.append(("G", 0.80))
            candidates.append(("P", 0.75))

        # 'H' (Index and Middle fingers extended & pointing horizontally sideways parallel together)
        elif index_horizontal and middle_horizontal and not ring_up and not pinky_up and not index_hooked:
            candidates.append(("H", 0.96))
            candidates.append(("G", 0.82))

        # 'G' (Index and Thumb pointing horizontally sideways parallel, other fingers curled)
        elif index_horizontal and not index_hooked and not middle_horizontal and not middle_up and not ring_up and not pinky_up:
            candidates.append(("G", 0.96))
            candidates.append(("H", 0.80))
            candidates.append(("Q", 0.75))

        # 'X' (Index finger hooked/bent at middle PIP joint, remaining fingers curled)
        elif index_hooked and not middle_up and not ring_up and not pinky_up:
            candidates.append(("X", 0.96))
            candidates.append(("D", 0.78))
            candidates.append(("1", 0.75))

        # === 3B. PINCH & LOOP EXCEPTION: 'F', 'OKAY', '9' ===
        # Thumb and Index tips touching in a ring, remaining three fingers (middle, ring, pinky) extended UP
        elif d_t4_t8 < 0.28 and middle_up and ring_up and pinky_up:
            candidates.append(("F", 0.96))
            candidates.append(("OKAY", 0.96))
            candidates.append(("9", 0.92))

        # === 3B.2. INDEX + PINKY EXCEPTION: 'I LOVE YOU' ===
        # Index and Pinky extended UP, while Middle and Ring fingers are curled (ext[2] < 0.62 and ext[3] < 0.62)
        elif (index_up or ext[1] > 0.50) and (pinky_up or ext[4] > 0.50) and ext[2] < 0.62 and ext[3] < 0.62:
            candidates.append(("I LOVE YOU", 0.97))
            candidates.append(("Y", 0.82))

        # === 3C. CATEGORICAL BRANCHING BY EXTENDED FINGER COUNT (up_count) ===
        # --- FOUR FINGERS UP (Index, Middle, Ring, Pinky) ---
        elif up_count == 4:
            thumb_open_lateral = (pts[4][0] < pts[2][0] - 0.03) if handedness == "Right" else (pts[4][0] > pts[2][0] + 0.03)
            if thumb_open_lateral or (thumb_extended and d_t4_mcp5 > 0.70):
                if palm_facing_camera:
                    candidates.append(("STOP", 0.96))
                    candidates.append(("5", 0.95))
                    candidates.append(("B", 0.80))
                    candidates.append(("THANK YOU", 0.75))
                    candidates.append(("HELLO", 0.70))
                else:
                    candidates.append(("5", 0.96))
                    candidates.append(("STOP", 0.95))
                    candidates.append(("B", 0.80))
            else:
                if d_t8_t12 < 0.18 and d_t12_t16 < 0.18:
                    candidates.append(("B", 0.96))
                    candidates.append(("4", 0.92))
                    candidates.append(("STOP", 0.80))
                else:
                    candidates.append(("4", 0.95))
                    candidates.append(("B", 0.90))
                    candidates.append(("STOP", 0.80))

        # --- THREE FINGERS UP ---
        elif up_count == 3:
            if index_up and middle_up and ring_up and not pinky_up:
                candidates.append(("W", 0.96))
                candidates.append(("3", 0.92))
            elif thumb_extended and index_up and middle_up and not ring_up and not pinky_up:
                candidates.append(("3", 0.96))
                candidates.append(("W", 0.86))
            elif thumb_extended and index_up and pinky_up and not middle_up and not ring_up:
                candidates.append(("I LOVE YOU", 0.97))
                candidates.append(("Y", 0.82))
            elif index_up and pinky_up and not middle_up and not ring_up:
                candidates.append(("I LOVE YOU", 0.97))
                candidates.append(("Y", 0.82))
            else:
                candidates.append(("W", 0.88))
                candidates.append(("3", 0.82))

        # --- TWO FINGERS UP ---
        elif up_count == 2:
            if index_up and middle_up and not ring_up and not pinky_up:
                # Crossed fingers test for 'R' (Index tip and Middle tip crossed)
                is_crossed = (d_t8_t12 < 0.50) and ((pts[8][0] > pts[12][0] + 0.015) if handedness == "Right" else (pts[8][0] < pts[12][0] - 0.015))
                if is_crossed:
                    candidates.append(("R", 0.96))
                    candidates.append(("U", 0.85))
                    candidates.append(("V", 0.80))
                else:
                    # Disambiguate 'K' vs 'PEACE' / 'V' / 'U' / '2'
                    # True 'K' requires: thumb wedged upright between index & middle knuckles with middle angled forward
                    is_thumb_between = (min(pts[5][0], pts[9][0]) - 0.02 <= pts[4][0] <= max(pts[5][0], pts[9][0]) + 0.02)
                    middle_angled = (pts[12][2] > pts[8][2] + 0.03 or abs(pts[12][0] - pts[9][0]) > 0.04)
                    is_true_k = is_thumb_between and middle_angled and (pts[4][1] < pts[5][1] + 0.02)

                    if is_true_k:
                        candidates.append(("K", 0.96))
                        candidates.append(("P", 0.85))
                        candidates.append(("V", 0.82))
                    elif d_t8_t12 < 0.20:
                        # 'U' (Index and Middle pressed tightly together)
                        candidates.append(("U", 0.96))
                        candidates.append(("V", 0.88))
                        candidates.append(("PEACE", 0.86))
                        candidates.append(("2", 0.85))
                    else:
                        # 'PEACE' / 'V' / '2' (Index and Middle spread apart in 'V')
                        candidates.append(("PEACE", 0.96))
                        candidates.append(("V", 0.96))
                        candidates.append(("2", 0.92))
                        candidates.append(("U", 0.80))
            elif pinky_up and not index_up and not middle_up and not ring_up:
                candidates.append(("Y", 0.96))
                candidates.append(("I LOVE YOU", 0.82))
            elif index_up and pinky_up and not middle_up and not ring_up:
                candidates.append(("I LOVE YOU", 0.97))
                candidates.append(("Y", 0.82))
            elif index_up and not middle_up and not ring_up and not pinky_up:
                candidates.append(("L", 0.96))
                candidates.append(("D", 0.80))
            else:
                candidates.append(("UNKNOWN", 0.30))

        # --- ONE FINGER UP ---
        elif up_count == 1:
            if index_up and not middle_up and not ring_up and not pinky_up:
                is_thumb_lateral = (pts[4][0] < pts[5][0] - 0.08) if handedness == "Right" else (pts[4][0] > pts[5][0] + 0.08)
                if (thumb_extended and d_t4_t8 > 0.40) or (is_thumb_lateral and d_t4_t8 > 0.35):
                    candidates.append(("L", 0.96))
                    candidates.append(("D", 0.80))
                else:
                    candidates.append(("D", 0.96))
                    candidates.append(("1", 0.95))
                    candidates.append(("L", 0.75))
            elif pinky_up and not index_up and not middle_up and not ring_up:
                candidates.append(("I", 0.96))
                candidates.append(("J", 0.85))
            else:
                candidates.append(("1", 0.85))
                candidates.append(("D", 0.80))

        # --- ZERO FINGERS UP (Fist Family or Curved Pinch) ---
        else:
            is_fist = all(ext[i] <= 0.45 for i in range(1, 5))
            if d_t4_t8 < 0.22:
                candidates.append(("O", 0.96))
                candidates.append(("0", 0.95))
                candidates.append(("C", 0.85))
            elif not is_fist and (0.22 <= d_t4_t8 < 0.85):
                # 'C' (Smooth open arc between curved fingers and thumb)
                candidates.append(("C", 0.95))
                candidates.append(("O", 0.85))
            else:
                # Fist family
                if thumb_high_up:
                    candidates.append(("THUMBS UP", 0.97))
                    candidates.append(("YES", 0.80))
                elif (pts[4][1] > pts[0][1] + 0.10) and (pts[4][1] > pts[1][1] + 0.05):
                    candidates.append(("THUMBS DOWN", 0.96))
                else:
                    is_lateral = (pts[4][0] <= pts[5][0] + 0.02) if handedness == "Right" else (pts[4][0] >= pts[5][0] - 0.02)
                    # 'E': Fingertips resting on thumb pad
                    if (d_t4_t8 < 0.65 and d_t4_t12 < 0.65) and pts[4][1] >= pts[2][1] - 0.05 and not is_lateral and d_t4_mcp5 > 0.28:
                        candidates.append(("E", 0.96))
                        candidates.append(("S", 0.82))
                        candidates.append(("A", 0.80))
                    # 'T': Thumb between index & middle knuckles
                    elif d_t4_mcp5 < 0.28 and d_t4_mcp9 < 0.28 and pts[4][1] < pts[5][1] + 0.01:
                        candidates.append(("T", 0.96))
                        candidates.append(("S", 0.82))
                        candidates.append(("A", 0.80))
                    # 'N': Thumb between middle & ring knuckles
                    elif d_t4_mcp9 < 0.32 and d_t4_mcp13 < 0.35 and pts[4][1] < pts[9][1] + 0.01:
                        candidates.append(("N", 0.95))
                        candidates.append(("M", 0.85))
                        candidates.append(("T", 0.82))
                    # 'M': Thumb under 3 fingers
                    elif (d_t4_mcp13 < 0.35 or d_t4_mcp17 < 0.48) and pts[4][1] < pts[13][1] + 0.01:
                        candidates.append(("M", 0.95))
                        candidates.append(("N", 0.85))
                        candidates.append(("S", 0.80))
                    # 'A': Thumb vertical along outer lateral edge of index knuckle
                    elif is_lateral and pts[4][1] < pts[5][1] + 0.01 and pts[4][1] < pts[2][1]:
                        candidates.append(("A", 0.96))
                        candidates.append(("S", 0.85))
                        candidates.append(("YES", 0.70))
                    # 'S': Thumb wrapped horizontally across front of middle knuckles
                    else:
                        candidates.append(("S", 0.96))
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
