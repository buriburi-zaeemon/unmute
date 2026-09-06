# UNMUTE — Contributor 1: Dual ASL & ISL Dataset Strategy & Controlled Vocabulary Specification

**Author:** Contributor 1 (ML Foundation and Static Recognition)  
**Status:** Approved Specification  
**Scope:** Dual American Sign Language (ASL) and Indian Sign Language (ISL) Recognition Pipelines

---

## 1. Executive Summary & Multi-Language Scope

UNMUTE is an assistive, real-time sign language translation platform supporting **both American Sign Language (ASL) and Indian Sign Language (ISL)**. The machine learning recognition architecture provides language-tailored pipelines:

1. **American Sign Language (ASL)**:
   * **Kinematic Style**: Primarily **unimanual (single-handed)** fingerspelling, numerals, and static postures.
   * **Feature Vector**: **109-dimensional** rotation- and scale-invariant geometric feature representation derived from 21 3D landmarks.
   * **Static Recognition Model**: `StaticASL_MLP` (PyTorch).
2. **Indian Sign Language (ISL)**:
   * **Kinematic Style**: Primarily **bimanual (two-handed)** fingerspelling (where the dominant hand interacts with the base hand according to official ISLRTC standards) alongside single-handed numerals.
   * **Feature Vector**: **218+ dimensional** bimanual invariant feature representation (109 Primary Hand + 109 Secondary Hand + Inter-hand contact and relative spatial metrics).
   * **Static Recognition Model**: `StaticISL_MLP` (PyTorch).

---

## 2. Dataset Strategy & Recommendations

### A. American Sign Language (ASL) Dataset
* **Selected Dataset**: **ASL Alphabet Dataset** (Akash Nagaraj, Kaggle)
* **Format**: 87,000 RGB images (200×200 px), 29 base folders.
* **MediaPipe Detection Fidelity**: >96% successful 21-landmark extraction.
* **Licensing**: CC0 Public Domain.
* **Role**: Primary dataset for extracting 109-dim single-hand features for ASL static letters, numerals 0–9, and static phrases.

### B. Indian Sign Language (ISL) Dataset
* **Selected Dataset**: **Indian Sign Language (ISLRTC-referred) Dataset** (Atharva Dumbre / Ayuraj / Kaggle)
* **Format**: 36,000 RGB images (250×250 px), 1,000 images per class across 36 standard classes (A–Z and 0–9).
* **Sign Standard**: Conforms directly to the **Indian Sign Language Research and Training Centre (ISLRTC)** standards under the Ministry of Social Justice and Empowerment, Government of India.
* **MediaPipe Detection Fidelity**: ~94% dual-hand detection across bimanual letters and single-hand numerals.
* **Licensing**: Open Research / Educational.
* **Role**: Primary training source for two-handed 218-dim feature extraction and bimanual static classification.

---

