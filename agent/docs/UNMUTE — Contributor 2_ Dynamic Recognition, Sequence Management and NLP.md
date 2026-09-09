# UNMUTE — Contributor 2: Dynamic Recognition, Sequence Management and NLP

You are one of three contributors working on the **UNMUTE capstone project**.

Your responsibility is to build the **dynamic ASL recognition pipeline, temporal modelling, sequential sign management, and sentence formation layer**.

---

# IMPORTANT PROJECT CONTEXT

UNMUTE is currently a functional real-time **web-based ASL recognition application** using:

- Browser webcam capture
- FastAPI backend
- WebSocket streaming
- OpenCV
- MediaPipe Hand Landmarker
- Existing 109-dimensional feature engineering
- Heuristic/rule-based ASL recognition
- Rule-based temporal gesture tracking
- Browser-based UI and speech output

The current project is **ASL-focused**.

Do not switch the project to ISL.

Do not redesign the frontend.

Do not migrate the application to PySide6.

The goal is to upgrade the existing prototype incrementally rather than rebuild it.

---

# YOUR PRIMARY RESPONSIBILITIES

## 1. Dynamic ASL Recognition

The existing repository contains:

`sign_engine/temporal_tracker.py`

This currently uses:

- A sliding frame window
- `collections.deque`
- Hand trajectory tracking
- Hard-coded movement heuristics

It detects signs such as:

- HELLO
- THANK YOU
- YES
- NO
- PLEASE
- J
- Z

However, the intended final architecture should introduce genuine temporal machine learning.

The target architecture is conceptually:

```text
Sequence of Landmark Feature Vectors
        ↓
Temporal Sequence Preparation
        ↓
LSTM
        ↓
Dense Layer
        ↓
Dynamic ASL Sign Probabilities
```

You are responsible for developing this pipeline.

Do not assume that every sign requires temporal modelling.

Static signs belong to the static recognition pipeline.

Movement-dependent signs belong to the dynamic recognition pipeline.

---

## 2. Dynamic Dataset Strategy

Work with the dataset/model contributor to ensure that the selected ASL data can support temporal modelling.

You should identify a practical controlled vocabulary of dynamic ASL signs.

The dataset or collected samples should provide:

- Multiple frames per sign
- Temporal movement information
- Labels
- Preferably multiple signers

Do not unnecessarily attempt unrestricted continuous ASL translation.

A smaller and reliable set of dynamic signs is preferred.

Before implementing the final dataset pipeline, document:

- Selected dynamic signs
- Why each requires temporal modelling
- Number of samples available
- Sequence length strategy
- Signer information where available
- Dataset limitations

Do not claim signer-independent evaluation unless it is genuinely performed.

---

## 3. Sequence Preparation Pipeline

Design a reproducible temporal data pipeline:

```text
Raw Video
    ↓
Frame Processing
    ↓
MediaPipe Landmark Extraction
    ↓
Feature Engineering / Normalization
    ↓
Temporal Feature Sequence
    ↓
Sequence Padding / Truncation
    ↓
Train / Validation / Test Split
    ↓
LSTM-Ready Dataset
```

The existing project already contains landmark and feature engineering infrastructure.

Reuse compatible existing functionality where practical.

Do not duplicate the same preprocessing logic unnecessarily.

Each dynamic sample should eventually be represented conceptually as:

```text
(time_steps, feature_dimension)
```

The exact sequence length should be chosen experimentally.

Do not arbitrarily claim that 30 frames or 36 frames is the final optimal sequence length.

Avoid data leakage.

Frames belonging to the same source video must not be split across training and testing datasets.

Prefer signer-level separation where metadata permits.

---

## 4. LSTM Model

Implement a beginner-friendly PyTorch LSTM model.

Suggested conceptual architecture:

```text
Input Sequence
        ↓
LSTM
        ↓
Final Hidden Representation
        ↓
Dense Layer
        ↓
Dynamic Sign Classes
```

Keep the architecture understandable for a student viva.

Do not introduce unnecessary transformers or extremely complex architectures.

Implement:

- PyTorch Dataset
- DataLoader
- Sequence handling
- LSTM model
- Forward pass
- Cross-entropy loss
- Optimizer
- Training loop
- Validation loop
- Checkpoint saving
- Label mapping
- Evaluation

