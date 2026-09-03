# 🖐️ Unmute - Real-Time AI Sign Language Translator

A real-time American Sign Language (ASL) translator powered by **Google MediaPipe**, **OpenCV**, **Scikit-learn**, and **FastAPI**, featuring **Live Camera Stream** and **Video File Upload** translation capabilities, with interactive practice challenges, custom gesture training, and subtitle export.

---

## 🌟 Key Features

1. **Dual Input Translation**:
   - **Live Webcam Translation**: Ultra-low-latency real-time video stream over WebSocket with glowing HUD landmark skeleton overlay, letter accumulator, sentence composer, and Text-To-Speech (TTS).
   - **Video File Translation**: Upload pre-recorded sign videos (MP4, WebM, MOV, AVI) for automated frame-by-frame analysis, timestamped interactive transcripts, synchronized subtitle playback, and `.srt`/`.vtt`/`.json`/`.txt` export.
2. **Comprehensive ASL Vocabulary**:
   - 🤖 **Continuous Hybrid Recognition Engine**: Real-time geometric and invariant feature classification of the full 26 ASL alphabet (**A–Z**), numbers (**0–9**), and dynamic multi-frame phrases (*HELLO, THANK YOU, YES, NO, PLEASE, I LOVE YOU, PEACE, THUMBS UP, STOP*).
3. **Sign Visualizer & Guide Quality Overhaul**:
   - 🖐️ **Interactive ASL Sign Visualizer**:
     - **Live Guide Previews**: Every dictionary card renders a glowing cyber-neon 21-landmark hand skeleton.
     - **Sign Inspector Modal**: High-res anatomical breakdown with joint-by-joint keypoints and direct "Practice This Sign" jump button.
     - **Practice Studio Reference Pose**: Challenges display a side-by-side reference handshape so you can directly mirror the target sign.
   - 🎯 **Gamified Practice Studio**: Real-time hand pose matching bar with score tracking, holding verification timer, and instant feedback.
   - ⚡ **Ultra-Low Latency Pipeline**: Binary WebSocket transfer with ping-pong flow control and non-blocking worker threads achieving **~13.5ms round-trip response (74+ FPS)**.
4. **Custom Gesture Recorder & Trainer**:
   - Capture live samples of novel signs directly through the browser and train lightweight custom models in real-time.
5. **ASL Visual Dictionary**:
   - Comprehensive searchable reference library of handshapes, fingerspelling cards, and dynamic gesture explanations.

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
- Python 3.10+ (Tested with Python 3.14 on Windows)
- Modern Web Browser (Chrome, Edge, Firefox, Safari) with webcam access

### 2. Installation
From the repository root:
```bash
# Install dependencies (using active Python or virtual environment)
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

## 🧪 Running Automated Tests
```bash
pytest tests/ -v
```
