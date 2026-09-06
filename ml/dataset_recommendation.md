# UNMUTE — Contributor 1: Dataset Recommendation & Controlled Vocabulary Strategy

**Author:** Contributor 1 (ML Foundation and Static Recognition)  
**Status:** Approved & Finalized (Week 1 Deliverable)  
**Scope:** American Sign Language (ASL) Static Recognition Pipeline

---

## 1. Executive Summary & Scope

UNMUTE is an assistive AI translator converting real-time American Sign Language (ASL) into English speech and captions. The machine learning pipeline is structured into two complementary recognition subsystems:
1. **Static Sign Recognition (Contributor 1)**: Single-frame posture recognition converting 21 3D MediaPipe hand landmarks into a 109-dimensional geometric feature representation, classified by a lightweight PyTorch Multi-Layer Perceptron (MLP).
2. **Dynamic Sign Recognition (Contributor 2)**: Temporal sequence tracking analyzing multi-frame trajectories (motion vectors, wrist displacement, temporal LSTM) for kinetic signs and phrases.

This document establishes the official dataset selection, controlled vocabulary boundaries, zero-leakage data partitioning strategy, and an authoritative anatomical definition catalog for every sign in the UNMUTE dictionary.

---

## 2. Investigation of Candidate Datasets

| Criterion | **ASL Alphabet Dataset (Recommended)** | **Sign Language MNIST (Rejected)** | **WLASL / MS-ASL (Rejected for Static)** |
| :--- | :--- | :--- | :--- |
| **Source & Author** | Akash Nagaraj (Kaggle) | Modified MNIST Benchmark | Li et al. / VGG Group |
| **Format** | 87,000 RGB images (200×200 px) | 28×28 Grayscale CSV matrices | 2,000+ Raw video clips (MP4) |
| **Sign Language** | ASL (American Sign Language) | ASL Fingerspelling | ASL Word-Level |
| **MediaPipe Compatibility** | **High (>96% landmark detection)** | **0% (Incompatible; resolution too low)** | Medium (Requires video decoding & frame slicing) |
| **Signer Diversity** | Multiple signers, varied angles & lighting | Synthetic cropped pixel maps | High (YouTube crowdsourced) |
| **Sign Dynamics** | Static single-frame handshapes | Static 28x28 crops | Continuous & dynamic motion |
| **Licensing** | CC0: Public Domain | CC0: Public Domain | Academic Research Only |
| **Suitability for Scope** | **Ideal for semester-scale static baseline** | Unusable with computer vision pipelines | Belongs to Contributor 2 (Dynamic LSTM) |

### Justification for ASL Alphabet Dataset
* **MediaPipe Landmark Fidelity**: MediaPipe Hand Landmarker requires clean color images with sufficient pixel resolution to accurately identify 21 3D joint coordinates. The 200×200 RGB frames provide sharp finger edges and joint separation.
* **Controlled Static Vocabulary**: Perfectly aligns with the static letters and provides clean, isolated postures without motion blur.
* **Storage & Training Efficiency**: Preprocessing extracts 109 floats per sample, condensing 87,000 images into a compact ~38 MB `.npz` archive. This enables sub-second epoch training on modern GPUs/CPUs.

---

## 3. UNMUTE Controlled Vocabulary Specification (36 Classes)