The trained model should eventually be usable by the real-time backend.

---

## 5. Existing Temporal Tracker Audit

Before replacing the current heuristic implementation, inspect:

`sign_engine/temporal_tracker.py`

Document:

1. Which dynamic signs it currently supports.
2. How its sliding-window logic works.
3. Which components are useful for real-time buffering.
4. Which heuristic components should eventually be replaced.
5. Whether the existing 36-frame window should remain a runtime buffering mechanism.
6. Whether any existing detection logic can serve as a fallback during early development.

Do not delete working functionality without understanding its role.

The project should remain runnable while ML-based dynamic recognition is being developed.

---

## 6. Real-Time Dynamic Inference Design

Design how the LSTM will eventually operate during live webcam inference.

A possible architecture is:

```text
Live Webcam Frame
        ↓
MediaPipe
        ↓
Feature Extraction
        ↓
Rolling Temporal Buffer
        ↓
Fixed-Length Sequence
        ↓
LSTM Inference
        ↓
Dynamic Sign Prediction
        ↓
Confidence / Stability Processing
```

Do not retrain the LSTM during live inference.

The trained model should be loaded once and used for predictions.

You should define:

- When the temporal buffer begins collecting frames
- How many frames are required before inference
- How frequently predictions are made
- How repeated predictions are stabilized
- How the same dynamic sign is prevented from being emitted repeatedly

The exact implementation can be refined experimentally.

---

## 7. Sequential Sign Recognition

One of the major goals of UNMUTE is moving beyond isolated gesture recognition.

The system should eventually recognize sequences such as:

```text
I → GO → HOME → YESTERDAY
```

without producing:

```text
GO GO GO GO GO GO
```

You are responsible for designing and implementing the sequence-management layer.

Possible mechanisms include:

- Confidence thresholds
- Prediction stability requirements
- Temporal smoothing
- Duplicate suppression
- Cooldown periods
- Sign boundary detection
- Hand disappearance
- Neutral pose detection
- Pause detection

Do not pretend that perfect sign segmentation is already solved.

Document the chosen initial strategy and its limitations.

The system should maintain a structured sequence buffer.

For example:

```python
["I", "GO", "HOME", "YESTERDAY"]
```

rather than immediately concatenating everything into a raw text string.

---

## 8. Sentence Formation and NLP

The recognition models should output sign labels.

They should **not directly generate the final English sentence**.

The correct conceptual pipeline is:

```text
Recognized Sign Labels
        ↓
Structured Sequence Buffer
        ↓
Sentence Formation
        ↓
Rule-Based NLP Refinement
        ↓
Natural-Language Text
```

Example:

```text
Recognition:
I → GO → HOME → YESTERDAY

Language Layer:
I went home yesterday.
```

For the first implementation, prefer:

- Deterministic grammar rules
- Vocabulary-specific mappings
- Sentence templates where useful
- Basic tense transformation
- Basic word ordering
- Basic cleanup

Do not make the project dependent on an LLM.

Do not use NLP to hide poor recognition results.

The language layer should refine recognized sequences, not hallucinate what the signer probably meant.

---

# SUGGESTED FILE OWNERSHIP

Prefer creating and owning new dynamic-recognition and language-processing modules.

A possible structure is:

```text
ml/
├── dynamic/
│   ├── dataset.py
│   ├── sequence_preparation.py
│   ├── dynamic_lstm.py
│   ├── train_dynamic.py
│   └── evaluate_dynamic.py
│
sign_engine/
├── sequence_buffer.py
└── dynamic_recognizer.py

nlp/
└── sentence_processor.py

models/
└── dynamic_lstm/
```

You may adapt this structure if necessary.

Avoid unnecessary modifications to:

- `static/app.js`
- Static recognition model code
- Dataset pipeline owned by Contributor 1

Coordinate interfaces instead of rewriting another contributor's work.

---

# EIGHT-WEEK PROJECT TIMELINE

Your responsibilities should be completed progressively according to the following schedule.

---

## WEEK 1 — Audit and Dynamic Recognition Planning

Focus on understanding the current dynamic system.

Tasks:

