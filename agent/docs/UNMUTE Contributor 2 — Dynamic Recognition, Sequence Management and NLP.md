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

# MANDATORY WORKFLOW POLICY: STRICT BRANCH-FIRST DEVELOPMENT

## Core Directive for All AI Agents and Contributors

To protect the stability of the `main` branch, eliminate code conflicts, and prevent unverified or breaking changes from harming the core application, **all contributors and AI agents MUST adhere strictly to the branch-first development workflow**. 

Direct development on `main` is strictly prohibited. Branching is mandatory to ensure feature isolation, safe rollbacks, and team coordination.

### Independent History & Source of Truth Architecture:
- **Each Branch Tracks Its Own History**: Contributor branches (`contributor-1-ml-foundation`, `contributor-2-dynamic-nlp`, `contributor-3-nlp-integration`) track their own independent development history. Do not cross-merge other contributor branches into your branch; if another contributor's branch is empty or not yet active, leave it untouched.
- **`main` Is the Combined Source of Truth**: The `main` branch serves as the single unified source of truth combining verified, tested contributions from all branches.

### Required Cyclic Step-by-Step Workflow (Squash-Merge Default Policy):

1. **Pull Main & Check for Updates**:
   Before starting any work or new task, fetch all remote refs, switch to `main`, and pull the latest changes to check if any upstream updates exist:
   ```bash
   git fetch --all
   git checkout main
   git pull origin main
   ```

2. **Pull Feature Branch & Squash-Merge Updates from Main**:
   Switch to your assigned feature branch and pull its remote state. If `main` contains new commits or updates, **squash-merge `main` into your feature branch** and commit with a clean sync message. This guarantees your branch has 100% of the latest upstream codebase baseline and fixes without polluting your branch's commit history with intermediate commits from other contributors:
   ```bash
   git checkout contributor-2-dynamic-nlp
   git pull origin contributor-2-dynamic-nlp
   # Upon seeing updates in main:
   git merge --squash main
   git commit -m "chore(sync): squash-sync latest codebase baseline from main"
   git push origin contributor-2-dynamic-nlp
   ```

3. **Develop & Implement Inside Your Branch**:
   Perform all code edits, model training, feature extraction, and experiments exclusively inside your assigned branch. Never edit directly on `main`.

4. **Test Thoroughly Inside Your Branch**:
   Run the complete test suite and verify that all unit, regression, and integration tests pass cleanly with zero errors before merging or pushing:
   ```bash
   pytest tests/ -v
   ```

5. **Commit Locally & Push Your Feature Branch**:
   Commit working units of code on your branch with descriptive, standardized commit messages, and push your feature branch to remote so its history is always backed up remotely:
   ```bash
   git add <modified-files>
   git commit -m "feat/fix/docs(<scope>): clear description of work done"
   git push origin contributor-2-dynamic-nlp
   ```

6. **Squash-Merge into `main` When Ready to Push**:
   Only after all tasks are completed, tested, and verified to be 100% functional, switch to `main`, pull any fresh changes, and **squash-merge your feature branch into `main`** to maintain a clean, high-signal commit history on `main`:
   ```bash
   git checkout main
   git pull origin main
   git merge --squash contributor-2-dynamic-nlp
   git commit -m "feat/fix(<scope>): summary of completed milestone"
   pytest tests/ -v  # Final sanity check on main
   ```

7. **Push `main` to Remote**:
   Once the squash-merge to `main` is validated and all tests pass without errors, push the updated `main` branch to remote origin:
   ```bash
   git push origin main
   ```

8. **Repeat Cycle for Every New Task (All Branches Always Pushed & Pulled)**:
   When beginning the next task, repeat this exact loop: pull `main`, inspect updates, squash-merge `main` into your feature branch, work, test, commit & push your feature branch, squash-merge to `main`, and push `main`. All branches must always be pushed and pulled, not just `main`.

### Why This Is Mandatory:
- **All Branches Always Pushed & Pulled**: Pushing and pulling both your feature branch and `main` ensures that individual branch histories are preserved remotely, while `main` continuously reflects the combined, working source of truth.
- **Independent History Isolation**: Each contributor branch retains clean provenance and atomic responsibility without cross-pollinating unverified code.
- **Zero Harm to `main`**: Unfinished experiments, broken dependencies, or syntax regressions remain isolated in feature branches and never compromise the live application or other contributors' workflows.
- **Conflict Prevention**: Concurrent development across Contributors 1, 2, and 3 proceeds independently without git collisions.

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

