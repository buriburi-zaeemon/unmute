# UNMUTE — Contributor 3: Sentence Formation, System Integration and Evaluation

You are one of three contributors working on the UNMUTE capstone project.

Your primary responsibility is to develop the **sign-sequence-to-language layer**, prepare the system for integration, and strengthen testing and evaluation.

---

# IMPORTANT PROJECT CONTEXT

UNMUTE is an ASL-focused, real-time sign-to-language system.

The core conceptual distinction is:

```text
AI Recognition Model
        ↓
Recognized ASL Sign Labels
        ↓
Sequence Buffer
        ↓
Language Processing
        ↓
Natural-Language Sentence
```

The recognition model does **NOT** directly generate the final English sentence.

For example:

```text
Recognized Signs:
I → GO → HOME → YESTERDAY

Language Layer:
I went home yesterday.
```

The current project already has:

- FastAPI backend
- WebSocket real-time recognition pipeline
- Browser UI
- Raw sign/character accumulation
- Browser speech synthesis

But it currently lacks:

- Structured sign-token handling
- Rule-based sentence formation
- NLP refinement
- Real end-to-end system evaluation

Your role is to build these missing layers while coordinating with the other contributors.

Do not redesign the entire application.

Do not change the project from ASL to ISL.

Do not use a large language model to compensate for poor recognition.

---

# IMPORTANT RULES

- Do not claim unrestricted ASL-to-English or ISL-to-English translation.
- Do not use an LLM to guess missing signs.
- Do not invent model performance metrics.
- Do not redesign the existing web UI unnecessarily.
- Do not replace browser speech synthesis without team approval.
- Do not modify another contributor's ML code unnecessarily.
- Keep the language layer deterministic and explainable.
- Clearly distinguish actual implementation from planned work.
- Work on your own Git branch.
- Pause and report at every checkpoint before proceeding to the next major phase.

---

# MANDATORY WORKFLOW POLICY: STRICT BRANCH-FIRST DEVELOPMENT

## Core Directive for All AI Agents and Contributors

To protect the stability of the `main` branch, eliminate code conflicts, and prevent unverified or breaking changes from harming the core application, **all contributors and AI agents MUST adhere strictly to the branch-first development workflow**. 

Direct development on `main` is strictly prohibited. Branching is mandatory to ensure feature isolation, safe rollbacks, and team coordination.

### Independent History & Source of Truth Architecture:
- **Each Branch Tracks Its Own History**: Contributor branches (`contributor-1-ml-foundation`, `contributor-2-dynamic-nlp`, `contributor-3-nlp-integration`) track their own independent development history. Do not cross-merge other contributor branches into your branch; if another contributor's branch is empty or not yet active, leave it untouched.
- **`main` Is the Combined Source of Truth**: The `main` branch serves as the single unified source of truth combining verified, tested contributions from all branches.

### Required Step-by-Step Workflow:

1. **Pull Latest Changes from All Branches**:
   At the start of every work cycle or task, ensure your local repository has the full remote state:
   ```bash
   git fetch --all
   git pull
   ```

2. **Switch to Your Dedicated Feature Branch**:
   Always switch to your contributor-assigned branch before making any edits or starting new tasks:
   - Contributor 1: `git checkout contributor-1-ml-foundation`
   - Contributor 2: `git checkout contributor-2-dynamic-nlp`
   - Contributor 3: `git checkout contributor-3-nlp-integration`

3. **Develop & Implement Inside Your Branch**:
   Perform all code edits, model training, feature extraction, and experiments exclusively inside your assigned branch.

4. **Test Thoroughly Before Any Merging**:
   Run the complete test suite and verify that all unit, regression, and integration tests pass cleanly with zero errors:
   ```bash
   pytest tests/ -v
   ```

5. **Commit Locally in Atomic Steps**:
   Commit working units of code on your branch with descriptive, standardized commit messages:
   ```bash
   git add <modified-files>
   git commit -m "feat/fix/docs(<scope>): clear description of work done"
   ```

6. **Merge into `main` Only When Everything Works**:
   Only after all tasks are completed, tested, and verified to be 100% functional:
   ```bash
   git checkout main
   git merge <your-contributor-branch>
   pytest tests/ -v  # Final sanity check on main
   ```

