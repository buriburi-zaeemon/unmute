"""
Feature Engineering module for robust ASL Sign Language Recognition.
Computes scale-, position-, and rotation-invariant geometric features from 21 3D hand landmarks.
Transforms landmarks into a local palm coordinate system (orthonormal basis) for maximum invariance.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import numpy as np


@dataclass
class HandFeatures:
    normalized_landmarks: np.ndarray  # (21, 3) relative to wrist and scaled
    local_landmarks: np.ndarray  # (21, 3) in local palm coordinate frame (X=knuckles, Y=palm, Z=normal)
    joint_angles: List[float]  # 15 joint angles in degrees [0..180]
    finger_extensions: List[float]  # 5 floats [0.0 = curled/fist, 1.0 = fully extended]
    fingertip_distances: Dict[str, float]  # Normalized distances between fingertip pairs
    thumb_position: Dict[str, float]  # Detailed thumb position relative to knuckles & fingers
    palm_orientation: Dict[str, float]  # Palm normal, pointing direction, roll/pitch
    feature_vector: np.ndarray  # Flattened 1D feature vector for ML classifiers


class FeatureEngineer:
    """Extracts rotation-invariant and scale-invariant geometric features from hand landmarks."""

    @staticmethod
    def _compute_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate joint angle at p2 in degrees (0 to 180)."""
        v1 = p1 - p2
        v2 = p3 - p2
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 < 1e-6 or norm2 < 1e-6:
            return 180.0
        cos_angle = np.dot(v1, v2) / (norm1 * norm2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return float(np.degrees(np.arccos(cos_angle)))

    @staticmethod
    def _distance(p1: np.ndarray, p2: np.ndarray) -> float:
        return float(np.linalg.norm(p1 - p2))

    def extract_features(self, landmarks_raw: List[Tuple[float, float, float]]) -> HandFeatures:
        """
        Transforms raw 21 landmarks into rotation- and scale-invariant geometric features.
        """
        pts = np.array(landmarks_raw, dtype=np.float32)  # (21, 3)

        # 1. Translation: Wrist is origin (0, 0, 0)
        wrist = pts[0]
        pts_centered = pts - wrist

        # 2. Scale: Normalized by palm length (wrist 0 to middle MCP 9)
        palm_scale = float(np.linalg.norm(pts_centered[9]))
        if palm_scale < 1e-4:
            palm_scale = 1.0
        pts_norm = pts_centered / palm_scale

        # 3. Local Palm Coordinate Frame (Orthonormal Basis):
        # Y-axis (longitudinal): from wrist (0) to middle MCP (9)
        y_axis = pts_norm[9].copy()
        y_norm = np.linalg.norm(y_axis)
        y_axis = y_axis / (y_norm if y_norm > 1e-6 else 1.0)

        # Vector across knuckles: from index MCP (5) to pinky MCP (17)
        v_knuckles = pts_norm[17] - pts_norm[5]

        # Z-axis (palm normal): cross product of Y-axis and knuckle vector
        z_axis = np.cross(y_axis, v_knuckles)
        z_norm = np.linalg.norm(z_axis)
        z_axis = z_axis / (z_norm if z_norm > 1e-6 else 1.0)

        # X-axis (lateral): cross product of Y and Z
        x_axis = np.cross(y_axis, z_axis)
        x_norm = np.linalg.norm(x_axis)
        x_axis = x_axis / (x_norm if x_norm > 1e-6 else 1.0)

        # Transformation matrix to local palm frame (3, 3)
        R_palm = np.vstack([x_axis, y_axis, z_axis])  # rows are basis vectors
        pts_local = np.dot(pts_norm, R_palm.T)  # (21, 3) in local frame

        # 4. Joint Angles (15 angles)
        finger_triplets = [
            [(0, 1, 2), (1, 2, 3), (2, 3, 4)],        # Thumb
            [(0, 5, 6), (5, 6, 7), (6, 7, 8)],        # Index
            [(0, 9, 10), (9, 10, 11), (10, 11, 12)],  # Middle
            [(0, 13, 14), (13, 14, 15), (14, 15, 16)], # Ring
            [(0, 17, 18), (17, 18, 19), (18, 19, 20)]  # Pinky
        ]

        joint_angles: List[float] = []
        for f_triplets in finger_triplets:
            for p1_i, p2_i, p3_i in f_triplets:
                ang = self._compute_angle(pts_norm[p1_i], pts_norm[p2_i], pts_norm[p3_i])
                joint_angles.append(ang)

        # 5. Robust Finger Extension States [0.0 = curled/fist, 1.0 = extended]
        finger_extensions: List[float] = []

        # Thumb extension:
        # Distance from thumb tip (4) to pinky MCP (17) and distance to index MCP (5) in local plane
        dist_t4_to_mcp17 = float(self._distance(pts_local[4], pts_local[17]))
        dist_t4_to_mcp5 = float(self._distance(pts_local[4], pts_local[5]))
        thumb_abduction = dist_t4_to_mcp5
        thumb_ext = np.clip((dist_t4_to_mcp17 - 0.45) / 0.55, 0.0, 1.0)
        finger_extensions.append(float(thumb_ext))

        # Index (8), Middle (12), Ring (16), Pinky (20):
        # In local palm coordinates, Y goes from wrist (0) to knuckles (1.0).
        # An extended finger has tip Y >> PIP Y and PIP angle > 130°.
        finger_indices = [
            (8, 7, 6, 5, 1),   # Index: tip, dip, pip, mcp, triplet_offset
            (12, 11, 10, 9, 4),# Middle
            (16, 15, 14, 13, 7),# Ring
            (20, 19, 18, 17, 10)# Pinky
        ]

        for tip_i, dip_i, pip_i, mcp_i, angle_idx in finger_indices:
            # Tip Y relative to MCP Y in local palm frame
            tip_y = pts_local[tip_i][1]
            pip_y = pts_local[pip_i][1]
            mcp_y = pts_local[mcp_i][1]

            # PIP angle: straight finger is ~160°-180°, bent is ~40°-90°
            pip_angle = joint_angles[angle_idx + 1]
            angle_factor = np.clip((pip_angle - 80.0) / 75.0, 0.0, 1.0)

            # Height factor: tip extends beyond MCP
            height_factor = np.clip((tip_y - mcp_y) / 0.5, 0.0, 1.0)

            # Overall extension score (0.0 to 1.0)
            ext_score = float(0.6 * height_factor + 0.4 * angle_factor)
            finger_extensions.append(np.clip(ext_score, 0.0, 1.0))

        # 6. Pairwise Fingertip & Knuckle Distances in local frame
        fingertip_distances = {
            "thumb_index": float(self._distance(pts_local[4], pts_local[8])),
            "thumb_middle": float(self._distance(pts_local[4], pts_local[12])),
            "thumb_ring": float(self._distance(pts_local[4], pts_local[16])),
            "thumb_pinky": float(self._distance(pts_local[4], pts_local[20])),
            "index_middle": float(self._distance(pts_local[8], pts_local[12])),
            "middle_ring": float(self._distance(pts_local[12], pts_local[16])),
            "ring_pinky": float(self._distance(pts_local[16], pts_local[20])),
            "index_pinky": float(self._distance(pts_local[8], pts_local[20])),
            # Tip to respective MCP (curledness check)
            "index_tip_to_mcp": float(self._distance(pts_local[8], pts_local[5])),
            "middle_tip_to_mcp": float(self._distance(pts_local[12], pts_local[9])),
            "ring_tip_to_mcp": float(self._distance(pts_local[16], pts_local[13])),
            "pinky_tip_to_mcp": float(self._distance(pts_local[20], pts_local[17])),
            # Thumb tip to index/middle PIP joints (fist classification)
            "thumb_to_index_pip": float(self._distance(pts_local[4], pts_local[6])),
            "thumb_to_middle_pip": float(self._distance(pts_local[4], pts_local[10])),
            "thumb_to_ring_pip": float(self._distance(pts_local[4], pts_local[14])),
        }

        # 7. Thumb Position Details in Local Coordinate Frame
        thumb_position = {
            "thumb_x": float(pts_local[4][0]),
            "thumb_y": float(pts_local[4][1]),
            "thumb_z": float(pts_local[4][2]),
            # Relative lateral offset from index knuckle (X_4 - X_5)
            "thumb_offset_index_x": float(pts_local[4][0] - pts_local[5][0]),
            "thumb_offset_middle_x": float(pts_local[4][0] - pts_local[9][0]),
            # Relative height vs index knuckle
            "thumb_height_vs_index_mcp": float(pts_local[4][1] - pts_local[5][1]),
            "thumb_height_vs_index_tip": float(pts_local[4][1] - pts_local[8][1]),
            "thumb_abduction": float(thumb_abduction),
        }

        # 8. Palm Orientation in World/Camera Space
        palm_orientation = {
            "normal_x": float(z_axis[0]),
            "normal_y": float(z_axis[1]),
            "normal_z": float(z_axis[2]),
            "pointing_up": float(y_axis[1] < -0.3),   # Y points up on screen (negative in pixel coords)
            "pointing_down": float(y_axis[1] > 0.3),
            "pointing_side": float(abs(y_axis[0]) > abs(y_axis[1])),
            "facing_camera": float(z_axis[2] < -0.3),
        }

        # 9. Assemble 1D Feature Vector
        flat_local = pts_local.flatten()  # 63
        flat_angles = np.array(joint_angles, dtype=np.float32) / 180.0  # 15
        flat_ext = np.array(finger_extensions, dtype=np.float32)  # 5
        flat_dist = np.array(list(fingertip_distances.values()), dtype=np.float32)  # 15
        flat_thumb = np.array(list(thumb_position.values()), dtype=np.float32)  # 8
        flat_palm = np.array([z_axis[0], z_axis[1], z_axis[2]], dtype=np.float32)  # 3

        feature_vector = np.concatenate([
            flat_local,
            flat_angles,
            flat_ext,
            flat_dist,
            flat_thumb,
            flat_palm
        ])

        return HandFeatures(
            normalized_landmarks=pts_norm,
            local_landmarks=pts_local,
            joint_angles=joint_angles,
            finger_extensions=finger_extensions,
            fingertip_distances=fingertip_distances,
            thumb_position=thumb_position,
            palm_orientation=palm_orientation,
            feature_vector=feature_vector,
        )