To ensure high accuracy and real-time reliability for a student capstone and viva evaluation, UNMUTE adopts a strictly defined **36-class controlled static vocabulary**:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      UNMUTE STATIC VOCABULARY (36 CLASSES)                       │
├───────────────────┬──────────────────────────────────┬──────────────────────────┤
│ Category          │ Count                            │ Classes                  │
├───────────────────┼──────────────────────────────────┼──────────────────────────┤
│ Alphabets (Static)│ 24 Classes                       │ A, B, C, D, E, F, G, H,  │
│                   │ (J and Z excluded as dynamic)    │ I, K, L, M, N, O, P, Q,  │
│                   │                                  │ R, S, T, U, V, W, X, Y   │
├───────────────────┼──────────────────────────────────┼──────────────────────────┤
│ Numbers           │ 5 Classes                        │ 1, 2, 3, 4, 5            │
├───────────────────┼──────────────────────────────────┼──────────────────────────┤
│ Static Phrases    │ 6 Classes                        │ I LOVE YOU, OKAY, PEACE, │
│                   │                                  │ STOP, THUMBS DOWN,       │
│                   │                                  │ THUMBS UP                │
├───────────────────┼──────────────────────────────────┼──────────────────────────┤
│ Control Gestures  │ 1 Class                          │ SPACE                    │
└───────────────────┴──────────────────────────────────┴──────────────────────────┘
```

### Dynamic Phrases & Letters (Contributor 2 Scope Interface)
The following signs require continuous motion tracking over time and are designated for Contributor 2's temporal tracker and dynamic LSTM:
* **Dynamic Letters**:
  * **J**: Starts from `I` handshape and traces a downward hook path with the pinky.
  * **Z**: Extends index finger and traces a 3-stroke zigzag in the air.
* **Dynamic Phrases**:
  * **HELLO**: Open palm begins near temple and waves/salutes forward and outward.
  * **THANK YOU**: Open palm begins at the chin/lips and extends outward toward recipient.
  * **YES**: Closed fist tilts/nods forward and back twice like a nodding head.
  * **NO**: Index and middle fingers snap downward onto the thumb pad.
  * **PLEASE**: Flat open palm executes circular rubbing motion over center of chest.

---

## 4. Authoritative Sign Definition Catalog

Every sign in UNMUTE is defined by strict anatomical handshape geometry, digit extension/flexion, and disambiguation criteria:

### A. Static Alphabets (A–Y, excluding dynamic J & Z)

#### Letter A
* **Anatomical Definition**: Closed fist with all four fingers (index, middle, ring, pinky) tightly curled into palm. The thumb remains fully extended upright along the outer lateral edge of the index finger knuckle (MCP).
* **Palm Orientation**: Facing forward toward the viewer/camera.
* **MediaPipe Landmarks**: Tips 8, 12, 16, 20 curled toward wrist (dist < 0.35 palm scale); thumb tip (4) elevated above index MCP (5).
* **Disambiguation**: Unlike **S**, the thumb is beside the fingers, not wrapped over the front. Unlike **T**, the thumb is not tucked between index and middle.

#### Letter B
* **Anatomical Definition**: All four fingers (index, middle, ring, pinky) extended straight upward, held tightly together with zero finger abduction. The thumb is folded flat horizontally across the lower center of the palm.
* **Palm Orientation**: Facing forward toward the viewer.
* **MediaPipe Landmarks**: Extensions for digits 1–4 are ~1.0; finger distances `index_middle`, `middle_ring`, `ring_pinky` < 0.15; thumb tip (4) folded inward across palm.
* **Disambiguation**: Differs from **4** because 4 spreads all four fingers wide and leaves the thumb tucked at the side.

#### Letter C
* **Anatomical Definition**: All four fingers and thumb curved into a smooth, continuous semicircular arc resembling an open cup or the letter "C". An open aperture remains between the thumb tip and fingertips.
* **Palm Orientation**: Facing sideways horizontally.
* **MediaPipe Landmarks**: Joint angles at PIP and DIP joints are moderately bent (90°–130°); distance between thumb tip (4) and index tip (8) is 0.35–0.60 palm scale.
* **Disambiguation**: Differs from **O** because fingertips and thumb tip do NOT touch.

#### Letter D
* **Anatomical Definition**: The index finger is extended straight upward. The middle, ring, and pinky fingers curl downward so their pads touch the pad of the thumb, forming a closed circular loop at the base.
* **Palm Orientation**: Facing forward or slightly angled sideways.
* **MediaPipe Landmarks**: Index extension ~1.0; middle, ring, pinky extensions < 0.3; distance `thumb_middle` and `thumb_ring` < 0.15.
* **Disambiguation**: Differs from **1** because in 1 the unused fingers are curled into a fist rather than forming a pinch loop with the thumb.

#### Letter E
* **Anatomical Definition**: All four fingers curl tightly downward at all joints so the fingertip pads rest directly on top of the tucked thumb pad, with knuckles prominently bent.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Extensions for all fingers < 0.15; thumb tucked horizontally underneath fingertips; thumb tip Y coordinate is lower than or equal to finger tips.
* **Disambiguation**: Differs from **S** and **A** by having finger pads resting on the thumb rather than curled into the palm.

#### Letter F
* **Anatomical Definition**: Tips of index finger and thumb touch together forming an open circular loop. Middle, ring, and pinky fingers are extended straight upward and spread slightly apart.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Distance `thumb_index` < 0.12 (pinch loop); extensions of middle, ring, pinky > 0.85.
* **Disambiguation**: Inverted counterpart of **D** (where only index is up). Identical handshape to number **9**.

#### Letter G
* **Anatomical Definition**: Index finger and thumb extend horizontally sideways parallel to each other, like a measuring caliper or gauge. Middle, ring, and pinky fingers are curled tightly into the palm.
* **Palm Orientation**: Knuckles facing outward; fingers pointing horizontally sideways across the body.
* **MediaPipe Landmarks**: Palm pointing side (`abs(y_axis[0]) > abs(y_axis[1])`); index extension > 0.8; distance `thumb_index` 0.20–0.45.
* **Disambiguation**: Differs from **H** because H extends both index AND middle fingers sideways.

#### Letter H
* **Anatomical Definition**: Index and middle fingers extended straight horizontally sideways pressed firmly together side-by-side. Ring and pinky are curled into palm; thumb is tucked flat across ring knuckle.
* **Palm Orientation**: Back of hand facing viewer; two fingers pointing sideways.
* **MediaPipe Landmarks**: Index and middle extended horizontally; distance `index_middle` < 0.12; palm pointing sideways.
* **Disambiguation**: Differs from **G** (1 finger) and **U** (points vertically up, not sideways).

#### Letter I
* **Anatomical Definition**: Pinky finger extended straight upward from a tightly closed fist. The thumb is folded horizontally across the middle joints of the curled index, middle, and ring fingers.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Pinky extension > 0.90; index, middle, ring extensions < 0.20.
* **Disambiguation**: Differs from **J** because I is strictly static (J requires tracing a hook in the air).

#### Letter K
* **Anatomical Definition**: Index finger extended vertically straight up. Middle finger extended forward angled upward at roughly 45°. Thumb is extended upward so its pad rests directly against the first knuckle (PIP joint) of the middle finger. Ring and pinky are curled into palm.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Index extension ~1.0; middle extension ~0.85; thumb tip (4) positioned between index MCP (5) and middle MCP (9) with Y elevation above knuckles.
* **Disambiguation**: Differs from **V** because V holds index and middle in the same plane with thumb folded over ring finger.

#### Letter L
* **Anatomical Definition**: Thumb and index finger extended fully at an unmistakable 90° perpendicular right angle, forming an "L" shape. Middle, ring, and pinky fingers remain curled tightly into palm.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Angle at index MCP between thumb tip (4) and index tip (8) is 80°–100°; index points up, thumb points horizontally lateral.
* **Disambiguation**: Highly distinctive right angle; one of the most reliable static classes.

#### Letter M
* **Anatomical Definition**: Index, middle, and ring fingers folded over the top of the tucked thumb so the thumb tip pokes out underneath the pinky knuckle. Three visible knuckle mounds are presented.
* **Palm Orientation**: Facing forward with knuckles angled slightly downward.
* **MediaPipe Landmarks**: Thumb tip (4) lateral X coordinate extends beyond ring MCP (13); three fingers drape over thumb.
* **Disambiguation**: Differs from **N** (which drapes only 2 fingers) and **T** (which drapes only 1 finger).

#### Letter N
* **Anatomical Definition**: Index and middle fingers folded over the top of the tucked thumb so the thumb tip pokes out between the middle and ring fingers. Two visible knuckle mounds are presented.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Thumb tip (4) rests between middle MCP (9) and ring MCP (13); two fingers drape over thumb.
* **Disambiguation**: Intermediate between **M** (3 fingers over thumb) and **T** (1 finger over thumb).

#### Letter O
* **Anatomical Definition**: All four fingers and thumb curve inward so all five fingertips meet and touch pad-to-pad, creating an enclosed round "O" circle.
* **Palm Orientation**: Facing forward or slightly angled sideways.
* **MediaPipe Landmarks**: Distance from thumb tip (4) to index tip (8) < 0.12; fingertips closely clustered; curvature angles bent.
* **Disambiguation**: Differs from **C** because in O the circle is fully closed with fingertips touching thumb.

#### Letter P
* **Anatomical Definition**: Hand oriented downward with wrist bent forward. Index finger points horizontally forward; middle finger extends straight downward at 90°. Thumb pad rests against middle finger PIP joint (downward K handshape).
* **Palm Orientation**: Pointing downward (`y_axis[1] > 0.3`).
* **MediaPipe Landmarks**: Palm orientation indicates downward pitch; index and middle extended downward/forward.
* **Disambiguation**: Downward oriented counterpart of **K**.

#### Letter Q
* **Anatomical Definition**: Index finger and thumb extend parallel pointing straight downward toward the ground. Middle, ring, and pinky fingers are curled into palm (downward G handshape).
* **Palm Orientation**: Pointing downward.
* **MediaPipe Landmarks**: Palm pointing down; index and thumb point downward with gap of 0.2–0.4 palm scale.
* **Disambiguation**: Downward oriented counterpart of **G**.

#### Letter R
* **Anatomical Definition**: Index and middle fingers extended straight upward and crossed tightly, with the index finger crossing over the front of the middle finger. Ring and pinky are curled; thumb folds over ring finger.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Index tip (8) and middle tip (12) are extended > 0.85; X-coordinates swap sign relative to normal hand symmetry (cross detected).
* **Disambiguation**: Crossed finger state is an explicit invariant feature in `FeatureEngineer`.

#### Letter S
* **Anatomical Definition**: Tight fist with all four fingers curled into palm, and the thumb folded horizontally across the front of the middle finger knuckles.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: All 4 finger extensions < 0.15; thumb pad rests across index and middle proximal phalanges (X offset centered over knuckles 5 and 9).
* **Disambiguation**: Crucial distinction: in **A**, thumb is at the side; in **S**, thumb wraps across the front; in **T**, thumb pokes between index and middle.

#### Letter T
* **Anatomical Definition**: Closed fist with the thumb tucked between the index and middle fingers, such that the thumb tip pokes upward between the first two knuckles.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Thumb tip (4) Y elevation sits between index MCP (5) and index PIP (6); thumb X lies between knuckles 5 and 9.
* **Disambiguation**: Differentiated by thumb insertion between digits 1 and 2.

#### Letter U
* **Anatomical Definition**: Index and middle fingers extended straight upward pressed firmly together side-by-side with zero gap. Ring and pinky are curled; thumb folds across ring finger.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Index and middle extensions > 0.90; distance `index_middle` < 0.10.
* **Disambiguation**: Differs from **V** (where fingers are spread in a "V" shape) and **H** (which points sideways).

#### Letter V
* **Anatomical Definition**: Index and middle fingers extended straight upward spread apart in a clear open "V" angle (approx. 20°–35°). Ring and pinky are curled; thumb folds across ring finger.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Index and middle extensions > 0.90; distance `index_middle` > 0.25 palm scale.
* **Disambiguation**: Differs from **U** by finger separation distance; identical handshape to number **2**.

#### Letter W
* **Anatomical Definition**: Index, middle, and ring fingers extended straight upward spread evenly apart in a "W" shape. Pinky is curled into palm held down by the thumb tip.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Index, middle, ring extensions > 0.85; pinky extension < 0.20; thumb tip touches pinky tip or cuticle.
* **Disambiguation**: Differs from number **3** (which extends thumb, index, middle).

#### Letter X
* **Anatomical Definition**: Middle, ring, and pinky fingers are curled into a fist. Index finger is raised but bent sharply at its PIP joint into a distinct curved hook shape.
* **Palm Orientation**: Facing forward or slightly angled sideways.
* **MediaPipe Landmarks**: Index MCP extended, index PIP bent at 75°–100° (hook angle); other 3 fingers curled into palm.
* **Disambiguation**: Hooked index posture is unique among all ASL letters.

#### Letter Y
* **Anatomical Definition**: Thumb and pinky finger extended fully outward in opposite directions (shaka / phone posture). Index, middle, and ring fingers are curled tightly into the palm.
* **Palm Orientation**: Facing forward.
* **MediaPipe Landmarks**: Thumb extension > 0.85; pinky extension > 0.85; index, middle, ring extensions < 0.20; large distance between thumb tip (4) and pinky tip (20) (> 1.2 palm scale).
* **Disambiguation**: Thumb and pinky bilateral flare.

---

### B. Numbers (1–5)

#### Number 1
* **Definition**: Single index finger extended straight up; middle, ring, pinky curled into palm held down by thumb. Palm facing forward/inward.
* **Disambiguation**: Similar to **D**, but thumb clasps over curled fingers instead of touching index tip.

#### Number 2
* **Definition**: Index and middle fingers extended straight up spread in a "V" shape; ring and pinky curled held by thumb. Palm facing inward or forward.
* **Disambiguation**: Geometric handshape identical to **V**.

#### Number 3
* **Definition**: Thumb, index, and middle fingers extended upright and spread apart; ring and pinky curled into palm.
* **Disambiguation**: Distinct from **W** (which extends index, middle, ring and keeps thumb folded over pinky).

#### Number 4
* **Definition**: Index, middle, ring, and pinky fingers all extended straight upward spread apart; thumb folded flat across palm.
* **Disambiguation**: Distinct from **B** (which holds all four fingers touching together with zero gap).

#### Number 5
* **Definition**: All five digits (thumb, index, middle, ring, pinky) fully extended upright and spread wide apart. Open hand.
* **Disambiguation**: Maximum total finger extension across all digits.

---

### C. Static Phrases & Control Signs

#### I LOVE YOU
* **Definition**: Thumb, index finger, and pinky finger simultaneously extended straight upward/outward; middle and ring fingers curled into palm.
* **Disambiguation**: Combines handshapes of letters **I**, **L**, and **Y**. Differs from **Y** by extending index finger.

#### OKAY
* **Definition**: Index finger and thumb tips touch together forming a circular ring; middle, ring, and pinky fingers extend straight upward spread apart.
* **Disambiguation**: Classical "OK" sign; identical handshape to letter **F**.

#### PEACE
* **Definition**: Index and middle fingers extended upward in a "V" shape with palm facing directly forward toward the camera. Signifies victory or peace.
* **Disambiguation**: Semantic alias of **V** / **2** with palm facing strictly forward.

#### THUMBS UP
* **Definition**: Closed fist with all four fingers curled tightly into palm and thumb extended straight vertically upward above knuckles.
* **Disambiguation**: Thumb pointing straight up (+Y in local palm frame). Signifies approval/good.

#### THUMBS DOWN
* **Definition**: Closed fist with thumb extended straight downward toward the floor.
* **Disambiguation**: Thumb pointing straight down (-Y in local palm frame). Signifies disapproval/bad.

#### STOP
* **Definition**: Flat open hand with all five fingers extended straight upright and pressed together, palm facing directly outward toward the camera like a traffic halt gesture.
* **Disambiguation**: Palm normal vector points directly along negative Z-axis toward camera (`facing_camera == 1.0`).

#### SPACE
* **Definition**: Flat open hand held horizontally parallel to ground or gentle open hand rest posture with all fingers relaxed, used as an intentional word break delimiter in fingerspelling.
* **Disambiguation**: Signals delimiter between fingerspelled words.

---

## 5. Week 2 Data Pipeline & Zero-Leakage Splitting Blueprint

```text
Raw Image Samples (87k images across classes)
      │
      ▼
