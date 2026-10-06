"""
FastAPI Backend Application for Sign Language Translator.
Provides REST and WebSocket endpoints for real-time webcam inference,
asynchronous video file processing, subtitle export, custom gesture training, and dictionary access.
"""

from typing import Dict, Any, List, Optional, Tuple
import os
import sys
import uuid
import base64
import asyncio
import threading
import json
import cv2
import numpy as np
import time

# Ensure sign_language_translator root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Query, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sign_engine.landmark_extractor import LandmarkExtractor, HandResult
from sign_engine.feature_engineering import FeatureEngineer
from sign_engine.asl_classifier import ASLClassifier, RecognitionResult
from sign_engine.temporal_tracker import TemporalGestureTracker
from sign_engine.gesture_trainer import GestureTrainer
from sign_engine.video_processor import VideoProcessor, VideoProcessingResult

# Initialize FastAPI App
app = FastAPI(
    title="Sign Language Translator API",
    description="Real-time ASL fingerspelling & dynamic gesture recognition API with dual camera/video input.",
    version="1.0.0",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Core Engine Instances
extractor = LandmarkExtractor()
classifier = ASLClassifier()
gesture_trainer = GestureTrainer()
feature_engineer = FeatureEngineer()
video_processor = VideoProcessor(
    landmark_extractor=extractor,
    classifier=classifier,
    gesture_trainer=gesture_trainer,
)

# Video Processing Jobs in-memory registry
video_jobs: Dict[str, Dict[str, Any]] = {}


# Pydantic Request Models
class FramePredictRequest(BaseModel):
    image_base64: str
    include_landmarks: bool = True
    session_id: Optional[str] = None


class CustomGestureRequest(BaseModel):
    gesture_name: str
    landmarks_batch: List[List[List[float]]]


# Complete ASL Dictionary Data with authoritative anatomical guidance
ASL_DICTIONARY_DATA = [
    # Alphabets A - Z
    {"sign": "A", "category": "Alphabet", "description": "Form a closed fist with all four fingers curled tightly into the palm, with the thumb extended straight upright alongside the index finger's outer knuckle.", "tips": "Keep thumb vertical along the side of the fist; do not tuck it over the front."},
    {"sign": "B", "category": "Alphabet", "description": "Extend all four fingers straight upward pressed firmly together, with the thumb folded flat across the center of the palm.", "tips": "Keep all four fingers upright and touching; thumb rests horizontally across palm."},
    {"sign": "C", "category": "Alphabet", "description": "Curve all four fingers and thumb into a smooth semi-circular 'C' shape with an open aperture, resembling holding a round cup.", "tips": "Maintain a clear curved arc between thumb and fingers."},
    {"sign": "D", "category": "Alphabet", "description": "Extend the index finger straight upward while the middle, ring, and pinky fingers curl downward to touch the tip of the thumb, forming a circular base loop.", "tips": "Only index points straight up; other 3 fingers touch thumb tip."},
    {"sign": "E", "category": "Alphabet", "description": "Curl all four fingers downward tightly so the fingertip pads rest directly on top of the tucked thumb pad, with knuckles bent.", "tips": "Thumb is held flat underneath the curled fingertip pads."},
    {"sign": "F", "category": "Alphabet", "description": "Touch the tips of the index finger and thumb together in a circular pinch, while extending the middle, ring, and pinky fingers straight upward spread apart.", "tips": "Thumb and index form a circle; remaining 3 fingers point up."},
    {"sign": "G", "category": "Alphabet", "description": "Extend the index finger and thumb parallel pointing horizontally sideways with knuckles facing outward, while the middle, ring, and pinky fingers are curled into the palm.", "tips": "Index and thumb point sideways horizontally like a parallel gauge."},
    {"sign": "H", "category": "Alphabet", "description": "Extend the index and middle fingers together pointing horizontally sideways pressed against each other, with thumb tucked and remaining fingers curled.", "tips": "Two parallel fingers pointing sideways horizontally."},
    {"sign": "I", "category": "Alphabet", "description": "Extend the pinky finger straight upward from a closed fist, with the thumb folded across the middle joints of the curled fingers.", "tips": "Only pinky extended upright; other four digits folded tight."},
    {"sign": "J", "category": "Alphabet", "description": "Extend the pinky finger upright from a closed fist, then trace a curving 'J' hook motion downward and upward in the air using a wrist pivot.", "tips": "Dynamic motion: trace the shape of letter J in the air with pinky."},
    {"sign": "K", "category": "Alphabet", "description": "Extend the index finger straight up and middle finger angled forward at 45°, with the thumb extended upward so its pad rests directly between the index and middle knuckles.", "tips": "Thumb pad rests against the first knuckle of the middle finger."},
    {"sign": "L", "category": "Alphabet", "description": "Extend the thumb and index finger fully at a perpendicular 90-degree right angle, while the middle, ring, and pinky fingers remain curled into the palm.", "tips": "Forms an unmistakable 'L' right angle with thumb and index."},
    {"sign": "M", "category": "Alphabet", "description": "Fold the index, middle, and ring fingers over the thumb so the thumb tip protrudes beneath the pinky knuckle, forming three visible knuckle mounds.", "tips": "Three fingers drape over top of the tucked thumb."},
    {"sign": "N", "category": "Alphabet", "description": "Fold the index and middle fingers over the thumb so the thumb tip protrudes between the middle and ring fingers, forming two visible knuckle mounds.", "tips": "Two fingers drape over top of the tucked thumb."},
    {"sign": "O", "category": "Alphabet", "description": "Curve all four fingers and thumb inward so all five fingertips meet touching in a closed round 'O' circle.", "tips": "All fingertips touch thumb tip forming a complete circle."},
    {"sign": "P", "category": "Alphabet", "description": "Extend the index finger forward horizontally and middle finger straight downward at a 90-degree angle, with the thumb tip placed against the middle finger's first knuckle joint.", "tips": "Hand oriented downward with index pointing forward and middle pointing down."},
    {"sign": "Q", "category": "Alphabet", "description": "Extend the index finger and thumb parallel pointing straight downward toward the ground, with the middle, ring, and pinky fingers curled tightly into the palm.", "tips": "Downward-pointing parallel pinch shape with fingers facing the ground."},
    {"sign": "R", "category": "Alphabet", "description": "Extend the index and middle fingers straight upward and cross the index finger over the front of the middle finger.", "tips": "Index and middle fingers crossed tightly upright."},
    {"sign": "S", "category": "Alphabet", "description": "Form a tight fist with all four fingers curled into the palm, folding the thumb horizontally across the front of the middle finger knuckles.", "tips": "Thumb wraps horizontally over the front of the clenched fingers."},
    {"sign": "T", "category": "Alphabet", "description": "Form a fist with the thumb tucked between the index and middle fingers, so the thumb tip pokes upward between the first two knuckles.", "tips": "Thumb pokes up between index and middle fingers."},
    {"sign": "U", "category": "Alphabet", "description": "Extend the index and middle fingers straight upward pressed firmly together side-by-side, with thumb folded across the ring and pinky fingers.", "tips": "Two fingers upright and touching; thumb holds remaining fingers closed."},
    {"sign": "V", "category": "Alphabet", "description": "Extend the index and middle fingers straight upward spread apart in a symmetrical open 'V' shape, with thumb holding ring and pinky fingers curled.", "tips": "Index and middle fingers spread apart forming a 'V' shape."},
    {"sign": "W", "category": "Alphabet", "description": "Extend the index, middle, and ring fingers straight upward spread evenly apart, with the thumb holding down the pinky tip across the palm.", "tips": "Three upright spread fingers; thumb clasps pinky."},
    {"sign": "X", "category": "Alphabet", "description": "Curl the middle, ring, and pinky fingers into a fist, while bending the index finger at its middle joint into a distinct curved hook shape.", "tips": "Hooked index finger pointing upward."},
    {"sign": "Y", "category": "Alphabet", "description": "Extend the thumb and pinky finger fully outward in opposite directions, while curling the index, middle, and ring fingers tightly into the palm.", "tips": "Thumb and pinky spread wide horizontally; middle three fingers curled."},
    {"sign": "Z", "category": "Alphabet", "description": "Extend the index finger from a closed fist, then draw the three-stroke 'Z' zigzag pattern in the air from left to right.", "tips": "Dynamic motion: trace letter Z in the air with index fingertip."},

    # Numbers 0 - 9
    {"sign": "0", "category": "Number", "description": "Curve all fingers and thumb into a closed oval shape where all fingertips touch the thumb pad.", "tips": "Identical to letter O."},
    {"sign": "1", "category": "Number", "description": "Extend index finger straight up with palm facing inward/forward, other fingers held down by thumb.", "tips": "Single index finger pointing up."},
    {"sign": "2", "category": "Number", "description": "Extend index and middle fingers spread apart in a 'V' with palm facing inward.", "tips": "Two fingers extended upright."},
    {"sign": "3", "category": "Number", "description": "Extend thumb, index, and middle fingers spread apart, with ring and pinky curled into palm.", "tips": "Thumb, index, and middle extended."},
    {"sign": "4", "category": "Number", "description": "Extend index, middle, ring, and pinky fingers upright spread apart, with thumb tucked across palm.", "tips": "Four upright fingers spread."},
    {"sign": "5", "category": "Number", "description": "Extend all five fingers and thumb fully upright and spread wide apart facing outward.", "tips": "Open 5-finger spread hand."},
    {"sign": "6", "category": "Number", "description": "Touch the tip of the pinky finger to the tip of the thumb, with index, middle, and ring fingers extended upward.", "tips": "Thumb and pinky touch; other 3 fingers up."},
    {"sign": "7", "category": "Number", "description": "Touch the tip of the ring finger to the tip of the thumb, with index, middle, and pinky fingers extended upward.", "tips": "Thumb and ring finger touch."},
    {"sign": "8", "category": "Number", "description": "Touch the tip of the middle finger to the tip of the thumb, with index, ring, and pinky fingers extended upward.", "tips": "Thumb and middle finger touch."},
    {"sign": "9", "category": "Number", "description": "Touch the tip of the index finger to the tip of the thumb, with middle, ring, and pinky fingers extended upward.", "tips": "Thumb and index touch (resembles 'F')."},

    # Common Phrases
    {"sign": "HELLO", "category": "Phrase", "description": "Open flat hand starts with fingertips near the temple and moves outward in a graceful salute or wave.", "tips": "Dynamic motion: salute/wave outward from forehead."},
    {"sign": "THANK YOU", "category": "Phrase", "description": "Flat open hand starts with fingertips touching the chin/lips, then extends forward and downward toward the recipient.", "tips": "Dynamic motion: fingertips move from chin outward toward person."},
    {"sign": "YES", "category": "Phrase", "description": "Form a closed fist and tilt it forward and back at the wrist twice, mimicking a nodding head.", "tips": "Dynamic motion: nod fist up and down twice."},
    {"sign": "NO", "category": "Phrase", "description": "Snap the index and middle fingertips together against the thumb pad in a quick pinching closure.", "tips": "Dynamic motion: quick snap of index+middle onto thumb."},
    {"sign": "PLEASE", "category": "Phrase", "description": "Place the flat open palm over the center of the chest and rotate in a smooth, clockwise circle.", "tips": "Dynamic motion: gentle circular motion on chest."},
    {"sign": "I LOVE YOU", "category": "Phrase", "description": "Simultaneously extend the thumb, index finger, and pinky finger while curling the middle and ring fingers into the palm.", "tips": "Universal ASL symbol combining the handshapes for letters I, L, and Y."},
    {"sign": "PEACE", "category": "Phrase", "description": "Extend index and middle fingers straight upward spread apart in an open 'V' shape.", "tips": "Victory / Peace shape with palm facing forward."},
    {"sign": "OKAY", "category": "Phrase", "description": "Touch index fingertip and thumb tip in a circle, with middle, ring, and pinky fingers extended straight upward.", "tips": "Standard OK handshape."},
    {"sign": "THUMBS UP", "category": "Phrase", "description": "Form a closed fist with the thumb extended straight upward above the knuckles.", "tips": "Thumb pointing straight up; signifies approval, good, or agreement."},
    {"sign": "THUMBS DOWN", "category": "Phrase", "description": "Form a closed fist with the thumb extended straight downward toward the ground.", "tips": "Thumb pointing straight down; signifies disapproval or bad."},
    {"sign": "STOP", "category": "Phrase", "description": "Hold the flat open hand upright with fingers straight and palm facing directly outward toward the viewer.", "tips": "Flat palm facing forward signaling halt."},
]


# Root route - Serves Web UI
@app.get("/")
async def root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ok", "message": "Sign Language Translator API is running. UI located at /static/index.html"}


# System Health & Info
@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "service": "Sign Language Translator",
        "version": "1.0.0",
        "custom_gestures_count": len(gesture_trainer.get_registered_gestures()),
        "dictionary_size": len(ASL_DICTIONARY_DATA),
        "supported_video_formats": ["mp4", "webm", "mov", "avi"],
    }