1. Inspect `temporal_tracker.py`.
2. Document all currently supported dynamic signs.
3. Understand the current rolling-window logic.
4. Identify reusable real-time buffering components.
5. Coordinate with Contributor 1 regarding the planned dataset strategy.
6. Propose a controlled vocabulary of dynamic signs.
7. Design the dynamic dataset representation.
8. Plan the LSTM input pipeline.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 1

Stop implementation and provide a report containing:

- Current dynamic recognition implementation
- Supported dynamic signs
- Existing heuristic logic
- Proposed dynamic vocabulary
- Proposed sequence representation
- Dataset dependencies
- Planned file structure
- Risks or blockers

Do not proceed to Week 2 until this checkpoint has been reviewed or acknowledged.

---

## WEEK 2 — Temporal Data Pipeline

Build the dataset-processing pipeline.

Tasks:

1. Define the dynamic sample format.
2. Implement landmark-sequence extraction.
3. Reuse compatible feature engineering where appropriate.
4. Implement sequence serialization.
5. Implement padding or truncation if required.
6. Preserve sample/video boundaries.
7. Implement labels and metadata handling.
8. Prepare an ML-ready temporal dataset.

### Incorporating Indian Sign Language (ISL) (Week 2 / Before Week 3)

Incorporate Indian Sign Language (ISL) alongside American Sign Language (ASL) into the temporal data pipeline before starting Week 3 dynamic dataset preparation:

1. **Dual-Hand Dynamic Sequences**:
   - Support bimanual dynamic sequences for ISL dynamic signs (e.g., `HELLO`, `THANK YOU`, `YES`, `NO`, `PLEASE`, `HELP`, `WATER`) where two-handed trajectories and spatial interactions occur.
   - Extend temporal feature frames to support both single-hand (109-dim) for ASL and dual-hand (228-dim) for ISL.

2. **Language-Aware Dynamic Vocabulary**:
   - Coordinate dynamic vocabulary lists with Contributor 1's static label mappings (`ml/data/labels.py`) and Contributor 3's token interface.
   - Maintain distinct dynamic sign classes or language flags so that ASL dynamic signs and ISL dynamic signs are recognized accurately according to the active language mode.

3. **Temporal Sliding Window & Sequence Buffering**:
   - Ensure the sequence extraction and sliding-window temporal buffering logic in `temporal_tracker.py` gracefully handles both 1-hand and 2-hand landmark streams without crashing or dropping frames.
   - Prepare dynamic dataset schemas to store dual-hand landmark trajectories without temporal frame leakage.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 2

Report:

- Dataset/sample format
- Feature dimensionality
- Sequence representation
- Sequence length strategy
- Label format
- Train/validation/test strategy
- Files created
- Files modified
- Pipeline test results
- Any data limitations

Do not proceed until the pipeline is reviewed.

---

## WEEK 3 — Dynamic Dataset Preparation and Baseline

Prepare actual dynamic training data for both ASL and ISL.

Tasks:

### 🚨 URGENT PRIORITY WORK — Core Classifier Overhaul Integration & Temporal Tracker Boundary Guarding

This task must be treated as your most important and urgent work in Week 3, coordinated directly with Contributor 1's overhaul of the core sign recognition classifier (`sign_engine/asl_classifier.py`):

1. **Temporal Tracker Synchronization with Overhauled Static Decision Hierarchy**:
   - Synchronize `TemporalGestureTracker` in `sign_engine/temporal_tracker.py` with Contributor 1's new finger-extension decision hierarchy to ensure dynamic sign tracking seamlessly integrates with the disambiguated static candidate stream across the whole application.
   - Enforce strict temporal boundary guarding and velocity thresholds so dynamic gestures (`HELLO`, `THANK YOU`, `YES`, `NO`, `PLEASE`, `J`, `Z`) never collide with, hijack, or corrupt static signs when a user is holding a static pose (e.g., distinguishing a nodding fist for `YES` from static closed fists `A`, `S`, `E`, `T`, `THUMBS UP`, and open-hand wave `HELLO` from static flat hand `STOP`, `B`, `5`).
   - Validate that dynamic cooldowns and continuous likelihood thresholds prevent spurious triggers during static fingerspelling in both the Live Camera WebSocket stream and Video Processor.

2. **Bilingual Stream Integrity (ASL & ISL)**:
   - Ensure the temporal rolling window (36 frames) properly handles both single-hand (109-dim ASL) and dual-hand (228-dim ISL) landmark sequences without temporal frame drops, buffering corruptions, or dimension mismatches.
   - Ensure dynamic likelihoods passed to `classifier.classify_hand()` are properly formatted and normalized to preserve stability in the live letter accumulator and sentence composer.