---

# EIGHT-WEEK PROJECT TIMELINE

Your responsibilities should be completed progressively according to the following schedule.

---

## WEEK 1 — Audit and Dynamic Recognition Planning (Sep 02 – Sep 06, 2026)

Focus on understanding the current dynamic system.

### Granular Sub-Tasks:
- **Sub-task 1.1 — Dynamic Recognition Codebase Audit**: Inspect `sign_engine/temporal_tracker.py`, evaluate rolling-window buffer (36 frames), and document heuristic tracking methods (`detect_wave`, `detect_nod`, `detect_thank_you`).
- **Sub-task 1.2 — Dynamic Signs Catalog & Vocabulary Definition**: Document currently supported gestures (`HELLO`, `YES`, `NO`, `THANK YOU`) and propose controlled dynamic vocabulary for ASL and ISL.
- **Sub-task 1.3 — Sequence Buffer Representation Design**: Formulate temporal sequence tensor specifications (timesteps $T=30$, features $D=109$ for ASL, $D=228$ for ISL).
- **Sub-task 1.4 — Model Architecture & LSTM Training Strategy**: Plan two-layer PyTorch LSTM sequence classification model with bidirectional context and dropout.
- **Sub-task 1.5 — Contributor 1 Alignment & Dataset Interface**: Coordinate with Contributor 1 regarding shared invariant landmark normalizations and dataset directory layouts.

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

## WEEK 2 — Temporal Data Pipeline (Sep 07 – Sep 08, 2026)

Build the dataset-processing pipeline.

### Granular Sub-Tasks:
- **Sub-task 2.1 — Dynamic Sample Format & Landmark Sequence Extraction**: Define structured sample schema (`landmarks`, `labels`, `sequence_length`, `fps`, `language_mode`).
- **Sub-task 2.2 — Dual-Hand Temporal Sequences for ISL**: Support bimanual sequence frames (228 dims) capturing inter-hand distance and relative wrist motion trajectories.
- **Sub-task 2.3 — Sliding Window & Padding/Truncation Pipeline**: Implement temporal sequence normalization to fixed length ($T=30$ frames) using linear interpolation and zero-padding.
- **Sub-task 2.4 — Zero-Leakage Dynamic Dataset Splitting**: Implement video-level stratified splitting (70% train / 15% val / 15% test) preventing contiguous frame leakage.
- **Sub-task 2.5 — PyTorch Sequence Dataset & DataLoader**: Implement PyTorch `Dataset` and `DataLoader` abstractions yielding batch tensors of shape `(B, T, D)`.

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

## WEEK 3 — Dynamic Dataset Preparation and Baseline (Sep 10 – Sep 11, 2026)

Prepare actual dynamic training data for both ASL and ISL.

### Granular Sub-Tasks:
- **Sub-task 3.1 — Core Classifier Overhaul Integration & Temporal Boundary Guarding**: Synchronize `TemporalGestureTracker` with Contributor 1's finger-extension decision hierarchy to prevent static pose collisions (`YES` vs fist family `A`/`S`/`E`/`T`, `HELLO` vs `STOP`/`B`/`5`).
- **Sub-task 3.2 — Velocity Thresholds & Gesture Cooldown Management**: Implement movement velocity filters and dynamic cooldowns to prevent spurious triggers during fingerspelling.
- **Sub-task 3.3 — Bimanual Sequence Extraction for ISL**: Process dynamic samples for ISL (`HELLO`, `THANK YOU`, `YES`, `NO`, `PLEASE`, `HELP`, `WATER`).
- **Sub-task 3.4 — Dynamic Baseline Training Experiments**: Establish baseline PyTorch LSTM experiments on dynamic sequences.

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

## WEEK 4 — LSTM Model Implementation (Sep 12 – Sep 19, 2026)

Implement the dynamic recognition model for both ASL and ISL.

### Granular Sub-Tasks:
- **Sub-task 4.1 — Dual-Language LSTM Architecture Implementation**: Implement `DynamicSignLSTM` supporting both unimanual ASL (109 dims) and bimanual ISL (228 dims) with configurable hidden units and bidirectional layers.
- **Sub-task 4.2 — Forward Pass & Logits Computation**: Implement sequence forward pass, temporal mean-pooling/last-step selection, and class probability prediction.
- **Sub-task 4.3 — Modular PyTorch Training & Validation Loops**: Implement cross-entropy loss, AdamW optimizer, and learning rate scheduling (`ReduceLROnPlateau`).
- **Sub-task 4.4 — Checkpoint Serialization & Best Weights Storage**: Save checkpoints to `models/asl_dynamic_lstm.pt` and `models/isl_dynamic_lstm.pt`.

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