7. **Push to Remote**:
   Once the merge to `main` is validated and all tests pass without errors, push the updated `main` branch:
   ```bash
   git push origin main
   ```

### Why This Is Mandatory:
- **Independent History Isolation**: Each contributor branch retains clean provenance and atomic responsibility without cross-pollinating unverified code.
- **Zero Harm to `main`**: Unfinished experiments, broken dependencies, or syntax regressions remain isolated in feature branches and never compromise the live application or other contributors' workflows.
- **Conflict Prevention**: Concurrent development across Contributors 1, 2, and 3 proceeds independently without git collisions.

---

# STARTING PROCEDURE

Before making changes:

1. Inspect the current repository state.
2. Confirm Git branch status.
3. Create or switch to your contributor branch.
4. Inspect the current text accumulation and backend flow.
5. Summarize the Week 1 implementation plan.
6. Begin Week 1.
7. Stop at the Week 1 pause-and-report checkpoint.

Do not rush directly to Week 8.

Follow the timeline incrementally and coordinate with the other two contributors as their ML and dynamic-recognition components become available.

---

# PROJECT TIMELINE AND RESPONSIBILITIES

Your work is organized around the overall eight-week UNMUTE development timeline.

Do not blindly complete all eight weeks at once.

At every explicit checkpoint, **pause and report the current repository state, completed work, test results, blockers, and recommended next step before proceeding**.

---

# WEEK 1 — PROJECT AUDIT AND INTEGRATION PLANNING

## Goals

Understand exactly how the current application handles recognized signs, text accumulation, backend communication, and speech.

## Tasks

Inspect:

- `static/app.js`
- `backend/main.py`
- Any existing sequence logic
- Any subtitle-generation logic
- Existing tests

Determine:

1. How predictions currently travel from the recognition engine to the frontend.
2. How recognized signs or characters are accumulated.
3. How duplicate predictions are suppressed.
4. Where a structured sequence buffer should eventually connect.
5. Where the sentence-processing layer should connect to the FastAPI architecture.
6. How browser speech synthesis currently receives text.

The current flow approximately resembles:

```text
Prediction
↓
Append directly to string
```

This is insufficient for:

```text
I → GO → HOME → YESTERDAY
```

Your goal is to identify a clean transition toward:

```text
Recognition Output
↓
Stable Sign Token
↓
Sequence Buffer
↓
Sentence Processor
↓
Final Sentence
↓
Frontend + Speech
```

Do not modify the recognition architecture unnecessarily.

## Deliverable

Create a short technical audit documenting:

- Current accumulation flow
- Current API/WebSocket flow
- Current speech flow
- Recommended integration points
- Files likely to require modification

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 1

Stop before implementing major language-processing changes.

Report:

1. Current repository state.
2. Exact current text/sign accumulation behavior.
3. Recommended structured token flow.
4. Recommended backend integration point.
5. Files inspected.
6. Files planned for modification.
7. Any dependency on Contributor 1 or Contributor 2.

Wait for review/approval before proceeding if coordination decisions are required.

---

# WEEK 2 — STRUCTURED SIGN TOKENS AND SEQUENCE INTERFACE

## Goals

Design the internal interface between recognition and sentence formation.

The language-processing component must receive structured sign tokens rather than directly depending on raw frontend strings.

Example:

```python
["I", "GO", "HOME", "YESTERDAY"]
```

Create a clean, documented interface.

For example:

```python
process_sign_sequence(
    ["I", "GO", "HOME", "YESTERDAY"]
)
```

Expected output:

```text
I went home yesterday.
```

The exact implementation may differ.

## Requirements

The interface should be:

- Modular
- Vocabulary-aware
- Extensible
- Easy to test
- Independent from ML implementation details

Coordinate the expected token format with the recognition contributors.

Do not assume unsupported vocabulary exists.

The supported vocabulary must ultimately depend on the actual recognition models implemented by Contributors 1 and 2.

## Deliverables

Define:

- Token representation
- Token normalization strategy
- Sequence input format
- Output format
- Unknown-token behavior
- Duplicate-token behavior where relevant
- Clear API contract

