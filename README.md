# 🖐️ Unmute - Real-Time AI Sign Language Translator (ASL + ISL)

A real-time bilingual **American Sign Language (ASL)** and **Indian Sign Language (ISL)** translator powered by **Google MediaPipe**, **PyTorch**, **OpenCV**, **Scikit-learn**, and **FastAPI**, featuring **Live Camera Stream** and **Video File Upload** translation capabilities, with interactive practice challenges, custom gesture training, and subtitle export.

---

## 🌟 Key Features

1. **Dual Sign Language Engines (ASL + ISL)**:
   - 🇺🇸 **American Sign Language (ASL)**: Unimanual 109-dimensional geometric feature pipeline supporting 24 static alphabets (A–Y excl. dynamic J/Z), complete numerals (0–9), static phrases (*I LOVE YOU, OKAY, PEACE, THUMBS UP, THUMBS DOWN, STOP*), and dynamic sequence gestures.
   - 🇮🇳 **Indian Sign Language (ISL)**: Bimanual two-handed 228-dimensional feature pipeline (109 Primary Hand + 109 Secondary Hand + 10 Inter-hand spatial/contact metrics) following **ISLRTC standards** (Ministry of Social Justice & Empowerment, Govt. of India) covering 26 bimanual alphabets (A–Z), single-handed numerals (0–9), cultural static phrases (*NAMASTE, I LOVE YOU, PEACE, OKAY, THUMBS UP, THUMBS DOWN, STOP*), and dynamic gesture sequences.
   - 🔄 **Real-Time Language Switcher**: Toggle seamlessly between ASL and ISL on the live feed and backend dispatch.
2. **Dual Input Translation**:
   - **Live Webcam Translation**: Ultra-low-latency real-time video stream over WebSocket with glowing HUD landmark skeleton overlay, letter accumulator, sentence composer, and Text-To-Speech (TTS).
   - **Video File Translation**: Upload pre-recorded sign videos (MP4, WebM, MOV, AVI) for automated frame-by-frame analysis, timestamped interactive transcripts, synchronized subtitle playback, and `.srt`/`.vtt`/`.json`/`.txt` export.
3. **Sign Visualizer & Guide Quality Overhaul**:
   - 🖐️ **Interactive Visualizer**: Live guide previews with glowing neon 21-landmark hand skeleton and high-resolution anatomical breakdowns.
   - 🎯 **Gamified Practice Studio**: Real-time hand pose matching bar with score tracking and holding verification timer.
   - ⚡ **Ultra-Low Latency Pipeline**: Binary WebSocket transfer with ping-pong flow control and non-blocking worker threads achieving **~13.5ms round-trip response (74+ FPS)**.
4. **Modern Dual-Theme UI**:
   - Clean, sky-blue **Light Mode** by default, with a complementary **Dark Mode** toggle, persisting via localStorage.
5. **Custom Gesture Recorder & Trainer**:
   - Capture live samples of novel signs directly through the browser and train lightweight custom models in real-time.
6. **Bilingual Visual Dictionary**:
   - Comprehensive searchable reference library of ASL and ISL handshapes, fingerspelling cards, and gesture explanations.

---

## 📐 System Architecture

See [`architecture.puml`](architecture.puml) for the complete PlantUML architecture diagram.