## WEEK 5 — Dynamic Model Training and Evaluation (Sep 20 – Sep 26, 2026)

Focus on actual experiments across both ASL and ISL.

### Granular Sub-Tasks:
- **Sub-task 5.1 — Extended Model Training on Full Dynamic Datasets**: Train ASL and ISL LSTM models across full training splits with early stopping.
- **Sub-task 5.2 — Validation Monitoring & Overfitting Prevention**: Track validation loss, accuracy curves, and apply dropout regularization ($p=0.3$).
- **Sub-task 5.3 — Comprehensive Held-Out Test Evaluation**: Evaluate accuracy, precision, recall, macro F1, and weighted F1 on held-out test splits.
- **Sub-task 5.4 — Confusion Matrix Generation & Weak Class Analysis**: Identify challenging motion trajectories, bimanual occlusions, and transition artifacts.

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

## WEEK 6 — Real-Time Dynamic Inference (Sep 27 – Oct 03, 2026)

Begin integrating the trained models conceptually with the live pipeline.

### Granular Sub-Tasks:
- **Sub-task 6.1 — Rolling Temporal Buffer Interface**: Implement thread-safe rolling feature buffer ($T=30$) accepting per-frame MediaPipe features based on active language mode (`ASL` vs `ISL`).
- **Sub-task 6.2 — Model Startup Loader & Warmup**: Load `asl_dynamic_lstm.pt` and `isl_dynamic_lstm.pt` once at startup with device auto-detection (`CPU`/`CUDA`).
- **Sub-task 6.3 — Real-Time Inference Dispatcher**: Perform non-blocking dynamic inference when rolling buffer is saturated with active motion.
- **Sub-task 6.4 — Confidence Calibration & Stability Guardrails**: Apply softmax thresholding and consecutive-frame stability filters to prevent prediction flicker.
- **Sub-task 6.5 — Fallback & Legacy Tracker Coexistence**: Preserve heuristic tracker fallback while dynamic LSTM inference is validated.

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

## WEEK 7 — Sequence Buffer and NLP (Oct 04 – Oct 10, 2026)

Focus on converting recognized signs into meaningful language for both ASL and ISL.

### Granular Sub-Tasks:
- **Sub-task 7.1 — Structured Sign Sequence Buffer**: Implement sequence buffer consuming static tokens (from Contributor 1) and dynamic tokens (from Contributor 2).
- **Sub-task 7.2 — Duplicate Token Suppression & Debouncing**: Implement temporal debounce and consecutive duplicate suppression window.
- **Sub-task 7.3 — Sign Boundary Detection & Word Segmentation**: Detect sign pauses and transitions using hand velocity and resting poses.
- **Sub-task 7.4 — Language-Specific Grammar Transformations**: Implement deterministic rule-based sentence transformations for ASL (topic-comment) and ISL (SOV sentence patterns).
- **Sub-task 7.5 — Capitalization, Punctuation & Output Formatting**: Apply automatic capitalization, punctuation insertion, and final English sentence composition.

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

## WEEK 8 — Integration Support and Final Evaluation (Oct 11 – Oct 18, 2026)

Prepare your modules for integration into the complete UNMUTE pipeline.

### Granular Sub-Tasks:
- **Sub-task 8.1 — End-to-End Pipeline Integration Verification**: Test integration of static/dynamic recognition with sequence buffer and NLP pipeline in live WebSocket stream.
- **Sub-task 8.2 — Multi-Modal Latency Benchmarking**: Measure per-frame inference latency, sequence buffer delay, and sentence formulation latency ($\le 25\text{ ms}$ total).
- **Sub-task 8.3 — Comprehensive Failure Mode Documentation**: Document edge cases (bimanual hand swap, fast sign transitions, ungrammatical input sequences).
- **Sub-task 8.4 — Final Technical Documentation & Handover Report**: Author technical documentation covering dynamic LSTM models, sequence buffer APIs, and NLP grammar rules.

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

# CRITICAL INTEGRATION & MANDATORY ARCHITECTURE UPDATE (WEEK 3)

## Architectural Alignment with Contributor 1 (ML Foundation & Static Recognition)

