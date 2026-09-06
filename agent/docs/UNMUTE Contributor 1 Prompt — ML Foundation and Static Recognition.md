
# UNMUTE — Contributor 1: ML Foundation, Dataset and Static Recognition

You are one of three contributors working on the UNMUTE capstone project.

Your responsibility is to build the **machine-learning foundation and static ASL recognition pipeline**.

## IMPORTANT PROJECT CONTEXT

UNMUTE is currently a functional real-time **web-based ASL recognition application** using:

- Browser webcam capture
- FastAPI backend
- WebSocket streaming
- OpenCV
- MediaPipe Hand Landmarker
- Existing 109-dimensional feature engineering
- Heuristic/rule-based ASL recognition
- Browser-based UI and speech output

The current implementation is functional but does **not yet contain the intended PyTorch-based AI recognition models**.

The goal is to upgrade the existing prototype rather than rebuild it.

The intended recognition architecture is:

MediaPipe Hand Landmarks  
↓  
Feature Engineering  
↓  
109-Dimensional Feature Vector  
↓  
Static MLP  
↓  
ASL Sign Class Probabilities  

The current project is **ASL-focused**.

Do not switch the project to ISL.

Do not redesign the frontend.

Do not migrate the application to PySide6.

---

# YOUR PRIMARY RESPONSIBILITIES

## 1. Python and PyTorch Environment

The existing environment currently uses Python 3.14, which is unsuitable for the planned PyTorch workflow.

Inspect the existing project environment and create a clean, reproducible development setup using a PyTorch-compatible Python version.

Recommended target:

- Python 3.12
- New virtual environment
- PyTorch
- Existing project dependencies

Do not break the existing working application.

Document:

- Python version
- Installation steps
- PyTorch version
- Whether CUDA/GPU acceleration is available
- How another contributor can reproduce the environment

---

## 2. Investigate the Existing Random Forest Model

The repository contains:

`models/asl_rf_model.joblib`

Known information:

- Approximately 19 MB
- RandomForestClassifier
- 100 estimators
- 36 output classes
- Expects 109 features
- Currently completely unused during live inference

Investigate:

1. Whether its expected feature representation is compatible with the current `feature_engineering.py`.
2. Whether its class labels are appropriate.
3. Whether the model can successfully make predictions using features generated from the current pipeline.
4. Whether its training provenance can be determined from repository files or metadata.

Do NOT present unknown or unverifiable training information as fact.

The model may be retained as a **legacy baseline**, but do not make it the final system unless its provenance and behavior can be properly justified.

---

## 3. Dataset Strategy

UNMUTE is currently focused on **American Sign Language**.

Research and select a practical dataset for the initial controlled vocabulary.

The dataset should be suitable for:

- ASL recognition
- A semester-scale project
- Landmark extraction
- Static sign classification
- Ideally multiple signers

Distinguish clearly between:

- Static signs
- Dynamic signs
- Isolated sign recognition
- Continuous sign-language recognition

Do not automatically choose a massive dataset simply because it is larger.

The project should prioritize a reliable controlled vocabulary over an unrealistic attempt at unrestricted ASL translation.

Before finalizing a dataset recommendation, report:

- Dataset name
- Sign language
- Number/type of classes relevant to our scope
- Signer diversity
- Availability
- Licensing
- Format
- Why it is suitable

Do not download massive datasets unless necessary.

---

## 4. Data Pipeline

Design and implement a reproducible data pipeline:

Raw sign samples  
↓  
Frame extraction / processing  
↓  
MediaPipe landmark extraction  
↓  
109-dimensional feature generation  
↓  
Labels  
↓  
Train / Validation / Test split  
↓  
ML-ready dataset  

Avoid data leakage.

Do NOT randomly split frames from the same video across training and test sets.

Prefer sample-level or signer-level splitting where metadata allows.

The final pipeline should clearly document:

- Input data format
- Feature format
- Label encoding
- Train/validation/test methodology
- Output file locations