### Incorporating Indian Sign Language (ISL) (Week 2 / Before Week 3)

Incorporate Indian Sign Language (ISL) alongside American Sign Language (ASL) into the structured token format and sequence interface before starting Week 3 rule-based sentence formation:

1. **Dual-Language Structured Token Schema**:
   - Extend the token contract (e.g. `Token`) to support an explicit language identifier or mode tag (`language: "ASL" | "ISL"`), alongside `text`, `confidence`, `sign_type` (`letter`, `number`, `phrase`, `dynamic`, `control`), and `timestamp`.
   - Ensure the token schema handles both single-handed ASL signs and bimanual ISL signs emitted from the recognition layers without format divergence.

2. **ISL-Specific Lexicon and Greeting Patterns**:
   - Incorporate ISL static phrases (e.g. `NAMASTE`, `I LOVE YOU`, `OKAY`, `PEACE`, `STOP`, `THUMBS UP`, `THUMBS DOWN`) and culturally distinct greeting patterns into the token normalization dictionary.
   - Account for ISL fingerspelling differences (complete 26-letter alphabet A–Z) compared to ASL (which reserves J and Z for dynamic tracking).

3. **Language Mode Synchronization**:
   - Design the sequence buffer and sentence processing interface to be language-aware, allowing real-time switching between ASL and ISL sentence-formation pipelines based on the active client mode.
   - Specify fallback and validation rules when an incoming token's language tag does not match the active sequence buffer language context.

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 2

Stop and report:

1. Final proposed token format.
2. Example inputs and outputs.
3. Integration contract for Contributors 1 and 2.
4. How unsupported tokens are handled.
5. Whether any changes are required in the backend.
6. Unit-test plan for the sequence interface.

Do not begin major grammar implementation until the token interface is stable.

---

# WEEK 3 — RULE-BASED SENTENCE FORMATION

### 🚨 URGENT PRIORITY WORK — System-Wide Classifier Overhaul Integration, Practice Studio Aliasing & Subtitle Verification

This task must be treated as your most important and urgent work in Week 3, coordinated directly with Contributor 1's overhaul of the core sign recognition classifier (`sign_engine/asl_classifier.py`):

1. **Interactive Practice Studio Overhaul (`static/app.js`)**:
   - Implement the authoritative **Handshape Alias Matrix** (`SIGN_ALIASES`: `PEACE` ↔ `V` ↔ `2`, `OKAY` ↔ `F` ↔ `9`, `STOP` ↔ `5` ↔ `B`, `1` ↔ `D`, `0` ↔ `O`) in `evaluatePracticeMatch()`.
   - Ensure the pose-matching meter reliably scores ≥ 90% when holding the correct physical handshape for both ASL and ISL challenge items.
   - Refine the challenge pool generation in `nextPracticeChallenge()` to focus on static verifiable signs within the single-frame camera loop.

2. **Live Camera WebSocket Pipeline Validation (`/ws/live-stream` & `static/app.js`)**:
   - Verify that the live stream WebSocket properly passes the newly disambiguated, stabilized signs into the **Live Letter Accumulator**, **Sentence Composer**, and **Browser Text-To-Speech (TTS)** without spurious letter jumping or word corruption.
   - Ensure TTS and UI display render clean, stable tokens for both ASL and ISL modes.

3. **Offline Video Processing & Subtitle Pipeline Guarantee (`sign_engine/video_processor.py`)**:
   - Test and verify that uploaded video files processed through `VideoProcessor` leverage the overhauled sign classifier to produce accurate, uncorrupted `.srt`, `.vtt`, `.json`, and `.txt` subtitle exports and translation transcripts.

4. **System-Wide End-to-End Integration Tests**:
   - Write integration tests asserting that the newly overhauled classifier predictions flow correctly through the WebSocket, REST endpoints, sequence buffers, and subtitle exporters.

## Goals

Implement the initial controlled-vocabulary sentence-processing layer for both ASL and ISL.

The system must use deterministic and explainable transformations.

Do **NOT** use an LLM as a substitute for incorrect sign recognition.

Do **NOT** hallucinate missing signs.