MediaPipe Hand Landmarker (extract 21 3D landmarks: x, y, z)
      │
      ▼
FeatureEngineer Pipeline (normalize origin, scale by palm, compute local basis)
      │
      ▼
109-Dimensional Invariant Feature Vector
      │
      ▼
Zero-Leakage Partitioning (Sample-level / Stratified shuffle split):
  ├── Training Set:    70% (~60,900 samples)
  ├── Validation Set:  15% (~13,050 samples)
  └── Test Set:        15% (~13,050 samples)
      │
      ▼
Export Compressed NumPy Archives:
  ├── data/train_features.npz
  ├── data/val_features.npz
  └── data/test_features.npz
```

### Zero-Leakage Guarantee
* **Frame-Level Leakage Prevention**: Never randomly split adjacent frames from the same video capture session.
* **Stratified Class Balance**: Each class maintains exact proportional representation across train, validation, and test splits.
* **Strict Evaluation Isolation**: Test set is locked and untouched during model training and hyperparameter tuning.

---

## 6. Architecture & System Reflection

The UNMUTE recognition engine maintains full backward and forward compatibility:
1. **Real-Time Webcam Pipeline**: Unaltered frontend captures 30 FPS video &rarr; WebSocket &rarr; MediaPipe landmark extraction &rarr; 109 features &rarr; Static MLP &rarr; real-time prediction.
2. **Comparative Baseline**: `models/asl_rf_model.joblib` is retained intact for viva demonstration, regression testing, and latency benchmarking.
3. **Temporal Tracker Interface**: Dynamic gestures (`HELLO`, `THANK YOU`, `YES`, `NO`, `PLEASE`, `J`, `Z`) are cleanly partitioned for Contributor 2's sequence model.