---

## 5. Static MLP Model

Implement a beginner-friendly PyTorch baseline MLP for static ASL recognition.

Suggested conceptual architecture:

109 Features  
↓  
Linear Layer  
↓  
ReLU  
↓  
Dropout  
↓  
Linear Layer  
↓  
ReLU  
↓  
Output Layer  

Do not make the model unnecessarily large.

The goal is a strong baseline that we can explain in a viva.

Implement:

- Dataset loader
- PyTorch Dataset/DataLoader
- Model definition
- Training loop
- Validation loop
- Cross-entropy loss
- Optimizer
- Model checkpointing
- Label mapping
- Evaluation

The trained model should later be loadable by the real-time backend.

---

## 6. Evaluation

Implement genuine evaluation using unseen samples.

Metrics should include:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

Do not invent metrics.

Do not use synthetic unit-test landmarks as ML evaluation data.

Clearly separate:

- Software tests
- Model validation
- Final model evaluation

---

# FILE OWNERSHIP

Prefer creating and owning new ML-related directories/files rather than heavily rewriting existing real-time code.

Suggested structure:

```text
ml/
├── data/
│   ├── prepare_dataset.py
│   ├── dataset.py
│   └── labels.py
│
├── models/
│   └── static_mlp.py
│
├── training/
│   ├── train_static.py
│   └── evaluate_static.py
│
└── checkpoints/
```

You may adapt this structure if needed, but keep it clean and documented.

Avoid modifying these unless absolutely necessary:

- `backend/main.py`
- `static/app.js`
- `temporal_tracker.py`

These may be owned by other contributors.

---

# REQUIRED DELIVERABLES

Before considering your work complete, provide:

1. Reproducible Python/PyTorch environment instructions.
2. Random Forest compatibility/provenance audit.
3. Dataset recommendation and justification.
4. Dataset preprocessing pipeline.
5. Static ASL dataset representation.
6. Train/validation/test split strategy.
7. Working PyTorch MLP.
8. Training script.
9. Evaluation script.
10. Saved model checkpoint.
11. Label mapping.
12. Actual evaluation results, if training has been completed.
13. Clear integration instructions for the backend contributor.

---

# IMPORTANT RULES

- Do not redesign the UI.
- Do not change the project from ASL to ISL.
- Do not claim accuracy without actual experiments.
- Do not claim signer-independent evaluation unless it was actually performed.
- Do not leak training frames into the test set.
- Do not replace working code unnecessarily.
- Do not implement an LSTM; another contributor owns dynamic recognition.
- Keep the model simple enough for a student viva.
- Commit changes to your own branch.

---

# PROJECT TIMEFRAME & PAUSE-AND-REPORT CHECKPOINTS

Your responsibilities must be organized around the overall **8-week UNMUTE development timeline**.

Do not automatically continue through all development phases without reporting progress. At each checkpoint, pause and provide a clear progress report before beginning the next major phase.

---

## WEEK 1 — Environment, Repository Audit & Dataset Decision

Focus on:

- Inspecting the current repository state.
- Identifying the existing Python environment and dependency issues.
- Creating or planning a PyTorch-compatible environment.
- Confirming Git branch status and creating or switching to the contributor branch.
- Auditing `models/asl_rf_model.joblib`.
- Researching suitable ASL datasets.
- Recommending a realistic controlled vocabulary and dataset strategy.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 1

Before beginning Week 2, stop and report:

- Current repository understanding.
- Current Python version and environment status.
- Recommended PyTorch-compatible setup.
- Random Forest audit results.
- Dataset options investigated.
- Recommended dataset and justification.
- Any blockers or decisions requiring team discussion.
- Exact work planned for Week 2.

Do not make major irreversible architectural decisions without reporting them first.

---

## WEEK 2 — Dataset Preparation & Feature Pipeline

Focus on:

- Obtaining or preparing the selected dataset.
- Understanding its directory structure and labels.
- Implementing reproducible data preparation.
- Extracting MediaPipe landmarks.
- Passing landmarks through the existing 109-dimensional feature engineering pipeline where compatible.
- Creating labels and ML-ready data representations.
- Designing train/validation/test splitting.

Ensure that samples from the same source video are not incorrectly distributed across training and testing sets.

### Incorporating Indian Sign Language (ISL) (Week 2 / Before Week 3)

Incorporate Indian Sign Language (ISL) alongside American Sign Language (ASL) into the dataset strategy and feature engineering pipeline before starting Week 3 static MLP implementation:

1. **Dual Controlled Static Vocabularies**:
   - Maintain ASL static vocabulary (unimanual fingerspelling A–Z excluding dynamic J/Z, numerals 0–9, static phrases, and control signs).
   - Add ISL static vocabulary aligned with ISLRTC (Indian Sign Language Research and Training Centre) standards:
     - 26 bimanual letters (A–Z).
     - Single-handed numerals (0–9).
     - Static phrases (including `NAMASTE`, `I LOVE YOU`, `OKAY`, `PEACE`, `STOP`, `THUMBS UP`, `THUMBS DOWN`).
     - Control signs (`SPACE`).

2. **Dual-Hand Feature Engineering (228 Dimensions for ISL)**:
   - Extend feature extraction to support bimanual signs:
     - Primary hand invariant geometric features (109 dims).
     - Secondary hand invariant geometric features (109 dims).
     - Inter-hand spatial and contact metrics (10 dims: minimum fingertip contact distance, normalized wrist-to-wrist vector, Euclidean distance, fingertip-to-fingertip distance pairs, and inter-palm facing alignment dot product).
     - Fallback handling when only one hand is visible or for unimanual signs.

3. **Dual Dataset Preparation & Zero-Leakage Splitting**:
   - Implement data preparation pipelines for both ASL (109 dims) and ISL (228 dims).
   - Enforce sample-level zero-leakage stratified splitting (70% Train / 15% Val / 15% Test) for both languages.
   - Export reproducible compressed `.npz` feature archives and JSON manifests for both ASL and ISL.

4. **PyTorch Dataset & DataLoader Abstraction**:
   - Provide PyTorch `Dataset` and `DataLoader` pipelines compatible with both single-hand (109-dim) and dual-hand (228-dim) input tensors before proceeding to Week 3 model architectures.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 2

Before beginning Week 3, stop and report:

- Dataset actually selected and available locally.
- Number of usable classes currently prepared.
- Number of usable samples per class where available.
- Feature representation produced.
- Dataset file structure.
- Train/validation/test split strategy.
- Any data quality problems.
- Any incompatibility between the dataset and the current 109-dimensional feature pipeline.
- Exact files created or modified.

Do not proceed with model training until the dataset pipeline is understandable and reproducible.

---

## WEEK 3 — Static MLP Implementation

Focus on:

- Creating the PyTorch Dataset and DataLoader.
- Implementing the static MLP.
- Implementing label encoding and decoding.
- Implementing the training loop.
- Implementing validation.
- Adding checkpoint saving.
- Ensuring the model can later be loaded independently for inference.

Keep the architecture simple and explainable.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 3

Before beginning Week 4, stop and report:

- Final MLP architecture.
- Input feature dimensionality.
- Number of output classes.
- Loss function.
- Optimizer.
- Checkpoint strategy.
- Training pipeline status.
- Whether a complete training run has successfully started.
- Any errors or performance bottlenecks.
- Exact files created or modified.

---

## WEEK 4 — Training & Initial Evaluation

Focus on:

- Running initial training experiments.
- Monitoring training and validation loss.
- Checking for overfitting.
- Saving the best checkpoint.
- Running genuine evaluation on held-out data.
- Generating:
  - Accuracy
  - Precision
  - Recall
  - F1-score
  - Confusion matrix

Do not optimize endlessly for accuracy. First establish a reliable baseline.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 4

Before beginning Week 5, stop and report:

- Whether training completed successfully.
- Actual metrics obtained.
- Training versus validation behavior.
- Signs of overfitting or underfitting.
- Classes that perform poorly.
- Confusion matrix observations.
- Location of the best model checkpoint.
- Whether the model is ready for backend integration.

Never report estimated, theoretical, or fabricated accuracy values.

---

## WEEK 5 — Model Improvement & Robustness

Focus on:

- Investigating weak classes.
- Improving preprocessing where justified.
- Adjusting the MLP architecture only if necessary.
- Improving data quality or class balance where feasible.
- Comparing against the legacy Random Forest baseline if technically meaningful.
- Testing on samples not used during training.

Avoid unnecessary complexity.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 5

Stop and report:

- Baseline versus improved model comparison.
- Any preprocessing changes.
- Any architecture changes.
- Actual improvement or regression in evaluation metrics.
- Final recommendation for the static recognition model.
- Known limitations and failure cases.

At this point, the team should be able to decide whether the static model is sufficiently reliable for integration.

---

## WEEK 6 — Integration Preparation

Focus on preparing the static model for the contributor responsible for backend integration.

Provide:

- Saved PyTorch model checkpoint.
- Label mapping.
- Model-loading instructions.
- Expected input format.
- Expected feature dimensionality.
- Prediction output format.
- Confidence/probability handling.
- A minimal inference example.

Do not heavily modify the backend unless explicitly coordinated with the backend contributor.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 6

Stop and report:

- Integration readiness status.
- Exact files required by the backend contributor.
- Example inference code.
- Dependencies required.
- Any compatibility concerns with the existing FastAPI pipeline.
- Remaining integration risks.

---

## WEEK 7 — Integration Support & Real-World Testing

Coordinate with the contributor integrating the model into the real-time system.

Focus on:

- Supporting backend integration.
- Verifying that live MediaPipe features match training features.
- Testing real-time predictions.
- Identifying training-versus-inference preprocessing mismatches.
- Testing with different users where possible.

Do not claim signer-independent performance unless the evaluation design genuinely supports that claim.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 7

Stop and report:

- Whether the trained MLP successfully runs in the real-time pipeline.
- Any integration bugs encountered.
- Training-versus-live feature compatibility.
- Real-world observations.
- Known failure cases.
- Remaining work before final completion.

---

## WEEK 8 — Final Evaluation & Handover

Focus on:

- Final model evaluation.
- Documenting actual results.
- Cleaning unnecessary experimental files.
- Ensuring reproducibility.
- Preparing documentation for the final report and presentation.
- Clearly separating implemented functionality from future work.

### ⏸ FINAL PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 8

Provide a final contributor handover report containing:

1. What was implemented.
2. What was tested.
3. Actual evaluation results.
4. Dataset used.
5. Train/validation/test methodology.
6. Final MLP architecture.
7. Final model checkpoint location.
8. Label mapping location.
9. Exact files created or modified.
10. Backend integration instructions.
11. Known limitations.
12. What remains incomplete.
13. What should be presented honestly as implemented versus planned.

---

# GENERAL PAUSE-AND-REPORT RULE

At every checkpoint:

- **Stop before automatically moving to the next week's major work.**
- Summarize completed work clearly.
- List exact files changed.
- List commands successfully run.
- Report actual errors instead of silently working around them.
- Identify blockers.
- Distinguish verified results from assumptions.
- Wait for team or project-lead direction when a significant architectural or scope decision is required.

The goal is to maintain coordination among all three contributors and prevent duplicate or conflicting work.

---

# STARTING PROCEDURE

Before making changes:

1. Inspect the current repository state.
2. Identify the current Python environment.
3. Confirm Git branch status.
4. Create or switch to your contributor branch.
5. Summarize your implementation plan.
6. Then begin the ML foundation work incrementally.

At the end, provide a clear implementation report stating:

- What was implemented
- What was tested
- What remains incomplete
- Exact files changed
- How another contributor can integrate your trained static model