```
Browser Client (Web UI) ───[WebSocket / REST]───> FastAPI Server (main.py)
                                                        │
                                           ┌────────────┴───────────┐
                                           ▼                        ▼
                                    Live Stream WS          Video Upload Pipeline
                                           │                        │
                                           └────────────┬───────────┘
                                                        ▼
                                       MediaPipe Hand Landmarker (1 or 2 Hands)
                                                        │
                                       Dual Feature Engineer (109-dim / 228-dim)
                                                        │
                                           ┌────────────┴───────────┐
                                           ▼                        ▼
                                Static MLP (ASL / ISL)     Dynamic Sequence LSTM
                                           │                        │
                                           └────────────┬───────────┘
                                                        ▼
                                       Stability & Temporal Jitter Filter
                                                        │
                                    Structured Tokens (text, type, lang, conf)
                                                        │
                                       NLP Sentence Processor & Grammar Engine
                                                        │
                                          Refined Sentence Output & TTS
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.11 or 3.12 (PyTorch-compatible environment; Python 3.11.9 tested and recommended)
- Modern Web Browser (Chrome, Edge, Firefox, Safari) with webcam access
- Optional: CUDA-compatible GPU (e.g. NVIDIA RTX) for accelerated PyTorch training

### 2. Environment Setup & Installation
We provide automated bootstrap scripts that configure a clean virtual environment with PyTorch, MediaPipe, OpenCV, and FastAPI:

**Option A — Automated Setup Script**:
- Windows Batch: `.\setup_env.bat`
- PowerShell: `.\setup_env.ps1`

**Option B — Manual Installation**:
```bash
# Create virtual environment with Python 3.11/3.12
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell: .\.venv\Scripts\Activate.ps1
# On Windows Command Prompt: .\.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### 3. Start the Server & Web Application

You can start the application using any of the scripts in the root directory:

**Option A — Python Launcher (Recommended)**:
```bash
python run.py
```
*(Options: `--port 8090`, `--reload`, `--no-browser`)*

**Option B — Double-Click Batch Script**:
- Double-click `start.bat` (or run `.\start.ps1` in PowerShell).

**Option C — Direct Uvicorn**:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8090 --reload
```

Then open your browser to **`http://localhost:8090`**.

### 4. Stop the Server

To stop any running server instance and free the port:

**Python**:
```bash
python stop.py
```

**Double-Click**:
- Double-click `stop.bat` (or run `.\stop.ps1` in PowerShell).

---

## 📡 API Reference

- `GET /api/status` - System health check, active model type, and supported languages (`["ASL", "ISL"]`).
- `POST /api/predict-frame` - Single-frame base64/binary image landmark extraction and sign prediction.
- `WS /ws/live-stream` - Bi-directional real-time WebSocket for live camera streaming and HUD prediction feeds.
- `POST /api/upload-video` - Uploads a video file and triggers asynchronous processing.
- `GET /api/video-status/{job_id}` - Polls video processing progress (0% - 100%).
- `GET /api/video-result/{job_id}` - Retrieves timestamped translation segments, sentence transcripts, and subtitles.
- `GET /api/video-file/{filename}` - Streams processed video file with HTTP Range support for synchronized playback.
- `GET /api/export-subtitles/{job_id}?format=srt` - Downloads `.srt`, `.vtt`, `.json`, or `.txt` subtitle files.
- `GET /api/dictionary` - Returns full bilingual ASL & ISL dictionary vocabulary, tips, and reference landmarks.
- `POST /api/custom-gesture/save` - Records and persists custom gesture training samples to disk.
- `GET /api/custom-gesture/list` - Lists all registered custom gestures.
- `DELETE /api/custom-gesture/{gesture_name}` - Deletes a custom gesture.

---

## 📂 Project Structure