1. Process selected dynamic sign samples for ASL (`HELLO`, `THANK YOU`, `YES`, `NO`, `PLEASE`, `J`, `Z`) and ISL (`HELLO`, `THANK YOU`, `YES`, `NO`, `PLEASE`, `HELP`, `WATER`).
2. Extract unimanual landmark sequences for ASL and bimanual landmark sequences for ISL.
3. Verify feature consistency (109 dims single-hand, 228 dims dual-hand).
4. Create reproducible dataset splits for both languages.
5. Confirm there is no frame-level leakage.
6. Build the initial PyTorch Dataset/DataLoader supporting both single-hand and dual-hand sequences.
7. Validate tensor shapes across both language configurations.
8. Establish minimal baseline experiments for both ASL and ISL.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 3

Report:

- Core classifier overhaul integration and temporal tracker boundary validation results
- Number of dynamic samples prepared (ASL and ISL)
- Dynamic classes across both languages
- Tensor shapes (single-hand vs dual-hand)
- Split methodology
- Whether signer separation is available
- Data pipeline validation results for both languages
- Known dataset limitations

Do not claim model performance unless training has actually occurred.

---

## WEEK 4 — LSTM Model Implementation

Implement the dynamic recognition model for both ASL and ISL.

Tasks:

1. Define the PyTorch LSTM architecture accommodating single-hand (109-dim ASL) and dual-hand (228-dim ISL) temporal sequences, or language-specific sequence heads.
2. Implement the forward pass.
3. Implement training and validation loops.
4. Configure loss and optimizer.
5. Add checkpoint saving (`asl_dynamic_lstm.pt` and `isl_dynamic_lstm.pt`).
6. Add label mapping for both ASL and ISL dynamic vocabularies.
7. Run initial training experiments for both languages.

Keep the model architecture explainable.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 4

Report:

- LSTM architecture (handling ASL and ISL)
- Input/output tensor shapes
- Training configuration
- Loss function
- Optimizer
- Checkpoint format
- Initial training results for both languages, if available
- Any errors or limitations

Do not continue to major integration until the basic model pipeline works.

---

## WEEK 5 — Dynamic Model Training and Evaluation

Focus on actual experiments across both ASL and ISL.

Tasks:

1. Train the dynamic LSTM models on ASL and ISL sequences.
2. Monitor training and validation behavior for both languages.
3. Save the best checkpoints (`asl_dynamic_lstm.pt` and `isl_dynamic_lstm.pt`).
4. Evaluate using unseen data for both ASL and ISL.
5. Generate for both ASL and ISL:
   - Accuracy
   - Precision
   - Recall
   - F1-score
   - Confusion matrix
6. Document model failure cases (including unimanual vs bimanual motion tracking issues).

Do not fabricate metrics.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 5

Report:

- Training status for both languages
- Best validation results (ASL and ISL)
- Test results
- Evaluation methodology
- Confusion matrices for both languages
- Known weak classes
- Overfitting/underfitting observations
- Checkpoint locations (`asl_dynamic_lstm.pt` and `isl_dynamic_lstm.pt`)

---

## WEEK 6 — Real-Time Dynamic Inference

Begin integrating the trained models conceptually with the live pipeline.

Tasks:

1. Design rolling temporal feature buffers that accommodate both single-hand ASL streams and dual-hand ISL streams based on active language mode.
2. Load the trained LSTM models once at startup.
3. Convert buffered frames into model input conditioned on active language mode.
4. Perform dynamic inference in real-time.
5. Add confidence extraction for both languages.
6. Add prediction stability handling.
7. Preserve the existing application and heuristic temporal tracker while integration is tested.

Do not remove the existing temporal tracker until the replacement is verified.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 6

Report:

- Real-time inference architecture for ASL and ISL
- Buffer size and strategy for 1-hand and 2-hand inputs
- Inference frequency
- Model loading mechanism
- Prediction output format
- Stability mechanism
- Integration dependencies
- Current test status across both languages

---

## WEEK 7 — Sequence Buffer and NLP

Focus on converting recognized signs into meaningful language for both ASL and ISL.

