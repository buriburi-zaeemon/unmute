# UNMUTE — Contributor 3 Technical Audit & Integration Plan (Week 1)

**Author:** Contributor 3 (Sentence Formation, System Integration & Evaluation)  
**Date:** September 6, 2026  
**Project:** UNMUTE — AI-Powered Real-Time Sign Language Translator  

---

## 1. Executive Summary

This document presents the **Week 1 Technical Audit** for Contributor 3 on the UNMUTE project. The audit analyzes the current codebase architecture—specifically prediction transport over WebSockets, string composition in the frontend, temporal tracking, and browser speech synthesis.

Based on this audit, we specify the structured token interface and integration points required to cleanly transition UNMUTE from a character-by-character string accumulator to a **real-time sequential sign-to-language translation system**.

---

## 2. Current Architecture Audit

### 2.1 Prediction & Transport Flow (Backend ➔ Frontend)
- **Transport Mechanism**: Real-time binary WebSocket channel mounted at `/ws/stream` in [backend/main.py](file:///d:/Repositories/unmute/backend/main.py).
- **Client Loop**: `startStreamingLoop()` in [static/app.js](file:///d:/Repositories/unmute/static/app.js) captures JPEG frame blobs from webcam at ~30 FPS network rate and sends them over WebSocket.
- **Server Processing**:
  1. Image decoded with OpenCV (`cv2.imdecode`).
  2. Hand landmarks extracted via `LandmarkExtractor` (MediaPipe Hands).
  3. Geometric features computed via `FeatureEngineer`.
  4. Rolling temporal state updated via `TemporalGestureTracker`.
  5. Sign classified via `ASLClassifier` / custom gesture trainer.
- **Payload Response**: Server returns JSON structure:
  ```json
  {
    "has_hands": true,
    "predicted_sign": "I",
    "confidence": 0.94,
    "is_stable": true,
    "sign_type": "alphabet",
    "handedness": "Right",
    "landmarks": [[0.5, 0.8, 0.0], "..."],
    "top_predictions": [{"label": "I", "confidence": 0.94}]
  }
  ```

---

### 2.2 Current Text Accumulation Mechanism
- **Location**: `accumulateSign(sign, signType)` in [static/app.js](file:///d:/Repositories/unmute/static/app.js).
- **Current Algorithm**:
  ```javascript
  // Client-side debounce (1100ms cooldown for identical consecutive signs)
  if (sign === this.lastCommittedSign && now - this.lastCommittedTime < 1100) return;
  
  if (sign === "SPACE") this.appendChar(" ");
  else if (sign === "BACKSPACE") this.backspace();
  else if (signType === "phrase") this.composedSentence += sign + " ";
  else this.appendChar(sign);
  ```
- **Limitations**:
  - Direct string concatenation treats incoming signs as isolated letters/raw strings (`"I" + "GO" + "HOME" + "YESTERDAY"` $\rightarrow$ `"IGOHOMEYESTERDAY"` or `"I GO HOME YESTERDAY"`).
  - No grammatical structure, tense inflections, or subject-verb-object ordering.
  - No structured sequence representation for downstream NLP tasks.

---

### 2.3 Duplicate Suppression & Stability
- **Server-Side**: `ASLClassifier` uses a sliding window history buffer to mark `is_stable = True` when the same prediction exceeds `min_stable_frames` threshold.
- **Dynamic Signs**: `TemporalGestureTracker` in [sign_engine/temporal_tracker.py](file:///d:/Repositories/unmute/sign_engine/temporal_tracker.py) enforces a `cooldown_seconds` (0.9s) per dynamic sign candidate.
- **Client-Side**: `activeConfidenceThreshold` slider (default 50%) filters out low-confidence predictions before calling `accumulateSign()`.

---

### 2.4 Speech Synthesis Flow
- **Location**: `speakText(text)` in [static/app.js](file:///d:/Repositories/unmute/static/app.js).
- **Engine**: Uses browser-native Web Speech API (`window.speechSynthesis`).
- **Trigger**: Fired when user clicks "Speak" button or when full video translation completes.
- **Assessment**: Browser speech synthesis is local, responsive, zero-overhead, and works cross-platform without external C-library dependencies. We will retain Web Speech API and feed it the refined sentence output from our NLP layer.

---

## 3. Recommended Structured Token Flow

To achieve continuous sign sequence translation (`["I", "GO", "HOME", "YESTERDAY"]` $\rightarrow$ `"I went home yesterday."`), we propose the following 5-stage pipeline:

```text
  [ Webcam / MediaPipe ]
           │
           ▼
[ ASLClassifier / LSTM ]  ──► Stable Sign Prediction (e.g. "GO", conf=0.92)
           │
           ▼
 [ nlp/sequence_buffer ]  ──► Structured Token Queue: ["I", "GO", "HOME", "YESTERDAY"]
           │
           ▼
[ nlp/sentence_processor ] ──► Rule-Based Grammar Transformation Engine
           │
           ▼
  [ Refined Sentence ]    ──► "I went home yesterday."
           │
           ├────────────────────────┐
           ▼                        ▼
[ Frontend UI Display ]   [ Speech Synthesis ]
```

### 3.1 Token Data Contract (`Token`)
```python
@dataclass
class Token:
    text: str              # Canonical sign label (e.g. "GO", "HELLO", "A")
    confidence: float      # Model prediction confidence (0.0 to 1.0)
    sign_type: str         # "alphabet", "word", "phrase", "dynamic"
    timestamp: float       # Epoch timestamp when sign was committed
```

---

## 4. Recommended Backend Integration Points

1. **`nlp/sequence_buffer.py`**:
   - Maintains active token sequence per WebSocket session.
   - Handles pause detection (e.g. > 1.8s no sign $\rightarrow$ sentence boundary).

2. **`nlp/sentence_processor.py`**:
   - Pure function interface: `process_sequence(tokens: List[Token]) -> SentenceResult`.
   - Converts sign token list to grammatically structured English sentence.

3. **`backend/main.py`**:
   - Update WebSocket response payload to include `token_sequence` and `processed_sentence`.
   - Add REST API endpoint `POST /api/process-sequence`.

---

## 5. File Modification & Ownership Plan

| File | Status | Contributor 3 Role |
| :--- | :--- | :--- |
| [nlp/vocabulary.py](file:///d:/Repositories/unmute/nlp/vocabulary.py) | **[NEW]** | Controlled vocabulary definitions and POS metadata |
| [nlp/grammar_rules.py](file:///d:/Repositories/unmute/nlp/grammar_rules.py) | **[NEW]** | Deterministic grammar transformation rules |
| [nlp/sentence_processor.py](file:///d:/Repositories/unmute/nlp/sentence_processor.py) | **[NEW]** | Rule-based NLP transformation engine |
| [nlp/sequence_buffer.py](file:///d:/Repositories/unmute/nlp/sequence_buffer.py) | **[NEW]** | Temporal token deduplication and sequence buffering |
| [backend/main.py](file:///d:/Repositories/unmute/backend/main.py) | **[MODIFY]** | Wire sequence buffer & sentence processor into API/WS |
| [static/app.js](file:///d:/Repositories/unmute/static/app.js) | **[MODIFY]** | Update UI text composer to render refined sentence |
| [tests/test_nlp_processor.py](file:///d:/Repositories/unmute/tests/test_nlp_processor.py) | **[NEW]** | Unit tests for NLP rules and sequence transformations |
| [evaluation/system_metrics.py](file:///d:/Repositories/unmute/evaluation/system_metrics.py) | **[NEW]** | System latency, FPS, and performance profiler |
| [evaluation/evaluation_plan.md](file:///d:/Repositories/unmute/evaluation/evaluation_plan.md) | **[NEW]** | Full system evaluation framework & testing plan |

---

## 6. Dependencies on ML Contributors

- **Contributor 1 (ML Foundation & Static Model)**: Needs to provide canonical label strings for static signs (e.g., `"A".."Z"`, `"0".."9"`).
- **Contributor 2 (Dynamic Recognition & LSTM)**: Needs to provide label strings for dynamic movement signs (`"HELLO"`, `"THANK YOU"`, `"GO"`, `"HOME"`, `"YESTERDAY"`).

---

## 7. Week 1 Checkpoint Summary

1. **Current Repository State**: Clean, setup complete with Python 3.11.9, PyTorch 2.5.1+cu121, OpenCV 5.0, MediaPipe 1.0.1.
2. **Current Accumulation Flow**: Direct string appending in `app.js` with basic 1.1s debounce.
3. **Structured Token Flow**: `Token` dataclass $\rightarrow$ `SequenceBuffer` $\rightarrow$ `SentenceProcessor` $\rightarrow$ Refined Sentence.
4. **Integration Point**: Integrated into `backend/main.py` WebSocket handler and `app.js`.
5. **Inspected Files**: `backend/main.py`, `static/app.js`, `sign_engine/temporal_tracker.py`, `sign_engine/asl_classifier.py`, `tests/test_backend.py`.
6. **Next Step**: Proceed to Week 2 (Structured Sign Tokens and Sequence Interface).