```text
unmute/
├── backend/                  # FastAPI web server and routing layer
│   └── main.py               # REST endpoints, WebSocket handler, and static file serving
├── sign_engine/              # Sign recognition core engine
│   ├── landmark_extraction.py# MediaPipe hand landmark extraction (21 3D points)
│   ├── feature_engineering.py# Invariant feature extraction (109-dim ASL / 228-dim ISL)
│   ├── asl_classifier.py     # Hybrid anatomical rule-based & legacy ML classifier
│   ├── temporal_tracker.py   # Rolling window (36 frames) dynamic gesture tracker
│   ├── custom_gestures.py    # Live k-NN custom gesture recorder & trainer
│   └── video_processor.py    # Offline video processing & keyframe subtitle pipeline
├── ml/                       # Machine Learning foundation & static recognition
│   ├── data/                 # Data preparation, labels, and PyTorch datasets
│   │   ├── labels.py         # Canonical class definitions for ASL (41) and ISL (44)
│   │   ├── prepare_dataset.py# Feature extraction & stratified zero-leakage 70/15/15 splitting
│   │   └── dataset.py        # PyTorch StaticSignDataset and get_dataloaders() factory
│   ├── models/               # PyTorch neural network architectures
│   │   └── static_mlp.py     # StaticASL_MLP (109 dims) and StaticISL_MLP (228 dims)
│   ├── training/             # Training, validation & evaluation pipelines
│   │   └── train_static.py   # Modular PyTorch training CLI with checkpointing
│   ├── legacy_rf_audit.py    # Audit suite for legacy Random Forest model
│   └── dataset_recommendation.md # Dataset strategy and anatomical sign catalogs
├── static/                   # Frontend single-page application
│   ├── index.html            # Web interface layout and modal templates
│   ├── app.js                # WebSocket streaming, Canvas HUD, and UI controller
│   └── styles.css            # Responsive styling, light/dark theme variables
├── models/                   # Serialized machine learning models and baselines
│   ├── asl_rf_model.joblib   # Legacy Random Forest baseline model (109 features)
│   ├── asl_static_mlp.pt     # Trained PyTorch ASL Static MLP checkpoint
│   └── isl_static_mlp.pt     # Trained PyTorch ISL Static MLP checkpoint
├── tests/                    # Automated pytest test suite
│   ├── test_backend.py       # REST and WebSocket endpoint integration tests
│   ├── test_sign_engine.py   # Landmark, feature engineering, and classifier tests
│   ├── test_ml_data.py       # Label mappings, dual features, zero-leakage splits tests
│   └── test_static_mlp.py    # PyTorch Static MLP architectures and training tests
├── agent/                    # Contributor documentation, master plans, and audit reports
│   └── docs/                 # Contributor prompts, weekly roadmaps, and audit files
├── architecture.puml         # Authoritative PlantUML system architecture diagram
├── requirements.txt          # Python dependencies
└── README.md                 # Project overview and developer documentation
```

---

## 🧠 Machine Learning Foundation (Contributor 1)

UNMUTE supports a Dual-Language Static Recognition Engine for both **American Sign Language (ASL)** and **Indian Sign Language (ISL)**:
- **ASL Pipeline**: 21 single-hand MediaPipe landmarks $\rightarrow$ 109-dimensional rotation- and scale-invariant geometric feature vector $\rightarrow$ `StaticASL_MLP` $\rightarrow$ 41 static classes.
- **ISL Pipeline**: 42 bimanual MediaPipe landmarks (Primary Hand 109 + Secondary Hand 109 + 10 Inter-hand spatial/contact metrics) $\rightarrow$ 228-dimensional feature vector $\rightarrow$ `StaticISL_MLP` $\rightarrow$ 44 static classes aligned with ISLRTC standards.

### Audit Legacy Baseline Model
To verify compatibility and profile the legacy comparative baseline model:
```bash
python -m ml.legacy_rf_audit
```

### Dataset Preparation Pipeline
To extract features, enforce zero sample leakage (70% Train / 15% Val / 15% Test), and export compressed `.npz` archives:
```bash
# ASL Dataset Pipeline (109-dim features, 41 classes)
python ml/data/prepare_dataset.py --language ASL --output-dir data

# ISL Dataset Pipeline (228-dim features, 44 classes)
python ml/data/prepare_dataset.py --language ISL --output-dir data
```

### Train Static Recognition Models
To train the PyTorch Multi-Layer Perceptrons with learning rate scheduling and best validation checkpointing:
```bash
# Train Static ASL MLP (saves models/asl_static_mlp.pt)
python -m ml.training.train_static --language ASL --epochs 25 --batch-size 32

# Train Static ISL MLP (saves models/isl_static_mlp.pt)
python -m ml.training.train_static --language ISL --epochs 25 --batch-size 32
```

---

## 🧪 Running Automated Tests
```bash
pytest tests/ -v
```