To ensure full compatibility across the multimodal sign translation pipeline, Contributor 1 has finalized and deployed foundational upgrades to the static recognition engine and the client-side visual inspection system. Contributor 2 and their AI agents MUST adhere to these updated interfaces when designing dynamic sequence buffers, rolling feature windows, and NLP translation boundaries:

### 1. Universal Person-Invariant Feature & Extension Extraction
- **Self-Phalange Bone Length Normalization**:
  The static classifier in `sign_engine/asl_classifier.py` and feature extraction pipeline in `sign_engine/feature_engineering.py` no longer depend on arbitrary palm-to-finger scaling ratios. Instead, each finger's straightness and extension ratio is normalized against its own cumulative bone length:
  $$\text{bone\_length} = \|\mathbf{p}_{\text{PIP}} - \mathbf{p}_{\text{MCP}}\| + \|\mathbf{p}_{\text{DIP}} - \mathbf{p}_{\text{PIP}}\| + \|\mathbf{p}_{\text{TIP}} - \mathbf{p}_{\text{DIP}}\|$$
  $$\text{extension\_ratio} = \frac{\|\mathbf{p}_{\text{TIP}} - \mathbf{p}_{\text{MCP}}\|}{\text{bone\_length}}$$
- **Directional Phalanx Collinearity**:
  To prevent false positives between curved/arched hands (`C`, `O`) and straight upright fingers (`U`, `V`, `B`, `R`, `L`), the proximal-to-distal phalanx vector dot product is used:
  $$\frac{\mathbf{v}_{\text{prox}} \cdot \mathbf{v}_{\text{dist}}}{\|\mathbf{v}_{\text{prox}}\| \|\mathbf{v}_{\text{dist}}\|} > 0.35$$
- **Dynamic Sequence Implication**: When Contributor 2 extracts delta motion vectors across rolling temporal windows ($T = 30$ frames), do NOT re-normalize keypoints against raw pixel dimensions. Always rely on invariant landmark-relative coordinates to preserve signer independence across varying hand sizes, palm-to-finger ratios, and camera distances.

### 2. Standardized 5-Finger Color System
All visualization layers (including dynamic gesture trajectory trails, attention heatmaps, and practice feedback) now utilize a standardized high-contrast 5-finger color palette:
- 🟠 **Thumb**: `#ff9f1c` (Neon Amber / Gold)
- 🔵 **Index**: `#00f0ff` (Electric Cyan)
- 🟢 **Middle**: `#20bf6b` (Vivid Emerald Green)
- 🟣 **Ring**: `#9b5de5` (Royal Purple)
- 🔴 **Pinky**: `#f72585` (Hot Pink / Magenta)
- ⚪ **Palm Base & Wrist**: `rgba(220, 235, 255, 0.65)` (Ice Silver)
- Dynamic trajectory overlays created by Contributor 2 should use these matching fingertip colors when rendering historical motion paths for index, thumb, or wrist.

### 3. Interactive 3D Hand Model & Animated Formation Guide Integration
- The frontend (`static/app.js`, `static/index.html`) now features:
  - `renderReferenceSkeleton(canvas, signNameOrLms, options)` with 3D yaw/pitch perspective projection and depth foreshortening.
  - An interactive 3D inspector modal with 360° drag orbit and angle presets (`Front`, `Side`, `Top`, `Isometric`).
  - An animated hand formation engine interpolating landmarks from neutral open hand to target handshape with Play/Pause controls.
  - A comprehensive fallback guide catalog (`FALLBACK_SIGN_GUIDE`) providing immediate anatomical directions, memory tips, and color-coded keypoints for all 26 letters and core static/dynamic phrases.
- **Sequence Buffer & NLP Alignment**: When the sequence buffer outputs multi-sign phrases or compound glosses (e.g. `["HELLO", "THANK YOU"]`), the UI inspector can receive and render canonical 3D guidance for each recognized segment.

