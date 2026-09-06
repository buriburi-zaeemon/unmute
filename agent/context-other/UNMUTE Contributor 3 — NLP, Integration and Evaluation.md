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

## Goals

Implement the initial controlled-vocabulary sentence-processing layer.

The system must use deterministic and explainable transformations.

Do **NOT** use an LLM as a substitute for incorrect sign recognition.

Do **NOT** hallucinate missing signs.

The intended pipeline is:

```text
Sign Tokens
↓
Token Normalization
↓
Phrase Mapping
↓
Basic Grammar Transformation
↓
Capitalization
↓
Punctuation
↓
Final Sentence
```

Example:

```python
["I", "GO", "HOME", "YESTERDAY"]
```

Could become:

```text
I went home yesterday.
```

This does not mean the system supports unrestricted ASL-to-English translation.

It is a **controlled-vocabulary sentence-formation system**.

## Suggested Structure

```text
nlp/
├── sentence_processor.py
├── grammar_rules.py
├── vocabulary.py
└── tests/
```

You may adapt this structure if necessary.

## Requirements

Implement explainable rules for supported patterns.

Examples may include:

- Pronoun handling
- Basic verb transformations
- Time-word positioning
- Phrase mappings
- Capitalization
- Punctuation

Every rule should be understandable and defensible in a viva.

## Deliverables

- Working sentence processor
- Vocabulary configuration
- Grammar-rule module
- Example transformations
- Unit tests

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 3

Report:

1. Supported sentence patterns.
2. Rules implemented.
3. Example transformations.
4. Unsupported patterns.
5. Unit-test results.
6. Known limitations.
7. Any vocabulary assumptions that need confirmation from the ML contributors.

Do not claim unrestricted natural-language translation.

---

# WEEK 4 — FASTAPI AND SYSTEM INTEGRATION PREPARATION

## Goals

Prepare clean integration points between:

```text
Recognition
↓
Stable Sign Token
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

Coordinate shared changes with the contributor responsible for real-time recognition.

## Requirements

If the final ML models are not yet available:

- Use clearly labelled mock inputs for development and testing.
- Never present mock recognition as actual AI performance.

The sentence-processing layer should be independently testable.

## Deliverables

- Backend integration design
- Sequence-buffer integration strategy
- API/WebSocket contract where needed
- Minimal integration implementation where safe
- Integration tests using controlled test tokens

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 4

Report:

1. Current integration architecture.
2. Exact integration points added or proposed.
3. Whether the real recognition contributors can now provide tokens directly.
4. Backend files modified.
5. Integration-test results.
6. Remaining dependencies before full end-to-end integration.

---

# WEEK 5 — SPEECH FLOW AND FRONTEND CONNECTION

## Goals

Ensure the application speaks the **final processed sentence**, not raw sign tokens.

The existing application already uses:

```javascript
window.speechSynthesis
```

This is functional.

Do **NOT** replace it with `pyttsx3` unless the team explicitly changes the application architecture.

The desired flow is:

```text
Recognized Sign Sequence
↓
Sentence Processing
↓
Final Sentence
↓
Display
↓
Speak
↓
Replay / Clear
```

## Tasks

Inspect and improve the connection between:

- Processed sentence
- Frontend display
- Speech synthesis
- Replay behavior
- Clear behavior

Do not redesign the UI unnecessarily.

Focus on functional correctness.

## Deliverables

- Final sentence passed correctly to frontend
- Speech uses processed output
- Clear behavior resets relevant state
- Replay uses the intended final sentence
- Relevant tests or manual test procedure

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 5

Report:

1. Whether processed sentences reach the frontend correctly.
2. Whether speech uses processed sentences.
3. Clear/replay behavior.
4. Files changed.
5. Manual tests performed.
6. Remaining integration problems.

---

# WEEK 6 — TESTING AND END-TO-END INTEGRATION SUPPORT

## Goals

Strengthen the system testing strategy.

Clearly separate:

### Unit Tests

Test:

- Sentence processing
- Token normalization
- Grammar rules
- Phrase mappings
- API contracts

### Integration Tests

Test:

```text
Recognition Output
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

Where possible, create controlled integration tests using known sign tokens.

## Deliverables

- NLP unit tests
- Integration tests
- Documented test categories
- Clear distinction between software correctness and model accuracy

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 6

Report:

1. Tests added.
2. Tests passing.
3. Tests failing.
4. Integration status with Contributor 1.
5. Integration status with Contributor 2.
6. Any blockers affecting the final system.
7. What must be completed during Weeks 7 and 8.

---

# WEEK 7 — SYSTEM EVALUATION FRAMEWORK AND ROBUSTNESS

## Goals

Prepare and execute the overall system evaluation framework where the required components are available.

The eventual system should evaluate:

### ML Metrics

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

These are primarily owned by the ML contributors.

### System Metrics

Measure where possible:

- Inference latency
- FPS
- End-to-end response time

### Robustness

Where practical, test:

- Different users
- Different lighting
- Different backgrounds
- Different distances
- Different orientations

### Sentence-Level Evaluation

Evaluate whether:

```text
Recognized Sign Sequence
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
- Actual results versus planned evaluation

---

## ⏸ PAUSE-AND-REPORT CHECKPOINT — END OF WEEK 7

Report:

1. Evaluation framework completed.
2. Actual metrics collected.
3. Metrics still unavailable.
4. System-level test results.
5. Robustness-test results.
6. Sentence-level evaluation results.
7. Any limitations discovered during testing.

Clearly label all results as:

- Implemented and tested
- Implemented but not fully evaluated
- Planned but incomplete

---

# WEEK 8 — FINAL INTEGRATION, VALIDATION AND DOCUMENTATION

## Goals

Support final end-to-end integration of the UNMUTE system.

The intended overall flow is:

```text
Webcam
↓
MediaPipe
↓
Landmark Extraction
↓
Feature Engineering
↓
Static/Dynamic Recognition
↓
Stable Sign Tokens
↓
Sequence Buffer
↓
Sentence Formation
↓
Final English Sentence
↓
Browser Speech
```

Do not claim that the system performs unrestricted ASL translation unless this has genuinely been implemented and evaluated.

## Tasks

1. Verify integration with both static and dynamic recognition contributors.
2. Test supported end-to-end sequences.
3. Verify sentence formation.
4. Verify frontend output.
5. Verify speech output.
6. Document limitations and known failure cases.
7. Prepare a concise integration guide for the team.

## Final Deliverables

Provide:

1. Current text accumulation audit.
2. Structured token interface specification.
3. Rule-based sentence processor.
4. Grammar and phrase transformation rules.
5. Unit tests.
6. Integration design for FastAPI.
7. Speech integration with final sentences.
8. Evaluation framework.
9. Documentation of supported sentence patterns.
10. Known limitations.

---

# FINAL ⏸ PAUSE-AND-REPORT CHECKPOINT — PROJECT COMPLETION

Before declaring your contribution complete, stop and provide a comprehensive implementation report containing:

## What Was Implemented

Clearly list every completed component.

## What Was Tested

Include:

- Unit tests
- Integration tests
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

Document exactly which patterns the sentence processor supports.

## Sentence Transformation Examples

Show realistic input/output examples.

## Rules Implemented

Explain the deterministic language-processing rules.

## Integration Points

Explain:

- What Contributor 1 provides
- What Contributor 2 provides
- What this component expects
- How the frontend receives the final result

## Files Changed

List every created or modified file.

## Current Limitations

Clearly document:

- Controlled vocabulary limitations
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

# IMPORTANT RULES

- Do not claim unrestricted ASL-to-English translation.
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