# Session temporal trackers for REST / Practice Studio
session_trackers: Dict[str, Tuple[TemporalGestureTracker, float]] = {}


def get_session_tracker(session_id: str) -> TemporalGestureTracker:
    now = time.time()
    # Clean up expired sessions older than 5 minutes
    expired = [s for s, (_, last_seen) in session_trackers.items() if now - last_seen > 300]
    for s in expired:
        session_trackers.pop(s, None)

    if session_id not in session_trackers:
        session_trackers[session_id] = (TemporalGestureTracker(window_size=36, cooldown_seconds=0.8), now)

    tracker, _ = session_trackers[session_id]
    session_trackers[session_id] = (tracker, now)
    return tracker


# REST Frame Inference Endpoint
@app.post("/api/predict-frame")
async def predict_frame(payload: FramePredictRequest):
    try:
        # Decode base64 image
        raw_b64 = payload.image_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",")[1]
        img_bytes = base64.b64decode(raw_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image payload")

        hand_result = extractor.extract(img)

        if not hand_result.has_hands:
            sess_id = payload.session_id or "default_rest_session"
            if sess_id in session_trackers:
                session_trackers[sess_id][0].clear()
            classifier.reset_buffer()
            return {
                "has_hands": False,
                "predicted_sign": None,
                "confidence": 0.0,
                "is_stable": False,
                "hands": [],
            }

        primary_hand = hand_result.hands[0]
        feats = feature_engineer.extract_features(primary_hand.landmarks)

        sess_id = payload.session_id or "default_rest_session"
        temporal_tracker = get_session_tracker(sess_id)
        dyn_sign = temporal_tracker.update(
            primary_hand.landmarks,
            feats.finger_extensions,
            feats.fingertip_distances["thumb_index"],
        )
        dyn_likelihoods = temporal_tracker.get_dynamic_likelihoods()

        # Check custom gesture first
        custom_pred = gesture_trainer.predict_custom(feats)
        if custom_pred:
            pred_sign, conf = custom_pred
            rec_result = RecognitionResult(
                predicted_sign=pred_sign,
                confidence=conf,
                is_stable=True,
                top_predictions=[{"label": pred_sign, "confidence": conf}],
                sign_type="custom",
                handedness=primary_hand.handedness,
            )
        else:
            rec_result = classifier.classify_hand(
                primary_hand,
                dynamic_sign=dyn_sign,
                dynamic_likelihoods=dyn_likelihoods,
            )

        response_data: Dict[str, Any] = {
            "has_hands": True,
            "predicted_sign": rec_result.predicted_sign,
            "confidence": rec_result.confidence,
            "is_stable": rec_result.is_stable,
            "sign_type": rec_result.sign_type,
            "handedness": rec_result.handedness,
            "top_predictions": [
                {"label": p.label if hasattr(p, "label") else p["label"], "confidence": p.confidence if hasattr(p, "confidence") else p["confidence"]}
                for p in rec_result.top_predictions
            ],
            "finger_extensions": feats.finger_extensions,
            "bbox": primary_hand.bbox,
            "landmarks": primary_hand.landmarks,
        }

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket Live Stream for ultra-low latency webcam translation
@app.websocket("/ws/live-stream")
async def websocket_live_stream(websocket: WebSocket):
    await websocket.accept()
    temporal_tracker = TemporalGestureTracker(window_size=36, cooldown_seconds=0.8)
    session_classifier = ASLClassifier(stability_threshold=2)

    def process_frame(img: np.ndarray) -> Dict[str, Any]:
        hand_result = extractor.extract(img)
        if not hand_result.has_hands:
            temporal_tracker.clear()
            return {
                "has_hands": False,
                "predicted_sign": None,
                "confidence": 0.0,
                "is_stable": False,
            }

        primary_hand = hand_result.hands[0]
        feats = feature_engineer.extract_features(primary_hand.landmarks)

        dyn_sign = temporal_tracker.update(
            primary_hand.landmarks,
            feats.finger_extensions,
            feats.fingertip_distances["thumb_index"],
        )
        dyn_likelihoods = temporal_tracker.get_dynamic_likelihoods()

        custom_pred = gesture_trainer.predict_custom(feats)
        if custom_pred:
            pred_sign, conf = custom_pred
            return {
                "has_hands": True,
                "predicted_sign": pred_sign,
                "confidence": conf,
                "is_stable": True,
                "sign_type": "custom",
                "handedness": primary_hand.handedness,
                "landmarks": primary_hand.landmarks,
                "bbox": primary_hand.bbox,
                "top_predictions": [{"label": pred_sign, "confidence": conf}],
            }
        else:
            rec_result = session_classifier.classify_hand(
                primary_hand,
                dynamic_sign=dyn_sign,
                dynamic_likelihoods=dyn_likelihoods,
            )
            return {
                "has_hands": True,
                "predicted_sign": rec_result.predicted_sign,
                "confidence": rec_result.confidence,
                "is_stable": rec_result.is_stable,
                "sign_type": rec_result.sign_type,
                "handedness": rec_result.handedness,
                "landmarks": primary_hand.landmarks,
                "bbox": primary_hand.bbox,
                "top_predictions": [
                    {"label": p.label if hasattr(p, "label") else p["label"], "confidence": p.confidence if hasattr(p, "confidence") else p["confidence"]}
                    for p in rec_result.top_predictions
                ],
            }

    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break

            img_bytes = message.get("bytes")
            if not img_bytes:
                text_data = message.get("text")
                if text_data:
                    try:
                        req = json.loads(text_data)
                        raw_b64 = req.get("image_base64", "")
                        if raw_b64:
                            if "," in raw_b64:
                                raw_b64 = raw_b64.split(",")[1]
                            img_bytes = base64.b64decode(raw_b64)
                    except Exception:
                        continue

            if not img_bytes:
                continue

            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is None:
                await websocket.send_json({"has_hands": False, "error": "Invalid frame"})
                continue

            # Run in worker thread so event loop remains unblocked
            res_payload = await asyncio.to_thread(process_frame, img)
            await websocket.send_json(res_payload)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass


# Video File Upload and Processing Endpoints
def _async_process_video_job(job_id: str, file_path: str):
    """Background worker for video translation job."""
    try:
        def on_progress(pct: float, msg: str):
            if job_id in video_jobs:
                video_jobs[job_id]["progress"] = round(pct, 1)
                video_jobs[job_id]["status_message"] = msg

        result = video_processor.process_video(
            file_path,
            output_annotated_video=False,
            progress_callback=on_progress,
        )

        segments_data = [
            {
                "index": s.index,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "start_time_srt": s.start_time_srt,
                "end_time_srt": s.end_time_srt,
                "text": s.text,
                "confidence": s.confidence,
                "sign_type": s.sign_type,
            }
            for s in result.segments
        ]

        video_jobs[job_id]["status"] = "completed"
        video_jobs[job_id]["progress"] = 100.0
        video_jobs[job_id]["status_message"] = "Processing complete!"
        video_jobs[job_id]["result"] = {
            "video_id": result.video_id,
            "duration_seconds": result.duration_seconds,
            "total_frames": result.total_frames,
            "fps": result.fps,
            "segments": segments_data,
            "full_transcript": result.full_transcript,
            "srt_content": result.srt_content,
            "vtt_content": result.vtt_content,
        }

    except Exception as e:
        if job_id in video_jobs:
            video_jobs[job_id]["status"] = "failed"
            video_jobs[job_id]["error"] = str(e)
            video_jobs[job_id]["status_message"] = f"Error: {str(e)}"


@app.post("/api/upload-video")
async def upload_video(file: UploadFile = File(...)):
    filename = file.filename or "uploaded_video.mp4"
    ext = filename.split(".")[-1].lower()
    if ext not in ("mp4", "webm", "mov", "avi", "mkv"):
        raise HTTPException(status_code=400, detail=f"Unsupported format .{ext}. Supported: mp4, webm, mov, avi")

    job_id = str(uuid.uuid4())
    saved_filename = f"{job_id}_{filename}"
    saved_path = os.path.join(UPLOADS_DIR, saved_filename)

    # Save uploaded file asynchronously
    contents = await file.read()
    with open(saved_path, "wb") as f:
        f.write(contents)

    # Register job
    video_jobs[job_id] = {
        "job_id": job_id,
        "original_filename": filename,
        "saved_path": saved_path,
        "status": "processing",
        "progress": 0.0,
        "status_message": "Queued for processing...",
        "created_at": time.time(),
        "result": None,
    }

    # Start background processing thread
    t = threading.Thread(target=_async_process_video_job, args=(job_id, saved_path), daemon=True)
    t.start()

    return {
        "job_id": job_id,
        "filename": filename,
        "status": "processing",
        "message": "Video successfully uploaded and processing started.",
    }


@app.get("/api/video-status/{job_id}")
async def get_video_status(job_id: str):
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = video_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "status_message": job["status_message"],
        "error": job.get("error"),
    }


