# 🖐️ Unmute - Real-Time AI Sign Language Translator (ASL + ISL)

A real-time bilingual **American Sign Language (ASL)** and **Indian Sign Language (ISL)** translator powered by **Google MediaPipe**, **PyTorch**, **OpenCV**, **Scikit-learn**, and **FastAPI**, featuring **Live Camera Stream** and **Video File Upload** translation capabilities, with interactive practice challenges, custom gesture training, and subtitle export.

---

## 🌟 Key Features

1. **Dual Sign Language Engines (ASL + ISL)**:
   - 🇺🇸 **American Sign Language (ASL)**: Unimanual 109-dimensional geometric feature pipeline supporting 26 alphabets (A–Z), complete numerals (0–9), and static phrases (*I LOVE YOU, OKAY, PEACE, THUMBS UP, THUMBS DOWN, STOP*).
   - 🇮🇳 **Indian Sign Language (ISL)**: Bimanual two-handed 218+ dimensional feature pipeline following **ISLRTC standards** (Ministry of Social Justice & Empowerment, Govt. of India) covering 26 bimanual alphabets (A–Z), numerals (0–9), and cultural phrases (*NAMASTE, I LOVE YOU, PEACE, OKAY, THUMBS UP, THUMBS DOWN, STOP*).
   - 🔄 **Real-Time Language Switcher**: Toggle seamlessly between ASL and ISL on the live feed.
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
Browser Client (Web UI) ───[WebSocket / REST]───> FastAPI Server
                                                       │
                                          ┌────────────┴───────────┐
                                          ▼                        ▼
                                   Live Stream WS          Video Upload Pipeline
                                          │                        │
                                          └────────────┬───────────┘
                                                       ▼
                                          MediaPipe Landmark Extractor
                                                       │
                                          Feature Engineering Engine
                                                       │
                                          Hybrid ASL Classifier (Rules + ML)
                                                       │
                                          Dynamic Temporal Tracker
                                                       │
                                          Stability Filter & Transcript Generator
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

- `GET /api/status` - System health check & active model information.
- `POST /api/predict-frame` - Single-frame base64/binary image landmark and sign prediction.
- `WS /ws/live-stream` - Bi-directional real-time WebSocket for camera streaming.
- `POST /api/upload-video` - Uploads a video file and starts asynchronous processing.
- `GET /api/video-status/{job_id}` - Polls video processing progress (0% - 100%).
- `GET /api/video-result/{job_id}` - Retrieves timestamped translation segments and subtitles.
- `GET /api/export-subtitles/{job_id}?format=srt` - Downloads `.srt`, `.vtt`, `.json`, or `.txt` subtitle files.
- `GET /api/dictionary` - Returns full ASL dictionary data.
- `POST /api/custom-gesture/save` - Records and persists custom gesture training samples.
- `GET /api/custom-gesture/list` - Lists all registered custom gestures.
- `DELETE /api/custom-gesture/{gesture_name}` - Deletes a custom gesture.

---

## 🧠 Machine Learning Foundation (Contributor 1)

UNMUTE's static recognition pipeline processes 21 3D MediaPipe landmarks into a 109-dimensional rotation- and scale-invariant geometric feature vector, classified by a PyTorch Multi-Layer Perceptron (MLP).

### Audit Legacy Baseline Model
To verify compatibility and profile the legacy comparative baseline model:
```bash
python -m ml.legacy_rf_audit
```

---

## 🧪 Running Automated Tests
```bash
pytest tests/ -v
```
