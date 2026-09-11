
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

UNMUTE is currently focused on **American Sign Language (ASL)** and **Indian Sign Language (ISL)**.

Research and select practical datasets for the initial controlled vocabularies.

The datasets should be suitable for:

- ASL and ISL recognition
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

# MANDATORY WORKFLOW POLICY: STRICT BRANCH-FIRST DEVELOPMENT

## Core Directive for All AI Agents and Contributors

To protect the stability of the `main` branch, eliminate code conflicts, and prevent unverified or breaking changes from harming the core application, **all contributors and AI agents MUST adhere strictly to the branch-first development workflow**. 

Direct development on `main` is strictly prohibited. Branching is mandatory to ensure feature isolation, safe rollbacks, and team coordination.

### Independent History & Source of Truth Architecture:
- **Each Branch Tracks Its Own History**: Contributor branches (`contributor-1-ml-foundation`, `contributor-2-dynamic-nlp`, `contributor-3-nlp-integration`) track their own independent development history. Do not cross-merge other contributor branches into your branch; if another contributor's branch is empty or not yet active, leave it untouched.
- **`main` Is the Combined Source of Truth**: The `main` branch serves as the single unified source of truth combining verified, tested contributions from all branches.

### Required Cyclic Step-by-Step Workflow:

1. **Pull All Branches (Remote Sync & Upstream Merge)**:
   At the start of every work cycle or new task, fetch all remote refs and pull latest updates for both `main` and your feature branch, then merge `main` into your feature branch to stay synchronized with the combined source of truth:
   ```bash
   git fetch --all
   git checkout main
   git pull origin main
   git checkout contributor-1-ml-foundation
   git pull origin contributor-1-ml-foundation
   git merge main
   ```

2. **Develop & Implement Inside Your Branch**:
   Perform all code edits, model training, feature extraction, and experiments exclusively inside your assigned branch. Never edit directly on `main`.

3. **Test Thoroughly Inside Your Branch**:
   Run the complete test suite and verify that all unit, regression, and integration tests pass cleanly with zero errors before merging or pushing:
   ```bash
   pytest tests/ -v
   ```

4. **Commit Locally & Push Your Feature Branch**:
   Commit working units of code on your branch with descriptive, standardized commit messages, and push your feature branch to remote so its history is always backed up:
   ```bash
   git add <modified-files>
   git commit -m "feat/fix/docs(<scope>): clear description of work done"
   git push origin contributor-1-ml-foundation
   ```

5. **Merge into `main` Only When Everything Works**:
   Only after all tasks are completed, tested, and verified to be 100% functional, switch to `main` and merge your feature branch:
   ```bash
   git checkout main
   git merge contributor-1-ml-foundation
   pytest tests/ -v  # Final sanity check on main
   ```

6. **Push `main` to Remote**:
   Once the merge to `main` is validated and all tests pass without errors, push the updated `main` branch to remote origin:
   ```bash
   git push origin main
   ```

7. **Repeat Cycle for Every New Task**:
   When beginning the next task, repeat this exact loop: fetch and pull all branches (`main` and your feature branch), merge `main` into your feature branch, work, test, commit & push your feature branch, merge to `main`, and push `main`. All branches must always be pushed and pulled, not just `main`.

### Why This Is Mandatory:
- **All Branches Always Pushed & Pulled**: Pushing and pulling both your feature branch and `main` ensures that individual branch histories are preserved remotely, while `main` continuously reflects the combined, working source of truth.
- **Independent History Isolation**: Each contributor branch retains clean provenance and atomic responsibility without cross-pollinating unverified code.
- **Zero Harm to `main`**: Unfinished experiments, broken dependencies, or syntax regressions remain isolated in feature branches and never compromise the live application or other contributors' workflows.
- **Conflict Prevention**: Concurrent development across Contributors 1, 2, and 3 proceeds independently without git collisions.

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
- Any incompatibility between the dataset and the current feature pipeline.
- Exact files created or modified.

Do not proceed with model training until the dataset pipeline is understandable and reproducible.

---

## WEEK 3 — Static MLP Implementation

Focus on:

### 🚨 URGENT PRIORITY WORK — Core Sign Classifier Overhaul & Disambiguation Hierarchy

This task must be treated as your most important and urgent work in Week 3, providing the foundational accurate classification layer for Contributors 2 and 3 and the entire application:

- **Restructure Core Classifier (`sign_engine/asl_classifier.py`)**:
  - Overhaul `ASLClassifier` into a clean, robust **Finger-Extension Decision Hierarchy** (grouping by discrete finger extension states: 0, 1, 2, 3, 4 fingers extended, pinch/curled shapes, and fist families).
  - Eliminate widespread sign collisions across the entire application:
    - Disambiguate `K` vs `V` / `PEACE` / `U` / `R` / `2`.
    - Disambiguate `L` vs `D` / `1` (requiring true perpendicular 90° thumb extension).
    - Disambiguate `B` vs `5` / `STOP` (thumb folded flat across palm vs open palm).
    - Disambiguate `S` vs `M` / `N` (thumb wrapped horizontally across front).
    - Disambiguate `C` vs `L` (smooth open curved arc).
  - Ensure all candidate lists populate canonical synonyms/aliases (`PEACE` with `V` and `2`, `OKAY` with `F`, `STOP` with `B` and `5`, `1` with `D`, `0` with `O`) with properly calibrated confidence scores.
  - Expand the automated test suite in `tests/test_sign_engine.py` to assert correct recognition across all 26 letters and static phrases.