@app.get("/api/video-result/{job_id}")
async def get_video_result(job_id: str):
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = video_jobs[job_id]
    if job["status"] == "processing":
        return {"job_id": job_id, "status": "processing", "progress": job["progress"]}
    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=job.get("error", "Processing failed"))

    return job["result"]


@app.get("/api/video-file/{job_id}")
async def stream_video_file(job_id: str):
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    file_path = video_jobs[job_id]["saved_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    ext = os.path.splitext(file_path)[1].lower().replace(".", "")
    media_type = f"video/{ext}" if ext in ("mp4", "webm") else "application/octet-stream"
    return FileResponse(file_path, media_type=media_type)


@app.get("/api/export-subtitles/{job_id}")
async def export_subtitles(job_id: str, format: str = Query("srt", pattern="^(srt|vtt|json|txt)$")):
    if job_id not in video_jobs or video_jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=404, detail="Completed video job not found")

    res = video_jobs[job_id]["result"]

    if format == "srt":
        return PlainTextResponse(
            content=res["srt_content"],
            media_type="application/x-subrip",
            headers={"Content-Disposition": f'attachment; filename="transcript_{job_id[:8]}.srt"'},
        )
    elif format == "vtt":
        return PlainTextResponse(
            content=res["vtt_content"],
            media_type="text/vtt",
            headers={"Content-Disposition": f'attachment; filename="transcript_{job_id[:8]}.vtt"'},
        )
    elif format == "json":
        return JSONResponse(
            content=res["segments"],
            headers={"Content-Disposition": f'attachment; filename="transcript_{job_id[:8]}.json"'},
        )
    else:
        return PlainTextResponse(
            content=res["full_transcript"],
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="transcript_{job_id[:8]}.txt"'},
        )