Tasks:

1. Implement a structured sign sequence buffer handling tokens from both ASL and ISL recognition engines.
2. Implement duplicate suppression.
3. Implement basic sign boundary handling.
4. Define the interface between recognition and NLP with language mode awareness (`mode: "ASL"` vs `mode: "ISL"`).
5. Implement rule-based sentence formation for both languages.
6. Add vocabulary-specific grammar transformations for both ASL and ISL:
   - ASL Example:
     ```text
     ["I", "GO", "HOME", "YESTERDAY"]
             ↓
     "I went home yesterday."
     ```
   - ISL Example:
     ```text
     ["NAMASTE", "I", "HELP", "YOU"]
             ↓
     "Namaste, I will help you."
     ```
7. Test sequences using known recognition outputs from both languages.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 7

Report:

- Sequence-buffer design (handling ASL and ISL tokens)
- Duplicate suppression strategy
- Boundary handling strategy
- NLP rules implemented for both languages
- Supported sentence patterns (ASL and ISL)
- Example input/output sequences for both languages
- Limitations
- Files created or modified

Do not claim unrestricted language translation.

---

## WEEK 8 — Integration Support and Final Evaluation

Prepare your modules for integration into the complete UNMUTE pipeline.

Tasks:

1. Test static/dynamic prediction interfaces for both ASL and ISL with the backend contributor.
2. Test sequence buffering with realistic recognition output from both language modes.
3. Test NLP processing across both ASL and ISL.
4. Measure relevant latency where possible for single-hand and dual-hand sequences.
5. Document failure cases.
6. Prepare integration instructions for both language pipelines.
7. Prepare final technical documentation.

### PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 8

Provide a final implementation report containing:

- What was implemented (ASL and ISL dynamic recognition)
- What was tested across both languages
- Actual model evaluation results
- Dynamic recognition capabilities (unimanual ASL and bimanual ISL)
- Sequence-management capabilities
- NLP capabilities across both languages
- Remaining limitations
- Exact files changed
- Model/checkpoint locations (`asl_dynamic_lstm.pt` and `isl_dynamic_lstm.pt`)
- Integration instructions
- Known issues
- Recommended future improvements

---

# REQUIRED DELIVERABLES

Before considering your contribution complete, provide:

1. Dynamic recognition audit.
2. Dynamic vocabulary selection.
3. Temporal dataset representation.
4. Sequence preprocessing pipeline.
5. Train/validation/test strategy.
6. Working PyTorch LSTM.
7. Dynamic training script.
8. Dynamic evaluation script.
9. Saved model checkpoint.
10. Label mapping.
11. Actual evaluation results, if training was completed.
12. Real-time temporal buffering design or implementation.
13. Structured sequence buffer.
14. Duplicate suppression strategy.
15. Rule-based sentence formation module.
16. Backend integration instructions.
17. Final implementation report.

---

# IMPORTANT RULES

- Do not redesign the UI.
- Support both ASL and ISL concurrently; do not discard or switch away from ASL when adding ISL.
- Do not claim unrestricted ASL or ISL translation.
- Do not fabricate model metrics.
- Do not claim signer-independent evaluation unless it actually occurred.
- Do not leak frames from the same video into train and test sets.
- Do not replace working code without verifying its role.
- Do not make the project dependent on an LLM.
- Do not use NLP to compensate for unreliable recognition.
- Keep the LSTM architecture understandable for a student viva.
- Keep static and dynamic recognition conceptually separate.
- Commit changes to your own branch.
- Coordinate interfaces with the other contributors.
- Stop and report at every weekly checkpoint before continuing to the next major stage.

---

# STARTING PROCEDURE

Before making changes:

1. Inspect the current repository state.
2. Review `temporal_tracker.py`.
3. Identify existing feature representations.
4. Confirm Git branch status.
5. Create or switch to your contributor branch.
6. Coordinate expected model/data interfaces with Contributor 1.
7. Summarize your Week 1 implementation plan.
8. Then begin the audit and planning process.

At the end of the project, provide a clear implementation report stating:

- What was implemented
- What was tested
- What remains incomplete
- Actual evaluation results
- Exact files changed
- Model/checkpoint locations
- How the backend contributor should integrate the dynamic model
- How recognized sign sequences are passed into sentence formation