The intended pipeline is:

```text
Sign Tokens (ASL / ISL)
↓
Token Normalization & Language Tagging
↓
Phrase Mapping (ASL & ISL Lexicons)
↓
Language-Specific Grammar Transformation (ASL / ISL Rules)
↓
Capitalization
↓
Punctuation
↓
Final Sentence
```

Examples:

1. **ASL Example**:
   ```python
   ["I", "GO", "HOME", "YESTERDAY"]
   ```
   Could become:
   ```text
   I went home yesterday.
   ```

2. **ISL Example**:
   ```python
   ["NAMASTE", "I", "HELP", "YOU"]
   ```
   Could become:
   ```text
   Namaste, I will help you.
   ```

This does not mean the system supports unrestricted ASL-to-English or ISL-to-English translation.

It is a **controlled-vocabulary sentence-formation system** supporting both sign languages.

## Suggested Structure

```text
nlp/
├── sentence_processor.py
├── grammar_rules.py        # Grammar rules for ASL and ISL
├── vocabulary.py           # Controlled vocabularies for ASL and ISL
└── tests/
```

You may adapt this structure if necessary.

## Requirements

Implement explainable rules for supported patterns across both languages.

Examples may include:

- Pronoun handling (ASL & ISL)
- Basic verb transformations
- Time-word positioning (ASL Topic-Time-Comment structure)
- Subject-Object-Verb (SOV) structure adjustments for ISL
- Phrase mappings (including ASL phrases and ISL phrases such as `NAMASTE`)
- Capitalization
- Punctuation

Every rule should be understandable and defensible in a viva.

## Deliverables

- Working sentence processor supporting both ASL and ISL
- Vocabulary configuration for both languages
- Grammar-rule module with language-aware dispatch
- Example transformations for both ASL and ISL
- Unit tests for both language pipelines

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 3

Report:

1. Supported sentence patterns for both ASL and ISL.
2. Rules implemented across both languages.
3. Example transformations (ASL and ISL).
4. Unsupported patterns.
5. Unit-test results for both language pipelines.
6. Known limitations.
7. Any vocabulary assumptions that need confirmation from the ML contributors.
8. System-wide classifier overhaul integration results (Practice Studio matching, Live Stream WebSocket accumulation, and Video Processor subtitle exports).

Do not claim unrestricted natural-language translation.

---

# WEEK 4 — FASTAPI AND SYSTEM INTEGRATION PREPARATION

## Goals

Prepare clean integration points between:

```text
Recognition (ASL / ISL)
↓
Stable Sign Token (with language mode tag)
↓
Sequence Buffer
↓
Sentence Processor
↓
WebSocket/API Response
↓
Frontend
```

Inspect the current FastAPI architecture carefully.

Prefer adding small, clean integration points rather than rewriting the backend.

Coordinate shared changes with the contributor responsible for real-time recognition, ensuring language mode selection (`mode: "ASL"` vs `mode: "ISL"`) is seamlessly propagated through the sequence buffer and sentence processor.

## Requirements

If the final ML models are not yet available:

- Use clearly labelled mock inputs for development and testing across both ASL and ISL.
- Never present mock recognition as actual AI performance.

The sentence-processing layer should be independently testable for both sign languages.

## Deliverables

- Backend integration design supporting both ASL and ISL streams
- Sequence-buffer integration strategy with language-mode awareness
- API/WebSocket contract where needed (including language mode headers)
- Minimal integration implementation where safe
- Integration tests using controlled test tokens from both ASL and ISL

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 4

Report:

1. Current integration architecture (supporting ASL and ISL).
2. Exact integration points added or proposed.
3. Whether the real recognition contributors can now provide tokens directly for both languages.
4. Backend files modified.
5. Integration-test results for both language flows.
6. Remaining dependencies before full end-to-end integration.

---

# WEEK 5 — SPEECH FLOW AND FRONTEND CONNECTION

## Goals

Ensure the application speaks the **final processed sentence**, not raw sign tokens, for both ASL and ISL.

The existing application already uses:

```javascript
window.speechSynthesis
```

This is functional.

Do **NOT** replace it with `pyttsx3` unless the team explicitly changes the application architecture.