# ASL Dictionary Endpoint
@app.get("/api/dictionary")
async def get_dictionary():
    return {
        "total": len(ASL_DICTIONARY_DATA),
        "dictionary": ASL_DICTIONARY_DATA,
    }


# Custom Gesture Endpoints
@app.post("/api/custom-gesture/save")
async def save_custom_gesture(payload: CustomGestureRequest):
    name = payload.gesture_name.strip().upper()
    if not name or len(name) < 2:
        raise HTTPException(status_code=400, detail="Invalid gesture name")

    if not payload.landmarks_batch:
        raise HTTPException(status_code=400, detail="No landmark frames provided")

    # Format landmark batch
    formatted_batch: List[List[Tuple[float, float, float]]] = []
    for raw_lms in payload.landmarks_batch:
        formatted = [(float(pt[0]), float(pt[1]), float(pt[2]) if len(pt) > 2 else 0.0) for pt in raw_lms]
        formatted_batch.append(formatted)

    total_samples = gesture_trainer.add_batch_samples(name, formatted_batch)

    return {
        "status": "success",
        "gesture_name": name,
        "total_samples": total_samples,
        "message": f"Custom gesture '{name}' trained and registered with {total_samples} samples.",
    }


@app.get("/api/custom-gesture/list")
async def list_custom_gestures():
    return {"gestures": gesture_trainer.get_registered_gestures()}


@app.delete("/api/custom-gesture/{gesture_name}")
async def delete_custom_gesture(gesture_name: str):
    success = gesture_trainer.delete_gesture(gesture_name)
    if not success:
        raise HTTPException(status_code=404, detail="Gesture not found")
    return {"status": "success", "message": f"Deleted '{gesture_name}'"}