## 3. Controlled Vocabulary Specifications

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          UNMUTE CONTROLLED VOCABULARIES                                │
├──────────────────────────┬─────────────────────────────────┬───────────────────────────┤
│ Category                 │ ASL (Single-Hand Focus)         │ ISL (Bimanual Focus)      │
├──────────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ Alphabets (Static)       │ 24 Classes (A–Y, excl J & Z)    │ 26 Classes (A–Z complete) │
├──────────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ Numerals                 │ 10 Classes (0, 1, 2, 3, 4,      │ 10 Classes (0, 1, 2, 3, 4,│
│                          │             5, 6, 7, 8, 9)      │             5, 6, 7, 8, 9)│
├──────────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ Static Phrases           │ 6 Classes:                      │ 7 Classes:                │
│                          │ I LOVE YOU, OKAY, PEACE,        │ NAMASTE, I LOVE YOU,      │
│                          │ STOP, THUMBS DOWN, THUMBS UP    │ PEACE, OKAY, THUMBS UP,   │
│                          │                                 │ THUMBS DOWN, STOP         │
├──────────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ Control Sign             │ 1 Class: SPACE                  │ 1 Class: SPACE            │
├──────────────────────────┼─────────────────────────────────┼───────────────────────────┤
│ Total Static Classes     │ 41 Classes                      │ 44 Classes                │
└──────────────────────────┴─────────────────────────────────┴───────────────────────────┘
```

---

## 4. Authoritative Sign Definition Catalog

### A. ASL Static Alphabets (A–Y, excluding dynamic J & Z)
* **A**: Closed fist with 4 fingers curled into palm; thumb extended upright alongside outer knuckle of index finger.
* **B**: All 4 fingers extended straight upward pressed together; thumb folded flat across palm.
* **C**: Fingers and thumb curved into an open semicircular "C" arc with clear aperture.
* **D**: Index finger extended straight up; middle, ring, pinky touch thumb tip in a closed loop.
* **E**: All 4 fingers curled tightly downward with fingertip pads resting directly on thumb pad.
* **F**: Index and thumb touch in a pinch circle; middle, ring, pinky extended straight up.
* **G**: Index and thumb parallel pointing horizontally sideways; middle, ring, pinky curled into palm.
* **H**: Index and middle fingers extended together pointing horizontally sideways; thumb tucked.
* **I**: Pinky finger extended straight up from closed fist; thumb folded across curled fingers.
* **K**: Index straight up, middle angled forward 45°, thumb pad rests against middle finger PIP knuckle.
* **L**: Thumb and index extended at a perpendicular 90° right angle; other fingers curled.
* **M**: Index, middle, ring fingers draped over thumb; thumb tip protrudes below pinky knuckle.
* **N**: Index and middle fingers draped over thumb; thumb tip protrudes between middle and ring.
* **O**: All fingertips and thumb tip touch pad-to-pad forming a completely closed "O" circle.
* **P**: Hand oriented downward; index forward, middle down 90°, thumb rests against middle PIP.
* **Q**: Index and thumb parallel pointing straight downward toward ground; other fingers curled.
* **R**: Index and middle fingers extended straight up and tightly crossed with index in front.
* **S**: Closed fist with thumb wrapped horizontally across the front of the curled fingers.
* **T**: Closed fist with thumb tucked between index and middle fingers, poking up between knuckles.
* **U**: Index and middle fingers extended straight up pressed firmly together side-by-side.
* **V**: Index and middle fingers extended straight up spread in an open symmetrical "V" angle.
* **W**: Index, middle, ring fingers extended straight up spread apart; thumb holds pinky tip.
* **X**: Middle, ring, pinky curled; index finger extended and bent sharply at PIP into a hook.
* **Y**: Thumb and pinky extended wide outward (shaka shape); index, middle, ring curled.

---

### B. ASL Numerals (0–9)
* **0**: All 5 fingertips touch thumb pad forming an oval circle (handshape identical to `O`).
* **1**: Single index finger extended upright; middle, ring, pinky curled into palm held by thumb.
* **2**: Index and middle fingers extended spread in a "V" shape with palm facing inward/forward.
* **3**: Thumb, index, and middle fingers extended spread apart; ring and pinky curled into palm.
* **4**: Index, middle, ring, and pinky extended upright spread apart; thumb folded across palm.
* **5**: All 5 digits (thumb through pinky) fully extended upright and spread wide apart.
* **6**: Thumb tip touches pinky tip; index, middle, and ring fingers extended upright.
* **7**: Thumb tip touches ring finger tip; index, middle, and pinky fingers extended upright.
* **8**: Thumb tip touches middle finger tip; index, ring, and pinky fingers extended upright.
* **9**: Thumb tip touches index finger tip; middle, ring, and pinky extended upright (resembles `F`).

---

### C. ISL Static Alphabets (A–Z, Two-Handed Bimanual Standards)

In Indian Sign Language fingerspelling, the **dominant hand (DH)** performs active gestures against the **non-dominant base hand (BH)**:

* **A (ISL)**: Non-dominant base hand held flat with fingers extended upright; dominant index finger touches the tip of the base hand's thumb.
* **B (ISL)**: Both hands touch index finger and thumb tips together, creating dual adjacent circles (resembling the two lobes of letter "B").
* **C (ISL)**: Dominant hand forms a curved semicircular "C" shape in the air with open aperture (unimanual).
* **D (ISL)**: Base hand forms a closed fist with index finger extended upright; dominant hand curves thumb and index to touch base index tip and wrist, forming "D".
* **E (ISL)**: Base hand held flat upright; dominant index finger touches the tip of the base hand's index finger.
* **F (ISL)**: Index and middle fingers of both hands crossed over each other horizontally forming a grid (hashtag shape).
* **G (ISL)**: Both hands form closed fists placed vertically on top of each other (dominant fist rests on base fist).
* **H (ISL)**: Base hand held flat horizontally palm upward; dominant hand sweeps flat across base palm horizontally.
* **I (ISL)**: Base hand held flat upright; dominant index finger touches the tip of the base hand's middle finger.
* **J (ISL)**: Base hand held flat upright; dominant index finger touches base middle fingertip, then sweeps downward into the base palm.
* **K (ISL)**: Dominant index finger bends at knuckle and hooks over the upright extended base index finger.
* **L (ISL)**: Dominant hand forms unimanual 90° right angle with thumb and index finger extended (similar to ASL L).
* **M (ISL)**: Dominant index, middle, and ring fingers placed downward onto the open palm of the base hand (three legs of "M").
* **N (ISL)**: Dominant index and middle fingers placed downward onto the open palm of the base hand (two legs of "N").
* **O (ISL)**: Base hand held flat upright; dominant index finger touches the tip of the base hand's ring finger.
* **P (ISL)**: Dominant hand forms a circular loop with thumb and index, placed against the upright extended index finger of the base hand.
* **Q (ISL)**: Base hand forms a circular "O" loop; dominant index finger hooks through the loop from behind.
* **R (ISL)**: Dominant hooked index finger placed over the palm of the flat upright base hand.
* **S (ISL)**: Pinky fingers of both hands hooked and linked together with hands facing inward.
* **T (ISL)**: Dominant index finger placed horizontally across the top edge of the upright extended base index finger.
* **U (ISL)**: Base hand held flat upright; dominant index finger touches the tip of the base hand's pinky finger.
* **V (ISL)**: Dominant hand extends index and middle fingers in a "V" shape placed onto the palm of the base hand.
* **W (ISL)**: Both hands interlock fingers spread apart with palms facing inward, creating a three-peak "W".
* **X (ISL)**: Index fingers of both hands extended and crossed over each other at right angles forming an "X".
* **Y (ISL)**: Dominant open "V" hand placed astride the base hand's open web between thumb and index.
* **Z (ISL)**: Dominant flat hand held horizontally sideways; palm placed against the upper edge of the base hand.

---

### D. ISL Numerals (0–9)
* **0 (ISL)**: Closed fist or circular "O" handshape with one hand.
* **1 (ISL)**: Dominant index finger extended straight upright.
* **2 (ISL)**: Dominant index and middle fingers extended upright spread apart.
* **3 (ISL)**: Dominant thumb, index, and middle fingers extended spread apart.
* **4 (ISL)**: Dominant four fingers extended upright, thumb folded.
* **5 (ISL)**: Dominant all 5 fingers fully extended and spread wide apart.
* **6 (ISL)**: Base hand flat; dominant index placed across base palm, or single hand thumb-to-pinky touch.
* **7 (ISL)**: Base hand flat; dominant index and middle placed across base palm.
* **8 (ISL)**: Base hand flat; dominant 3 fingers placed across base palm.
* **9 (ISL)**: Base hand flat; dominant 4 fingers placed across base palm.

---

### E. Static Phrases & Control Signs

#### ASL Static Phrases
* **I LOVE YOU**: Simultaneous extension of thumb, index, and pinky.
* **OKAY**: Index-thumb pinch circle with middle, ring, pinky extended.
* **PEACE**: Upright index and middle "V" with palm facing camera.
* **STOP**: Flat open hand facing outward toward camera.
* **THUMBS UP**: Clenched fist with thumb vertical upward.
* **THUMBS DOWN**: Clenched fist with thumb pointing toward floor.
* **SPACE**: Relaxed open hand pause delimiter.

#### ISL Static Phrases
* **NAMASTE**: Both hands brought together in front of chest with palms pressed together and fingers pointing upward (Añjali Mudrā / universal greeting).
* **I LOVE YOU (ISL)**: Universal ILY gesture or dual-hand heart shape formed by thumbs and index fingers.
* **PEACE (ISL)**: Symmetrical two-handed or one-handed victory sign.
* **OKAY (ISL)**: Thumb-index circle with remaining digits extended upright.
* **THUMBS UP (ISL)**: Upright vertical thumb with closed fist (signifying approval/achha).
* **THUMBS DOWN (ISL)**: Downward vertical thumb with closed fist (signifying disapproval/kharab).
* **STOP (ISL)**: Flat open palm held outward facing camera.
* **SPACE (ISL)**: Open hands horizontal pause delimiter.

---

## 5. Dual Feature Pipeline & Zero-Leakage Splitting Blueprint

```text
                        Webcam / Video Frame
                                  │
                                  ▼
                MediaPipe Hand Landmarker (max_num_hands=2)
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
          Single Hand (ASL)               Two Hands (ISL)
                  │                               │
                  ▼                               ▼
       FeatureEngineer (109 dims)       DualFeatureEngineer (218+ dims)
                  │                               │
                  ▼                               ▼
         StaticASL_MLP (PyTorch)         StaticISL_MLP (PyTorch)
                  │                               │
                  ▼                               ▼
          ASL Class Output                ISL Class Output
```

### Zero-Leakage Dataset Partitioning
* **Split Ratio**: 70% Train (~25,200 samples per language) / 15% Validation (~5,400 samples) / 15% Test (~5,400 samples).
* **Isolation**: All splits are computed at the sample level using stratified class balancing and locked seeds to guarantee zero data leakage between training and evaluation phases.