The desired flow is:

```text
Recognized Sign Sequence (ASL / ISL)
↓
Sentence Processing (Language-Specific Rules)
↓
Final Sentence
↓
Display
↓
Speak (Browser Speech Synthesis)
↓
Replay / Clear
```

## Tasks

Inspect and improve the connection between:

- Processed sentence (ASL and ISL)
- Frontend display and subtitle rendering
- Speech synthesis (with language/voice selection where available)
- Replay behavior for both languages
- Clear behavior for both languages

Do not redesign the UI unnecessarily.

Focus on functional correctness.

## Deliverables

- Final sentence passed correctly to frontend for both ASL and ISL
- Speech uses processed output across both language modes
- Clear behavior resets relevant state
- Replay uses the intended final sentence for both languages
- Relevant tests or manual test procedures covering both ASL and ISL

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 5

Report:

1. Whether processed sentences reach the frontend correctly for both ASL and ISL.
2. Whether speech uses processed sentences across both language modes.
3. Clear/replay behavior.
4. Files changed.
5. Manual tests performed for ASL and ISL.
6. Remaining integration problems.

---

# WEEK 6 — TESTING AND END-TO-END INTEGRATION SUPPORT

## Goals

Strengthen the system testing strategy across both ASL and ISL.

Clearly separate:

### Unit Tests

Test:

- Sentence processing (ASL and ISL grammar rules)
- Token normalization & language tagging
- Grammar rules (ASL topic-comment, ISL SOV adjustments)
- Phrase mappings (ASL and ISL lexicons)
- API contracts

### Integration Tests

Test:

```text
Recognition Output (ASL / ISL)
↓
Sequence Buffer
↓
Sentence Processor
↓
Backend/API Response
↓
Frontend
```

### Model Evaluation

Contributor 1 and Contributor 2 own ML model evaluation.

Do not confuse software tests with recognition accuracy.

## Tasks

Add or improve tests without modifying another contributor's ML implementation unnecessarily.

Where possible, create controlled integration tests using known sign tokens from both ASL and ISL.

## Deliverables

- NLP unit tests covering both ASL and ISL rules
- Integration tests for both language pipelines
- Documented test categories
- Clear distinction between software correctness and model accuracy

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 6

Report:

1. Tests added (ASL and ISL).
2. Tests passing.
3. Tests failing.
4. Integration status with Contributor 1 (ASL & ISL static models).
5. Integration status with Contributor 2 (ASL & ISL dynamic models).
6. Any blockers affecting the final system.
7. What must be completed during Weeks 7 and 8.

---

# WEEK 7 — SYSTEM EVALUATION FRAMEWORK AND ROBUSTNESS

## Goals

Prepare and execute the overall system evaluation framework where the required components are available for both ASL and ISL.

The eventual system should evaluate:

### ML Metrics

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

These are primarily owned by the ML contributors for both ASL and ISL models.

### System Metrics

Measure where possible:

- Inference latency (single-hand ASL vs dual-hand ISL)
- FPS across both pipelines
- End-to-end response time

### Robustness

Where practical, test across both ASL (unimanual) and ISL (bimanual):

- Different users
- Different lighting
- Different backgrounds
- Different distances
- Different orientations and inter-hand occlusions (ISL)

### Sentence-Level Evaluation

Evaluate whether:

```text
Recognized Sign Sequence (ASL / ISL)
```

is transformed into a sentence that preserves the intended meaning.

Do not fabricate metrics.

If a component is incomplete, explicitly document that the evaluation could not yet be performed.

## Deliverables

Create:

```text
evaluation/
├── system_metrics.py
└── evaluation_plan.md
```

or an equivalent clean structure.

Document:

- What is measured
- How it is measured
- Which contributor owns each metric
- What data is required
- Actual results versus planned evaluation for both ASL and ISL

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 7

Report:

1. Evaluation framework completed.
2. Actual metrics collected for both ASL and ISL.
3. Metrics still unavailable.
4. System-level test results (latency and FPS for ASL vs ISL).
5. Robustness-test results across both languages.
6. Sentence-level evaluation results for ASL and ISL.
7. Any limitations discovered during testing.