- Creating the PyTorch Dataset and DataLoader for both ASL (109-dim) and ISL (228-dim).
- Implementing the static MLPs:
  - `StaticASL_MLP` for unimanual ASL recognition (109-dim input, 41 classes).
  - `StaticISL_MLP` for bimanual ISL recognition (228-dim input, 44 classes).
- Implementing label encoding and decoding for both ASL and ISL canonical vocabularies.
- Implementing the training loop for both ASL and ISL models.
- Implementing validation for both models.
- Adding checkpoint saving (`asl_static_mlp.pt` and `isl_static_mlp.pt`).
- Ensuring the models can later be loaded independently for inference.

Keep the architectures simple and explainable.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 3

Before beginning Week 4, stop and report:

- Core sign classifier overhaul status and regression test results across all 26 letters and static phrases.
- Final MLP architectures (ASL and ISL).
- Input feature dimensionalities (109-dim ASL, 228-dim ISL).
- Number of output classes (41 classes for ASL, 44 classes for ISL).
- Loss function.
- Optimizer.
- Checkpoint strategy for both models.
- Training pipeline status.
- Whether complete training runs have successfully started for both ASL and ISL.
- Any errors or performance bottlenecks.
- Exact files created or modified.

---

## WEEK 4 — Training & Initial Evaluation

Focus on:

- Running initial training experiments for both ASL and ISL models.
- Monitoring training and validation loss for both models.
- Checking for overfitting on both datasets.
- Saving the best checkpoints (`asl_static_mlp.pt` and `isl_static_mlp.pt`).
- Running genuine evaluation on held-out data for both ASL and ISL.
- Generating for both ASL and ISL:
  - Accuracy
  - Precision
  - Recall
  - F1-score
  - Confusion matrix

Do not optimize endlessly for accuracy. First establish reliable baselines for both languages.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 4

Before beginning Week 5, stop and report:

- Whether training completed successfully for both ASL and ISL.
- Actual metrics obtained for both ASL and ISL models.
- Training versus validation behavior.
- Signs of overfitting or underfitting.
- Classes that perform poorly in ASL and ISL.
- Confusion matrix observations for both languages.
- Locations of the best model checkpoints (`asl_static_mlp.pt` and `isl_static_mlp.pt`).
- Whether the models are ready for backend integration.

Never report estimated, theoretical, or fabricated accuracy values.

---

## WEEK 5 — Model Improvement & Robustness

Focus on:

- Investigating weak classes in both ASL and ISL (including bimanual contact and occlusion patterns in ISL).
- Improving preprocessing where justified for 109-dim single-hand and 228-dim dual-hand pipelines.
- Adjusting the MLP architectures only if necessary.
- Improving data quality or class balance where feasible across both datasets.
- Comparing ASL against the legacy Random Forest baseline if technically meaningful.
- Robustness testing on samples not used during training, including single-hand fallback scenarios for ISL.

Avoid unnecessary complexity.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 5

Stop and report:

- Baseline versus improved model comparison for both ASL and ISL.
- Any preprocessing changes.
- Any architecture changes.
- Actual improvement or regression in evaluation metrics across both languages.
- Final recommendations for the static recognition models.
- Known limitations and failure cases (unimanual vs bimanual).

At this point, the team should be able to decide whether the static models are sufficiently reliable for integration.

---

## WEEK 6 — Integration Preparation

Focus on preparing the static models for the contributor responsible for backend integration.

Provide:

- Saved PyTorch model checkpoints (`asl_static_mlp.pt` and `isl_static_mlp.pt`).
- Label mappings for both ASL and ISL.
- Model-loading instructions for both models.
- Expected input formats and language mode selection (`mode: "ASL"` vs `mode: "ISL"`).
- Expected feature dimensionalities (109 dims for ASL, 228 dims for ISL).
- Prediction output format and class probability distributions.
- Confidence/probability handling and thresholding.
- Minimal inference examples for both ASL and ISL.

Do not heavily modify the backend unless explicitly coordinated with the backend contributor.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 6

Stop and report:

- Integration readiness status for both ASL and ISL models.
- Exact files required by the backend contributor.
- Example inference code for both languages.
- Dependencies required.
- Any compatibility concerns with the existing FastAPI pipeline and language switcher.
- Remaining integration risks.

---

## WEEK 7 — Integration Support & Real-World Testing

Coordinate with the contributor integrating the model into the real-time system.