### 4. Three.js WebGL Volumetric 3D Engine & OrbitControls Upgrade
- **Full WebGL 3D Integration**: The client-side visualizer has been upgraded to a true Three.js WebGL engine using locally-staged static/three.min.js (Three.js r128) and static/OrbitControls.js.
- **Volumetric 3D Geometry**: Hands are rendered with 21 lit joint spheres, metallic bone cylinders rotated with quaternions along parent-child vectors, and a translucent cybernetic palm plate spanning wrist and knuckles.
- **Interactive OrbitControls**: Signers can freely orbit in 360 degrees, zoom in/out with mouse-wheel (1.0x to 5.5x), pan, or snap to camera view presets (Front, Side, Top, Isometric).
- **Cubic-Eased Dynamic Formation Animation**: Real-time sinusoidal cubic easing interpolates landmarks between a neutral resting hand and the target sign shape with Play Guide / Pause Guide toggles.
- **Viewport Availability**: Embedded into the 3D Sign Inspector Modal (#modal-sign-canvas), Practice Studio Challenge Card (#practice-target-canvas), and Live Camera Reference Widget (#camera-ref-canvas).

### 5. Dedicated Hardcoded Port 8505 Configuration
- **Port Conflict Prevention**: To prevent clashes with standard ports (8080, 8000, 3000) used by other local development servers and proxies, UNMUTE now hardcodes and defaults to port **8505** in 
un.py and stop.py.
- **Integration Requirement**: All WebSocket connections (ws://127.0.0.1:8505/ws/...), REST API calls, and integration test suites should target port **8505** (http://localhost:8505).


---

# ACTIONABLE SCHEDULE INTEGRATION: FIT NEW ADDITIONS INTO CONTRIBUTOR 2 ROADMAP (WEEKS 3-8)

## Instructions for Contributor 2 and Assigned AI Agents
Contributor 1 has deployed three major platform capabilities:
1. **Universal Invariant Recognition Engine** (`sign_engine/asl_classifier.py`) based on Self-Phalange Bone Length Normalization ($||\mathbf{p}_{\text{TIP}} - \mathbf{p}_{\text{MCP}}|| / \sum \text{phalange segments}$) and Directional Phalanx Collinearity.
2. **Three.js WebGL Volumetric 3D Hand Model & OrbitControls** (`static/app.js`, `static/three.min.js`, `static/OrbitControls.js`) featuring 21 lit joint spheres, bone cylinders, translucent palm plate, camera presets, and cubic-eased dynamic hand formation animations.
3. **Dedicated Hardcoded Port 8505** (`run.py`, `stop.py`, `http://localhost:8505`) eliminating all local port clashes with 8080/8000/3000.

You MUST integrate these additions directly into your upcoming schedule as follows:

### Week 3 — Sequence Modeling & Invariant Dynamic Feature Dataset
- **Self-Phalange Normalization for Trajectories**: In your temporal sequence feature pipeline (`ml/data/prepare_dynamic_dataset.py`), do NOT normalize coordinates by raw bounding box pixels or palm ratios. Apply Contributor 1's invariant phalanx vector normalization across each frame in the rolling window (T = 30) so dynamic gestures (`HELLO`, `THANK YOU`, `YES`, `NO`) remain invariant to signer hand size and distance.
- **Dynamic Dataset Export**: Ensure sequence `.npz` archives use the 109-dim (ASL) and 228-dim (ISL) feature vectors generated from the normalized landmarks.

### Week 4 — Real-Time Dynamic Inference & High-Contrast 5-Finger Palette
- **Fingertip Motion Path Overlays**: When rendering historical motion trails in `temporal_tracker.py` or the client HUD:
  - Thumb trajectory: `#ff9f1c` (Amber)
  - Index trajectory: `#00f0ff` (Cyan)
  - Middle trajectory: `#20bf6b` (Green)
  - Ring trajectory: `#9b5de5` (Purple)
  - Pinky trajectory: `#f72585` (Hot Pink)
- **Port 8505 Client Socket**: Connect real-time dynamic inference WebSockets to `ws://127.0.0.1:8505/ws/live-stream`.

### Week 5 & Week 6 — Multi-Modal Fusion & Sequence-to-3D Guide Interaction
- **Compound Sign 3D Guide Dispatch**: When the sequence accumulator recognizes dynamic multi-sign glosses (e.g. `["HELLO", "THANK YOU"]`), expose structured tokens so the UI can invoke `openInspectorModal(signName)` for any token, allowing signers to view the WebGL 3D volumetric model and play the formation animation guide.
- **Port 8505 Test Client**: Configure all integration tests to target `http://localhost:8505`.

### Week 7 & Week 8 — Dynamic Model Evaluation & Final Delivery
- **Signer Invariance Benchmarking**: Evaluate dynamic recognition accuracy across diverse signers (slender, broad, and child hands) to verify that sequence models maintain the invariance guarantees established by Contributor 1.
- **Zero-Port-Clash Launch**: Ensure all scripts run out-of-the-box on dedicated port `8505`.