Clearly label all results as:

- Implemented and tested
- Implemented but not fully evaluated
- Planned but incomplete

---

# WEEK 8 — FINAL INTEGRATION, VALIDATION AND DOCUMENTATION

## Goals

Support final end-to-end integration of the UNMUTE system across both ASL and ISL.

The intended overall flow is:

```text
Webcam
↓
MediaPipe
↓
Landmark Extraction (1 or 2 Hands)
↓
Feature Engineering (109-dim ASL / 228-dim ISL)
↓
Static/Dynamic Recognition (ASL / ISL)
↓
Stable Sign Tokens (with language mode tag)
↓
Sequence Buffer
↓
Sentence Formation (Language-Specific Rules)
↓
Final English Sentence
↓
Browser Speech
```

Do not claim that the system performs unrestricted ASL or ISL translation unless this has genuinely been implemented and evaluated.

## Tasks

1. Verify integration with both static and dynamic recognition contributors for both ASL and ISL.
2. Test supported end-to-end sequences in both language modes.
3. Verify sentence formation across both languages.
4. Verify frontend output and mode switching.
5. Verify speech output for both languages.
6. Document limitations and known failure cases.
7. Prepare a concise integration guide for the team.

## Final Deliverables

Provide:

1. Current text accumulation audit.
2. Structured token interface specification (handling ASL and ISL).
3. Rule-based sentence processor supporting both languages.
4. Grammar and phrase transformation rules for ASL and ISL.
5. Unit tests for both language pipelines.
6. Integration design for FastAPI supporting language mode switching.
7. Speech integration with final sentences.
8. Evaluation framework covering both languages.
9. Documentation of supported sentence patterns (ASL and ISL).
10. Known limitations of each language pipeline.

---

# FINAL ⏸ PAUSE-AND-REPORT CHECKPOINT — PROJECT COMPLETION

Before declaring your contribution complete, stop and provide a comprehensive implementation report containing:

## What Was Implemented

Clearly list every completed component for both ASL and ISL.

## What Was Tested

Include:

- Unit tests (ASL and ISL)
- Integration tests across both modes
- Manual tests
- End-to-end tests

## Actual Results

Report only real results.

Do not invent:

- Accuracy
- Latency
- FPS
- Robustness results
- Translation quality

## Supported Sign-Token Patterns

Document exactly which patterns the sentence processor supports for ASL and ISL.

## Sentence Transformation Examples

Show realistic input/output examples for both ASL and ISL.

## Rules Implemented

Explain the deterministic language-processing rules for both languages.

## Integration Points

Explain:

- What Contributor 1 provides (ASL and ISL static models)
- What Contributor 2 provides (ASL and ISL dynamic models)
- What this component expects
- How the frontend receives the final result

## Files Changed

List every created or modified file.

## Current Limitations

Clearly document:

- Controlled vocabulary limitations (ASL and ISL)
- Unsupported grammar patterns
- Recognition dependencies
- Any incomplete integration

## Remaining Work

List anything still required before UNMUTE can be presented as a complete end-to-end system.

Do not claim complete implementation unless the entire pipeline has actually been integrated and tested.

---

# FILE OWNERSHIP

Prefer creating and owning:

```text
nlp/
├── sentence_processor.py
├── grammar_rules.py
├── vocabulary.py
└── tests/
```

You may also add:

```text
evaluation/
├── system_metrics.py
└── evaluation_plan.md
```

Avoid major modifications to:

- ML training code
- Feature engineering
- Static MLP implementation
- LSTM implementation
- Frontend architecture

Coordinate shared backend changes before making them.

---

# CRITICAL INTEGRATION & MANDATORY ARCHITECTURE UPDATE (WEEK 3)

## Architectural Alignment with Contributor 1 (ML Foundation, Static Engine & Interactive 3D Guide)

To ensure smooth multimodal user experience, consistent evaluation benchmarking, and accurate frontend-backend integration, Contributor 1 has finalized the following architectural interfaces. Contributor 3 and their AI agents MUST incorporate these additions into testing, evaluation, and frontend response handlers:

### 1. Universal Person-Invariant Recognition Engine
- The static recognition engine in `sign_engine/asl_classifier.py` and dataset preparation pipeline in `ml/data/prepare_dataset.py` now implement **Self-Phalange Bone Length Normalization**:
  $$\text{bone\_length} = \|\mathbf{p}_{\text{PIP}} - \mathbf{p}_{\text{MCP}}\| + \|\mathbf{p}_{\text{DIP}} - \mathbf{p}_{\text{PIP}}\| + \|\mathbf{p}_{\text{TIP}} - \mathbf{p}_{\text{DIP}}\|$$
  $$\text{extension\_ratio} = \frac{\|\mathbf{p}_{\text{TIP}} - \mathbf{p}_{\text{MCP}}\|}{\text{bone\_length}}$$
  Combined with proximal-to-distal phalanx collinearity vectors ($\mathbf{v}_{\text{prox}} \cdot \mathbf{v}_{\text{dist}} > 0.35$), this provides invariance across varying palm sizes, hand geometries, and finger proportions (tested across slender, broad, and child hands in `tests/test_sign_engine.py`).
- **Evaluation Implication for Contributor 3**: When designing end-to-end evaluation protocols and measuring accuracy/robustness in `evaluation/system_metrics.py`, include signers with diverse hand proportions (broad palms, slender fingers) to demonstrate signer-independent invariance.

### 2. High-Contrast 5-Finger Color System
The visualizer and practice canvas have adopted a standardized color hierarchy for each finger:
- 🟠 **Thumb**: `#ff9f1c` (Neon Amber / Gold)
- 🔵 **Index**: `#00f0ff` (Electric Cyan)
- 🟢 **Middle**: `#20bf6b` (Vivid Emerald Green)
- 🟣 **Ring**: `#9b5de5` (Royal Purple)
- 🔴 **Pinky**: `#f72585` (Hot Pink / Magenta)
- ⚪ **Palm Base & Wrist**: `rgba(220, 235, 255, 0.65)` (Ice Silver)
- When evaluating UI usability or designing new visual indicators, adhere strictly to these color standards.

### 3. Interactive 3D Visualizer, Animated Guide & Instant Fallback Catalog
- The web client (`static/app.js`, `static/index.html`, `static/styles.css`) now incorporates:
  - **Interactive 3D Hand Model**: 360° mouse and touch drag orbit controls with view angle presets (`Front`, `Side`, `Top`, `Isometric`) using 3D perspective foreshortening.
  - **Animated Sign Formation Guide**: Smoothly interpolates the hand skeleton from a neutral open resting pose to target sign formation (`▶ Animate` / `⏸ Pause`).
  - **Practice Studio 3D Modal**: Dedicated "📖 View 3D Sign Guide & Tips" action button in the challenge card.
  - **Instant Fallback Dictionary (`FALLBACK_SIGN_GUIDE`)**: Contains pre-rendered anatomical descriptions, tips, and color-coded keypoints for all 26 letters and phrases, ensuring the UI is never blank even before server responses arrive.
- **Integration & NLP Implication for Contributor 3**:
  - Sentence processor and NLP output tokens can trigger the inspector modal with recognized signs (`openInspectorModal(signName)`).
  - Practice Studio evaluation metrics should record match accuracy against canonical reference landmarks rendered in the 3D model.