Focus on:

- Supporting backend integration for both ASL and ISL pipelines.
- Verifying that live MediaPipe features match training features (single-hand 109 dims for ASL, dual-hand 228 dims for ISL).
- Testing real-time predictions in both ASL and ISL live modes.
- Identifying training-versus-inference preprocessing mismatches across both languages.
- Testing with different users where possible on both unimanual and bimanual signs.

Do not claim signer-independent performance unless the evaluation design genuinely supports that claim.

### ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 7

Stop and report:

- Whether the trained ASL and ISL MLPs successfully run in the real-time pipeline.
- Any integration bugs encountered in either language mode.
- Training-versus-live feature compatibility for 1-hand and 2-hand detection.
- Real-world observations for ASL and ISL.
- Known failure cases.
- Remaining work before final completion.

---

## WEEK 8 — Final Evaluation & Handover

Focus on:

- Final model evaluation for both ASL and ISL.
- Documenting actual results for both languages.
- Cleaning unnecessary experimental files.
- Ensuring reproducibility of both training pipelines.
- Preparing documentation for the final report and presentation covering dual-language capabilities.
- Clearly separating implemented functionality from future work.

### ⏸ FINAL PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 8

Provide a final contributor handover report containing:

1. What was implemented (ASL and ISL).
2. What was tested across both languages.
3. Actual evaluation results for both ASL and ISL models.
4. Datasets used for both languages.
5. Train/validation/test methodology.
6. Final MLP architectures (`StaticASL_MLP` and `StaticISL_MLP`).
7. Final model checkpoint locations (`asl_static_mlp.pt` and `isl_static_mlp.pt`).
8. Label mapping locations for both languages.
9. Exact files created or modified.
10. Backend integration instructions for both language modes.
11. Known limitations of each language model.
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

# COMPLETED IMPLEMENTATION REPORT (CONTRIBUTOR 1 — ML FOUNDATION & RECOGNITION)

## Key Milestones Delivered:
1. **Universal Person-Invariant Recognition Engine**:
   - Implemented Self-Phalange Bone Length Normalization in sign_engine/asl_classifier.py and sign_engine/feature_engineering.py.
   - Implemented Directional Phalanx Collinearity vectors ($\mathbf{v}_{	ext{prox}} \cdot \mathbf{v}_{	ext{dist}} > 0.35$) for robust curvature disambiguation (C/O vs U/V/B/R/L).
   - Validated across slender, broad, and child hand geometries (39/39 tests passing).
2. **Three.js WebGL Volumetric 3D Hand Visualizer & OrbitControls**:
   - Integrated Three.js r128 (static/three.min.js) and static/OrbitControls.js.
   - 21 lit joint spheres, 21 bone cylinders, and cybernetic translucent palm plate.
   - Smooth 360-degree drag orbit, mouse-wheel zoom (1.0x - 5.5x), and camera presets (Front, Side, Top, Isometric).
   - Dynamic cubic-eased hand formation animation guide with Play/Pause controls.
   - High-contrast 5-finger color system across all UI viewports.
3. **Dedicated Port 8505 Configuration**:
   - Hardcoded UNMUTE_PORT = 8505 in 
un.py and stop.py to prevent port collisions with 8080, 8000, and 3000.
   - All client relative routing and documentation synchronized to port 8505.


---

# ACTIONABLE SCHEDULE STATUS & HANDOFF MATRIX (CONTRIBUTOR 1)

## Delivered Components in Main Baseline:
1. **Universal Invariant Recognition Engine** (`sign_engine/asl_classifier.py`):
   - Self-Phalange Bone Ratio Normalization ($||\mathbf{p}_{\text{TIP}} - \mathbf{p}_{\text{MCP}}|| / \sum \text{bones}$).
   - Directional Phalanx Collinearity ($\mathbf{v}_{\text{prox}} \cdot \mathbf{v}_{\text{dist}} > 0.35$).
   - Invariant unit tests in `tests/test_sign_engine.py` (39/39 passing).
2. **Three.js WebGL Volumetric 3D Hand Visualizer & OrbitControls**:
   - `static/three.min.js` and `static/OrbitControls.js` staged locally.
   - Volumetric joint spheres, bone cylinders, translucent palm plate.
   - Smooth 360° mouse drag, wheel zoom, camera presets, and cubic-eased animation guide.
   - Deployed in 3D Inspector Modal, Practice Studio Card, and Live Camera Widget.
3. **Dedicated Port 8505**:
   - Hardcoded `UNMUTE_PORT = 8505` in `run.py` and `stop.py`.
   - Complete avoidance of port 8080/8000 collisions.

## Handoff Coordination for Contributors 2 & 3:
- Contributor 2 can consume normalized landmarks for rolling dynamic sequence models in Weeks 3–6.
- Contributor 3 can connect NLP sentence tokens and Practice Studio verification to the WebGL 3D Inspector on port 8505 in Weeks 3–8.