### 4. Three.js WebGL Volumetric 3D Engine & OrbitControls Upgrade
- **Full WebGL 3D Integration**: The client-side visualizer has been upgraded to a true Three.js WebGL engine using locally-staged static/three.min.js (Three.js r128) and static/OrbitControls.js.
- **Volumetric 3D Geometry**: Hands are rendered with 21 lit joint spheres, metallic bone cylinders rotated with quaternions along parent-child vectors, and a translucent cybernetic palm plate spanning wrist and knuckles.
- **Interactive OrbitControls**: Signers can freely orbit in 360 degrees, zoom in/out with mouse-wheel (1.0x to 5.5x), pan, or snap to camera view presets (Front, Side, Top, Isometric).
- **Cubic-Eased Dynamic Formation Animation**: Real-time sinusoidal cubic easing interpolates landmarks between a neutral resting hand and the target sign shape with Play Guide / Pause Guide toggles.
- **Viewport Availability**: Embedded into the 3D Sign Inspector Modal (#modal-sign-canvas), Practice Studio Challenge Card (#practice-target-canvas), and Live Camera Reference Widget (#camera-ref-canvas).

### 5. Dedicated Hardcoded Port 8505 Configuration
- **Port Conflict Prevention**: To prevent clashes with standard ports (8080, 8000, 3000) used by other local development servers and proxies, UNMUTE now hardcodes and defaults to port **8505** in 
un.py and stop.py.
- **Integration & Evaluation Requirement**: All automated test suites, end-to-end evaluation harnesses (valuation/system_metrics.py), WebSocket integration tests, and benchmark scripts must target port **8505** (http://localhost:8505).


---

# ACTIONABLE SCHEDULE INTEGRATION: FIT NEW ADDITIONS INTO CONTRIBUTOR 3 ROADMAP (WEEKS 3-8)

## Instructions for Contributor 3 and Assigned AI Agents
Contributor 1 has finalized and integrated three core architectural foundations:
1. **Universal Person-Invariant Recognition Engine** (`sign_engine/asl_classifier.py`): Self-Phalange Bone Ratio normalization & directional phalanx collinearity.
2. **Three.js WebGL Volumetric 3D Hand Visualizer & OrbitControls** (`static/app.js`): Real 3D meshes, translucent cybernetic palm plate, 5-finger color hierarchy, camera presets, and cubic-eased animated guide.
3. **Dedicated Hardcoded Port 8505** (`run.py`, `stop.py`, `http://localhost:8505`): Complete avoidance of port 8080/8000 collisions.

You MUST schedule and integrate these additions into your weekly deliverables as follows:

### Week 3 — Rule-Based Sentence Formation & Practice Studio 3D Integration
- **Practice Challenge Alignment**: In `static/app.js` and the Practice Studio evaluation flow, utilize the in-card WebGL 3D visualizer (`#practice-target-canvas`) with presets (`Isometric`, `Front`, `Side`) and animation toggle (`#btn-practice-anim-toggle`).
- **Interactive Sign Guide Launcher**: Ensure that clicking words in sentence compositions or practice cards triggers `openInspectorModal(signName)` to display the 3D WebGL hand model with 5-finger color-coded keypoints.

### Week 4 — FastAPI Server Integration & Port 8505 Standard
- **Dedicated Port 8505 Binding**: Update all test clients (`fastapi.testclient.TestClient`), background task launchers, and API documentation to communicate exclusively via `http://localhost:8505` and `ws://127.0.0.1:8505`.
- **System Health & REST Testing**: Ensure `GET /api/status` and `POST /api/predict-frame` test suites pass under port 8505 without conflicts.

### Week 5 — Speech Flow & Frontend 3D HUD Synchronization
- **5-Finger Color Badging**: Apply the standardized color system across all subtitle overlays, sentence composer tags, and TTS feedback cards:
  - Thumb: `#ff9f1c` | Index: `#00f0ff` | Middle: `#20bf6b` | Ring: `#9b5de5` | Pinky: `#f72585`.
- **WebGL Context Lifecycle**: In single-page tab transitions (`camera-tab`, `practice-tab`, `dictionary-tab`), ensure WebGL contexts are properly maintained without memory leaks.

### Week 6 & Week 7 — End-to-End Testing & System Evaluation Framework
- **Diverse Hand Geometry Evaluation**: In `evaluation/system_metrics.py` and test harnesses, benchmark recognition accuracy across varying hand proportions (slender fingers, broad palms, short fingers).
- **Latency & Throughput Verification**: Measure round-trip inference latency over WebSockets on port 8505 (target: < 20ms, 60+ FPS).
- **3D Render Performance Audit**: Verify that Three.js WebGL rendering maintains 60 FPS without GPU throttling during live video inference.

### Week 8 — Final System Validation & Documentation Handover
- **Cross-Platform Port Validation**: Verify that `start.bat`, `start.ps1`, `python run.py`, and `stop.py` reliably launch and terminate on port `8505` across Windows, macOS, and Linux without port clashes.

