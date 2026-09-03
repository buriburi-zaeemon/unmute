#!/usr/bin/env python3
"""
Unmute Launcher Script
Initializes dependencies, verifies AI models, and starts the FastAPI server.
"""

import os
import sys
import argparse
import webbrowser
import threading
import time
import urllib.request

# Ensure current directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

BANNER = r"""
  _   _                       _       
 | | | |_ __  _ __ ___  _   _| |_ ___ 
 | | | | '_ \| '_ ` _ \| | | | __/ _ \
 | |_| | | | | | | | | | |_| | ||  __/
  \___/|_| |_|_| |_| |_|\__,_|\__\___|
                                      
      AI-Powered Real-Time ASL Translation System
"""

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = os.path.join(SCRIPT_DIR, "models", "hand_landmarker.task")


def check_and_download_model():
    os.makedirs(os.path.join(SCRIPT_DIR, "models"), exist_ok=True)
    if not os.path.exists(MODEL_PATH) or os.path.getsize(MODEL_PATH) < 1000:
        print("[*] MediaPipe Hand Landmarker model not found. Downloading official task model...")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print(f"[+] Download complete: {MODEL_PATH} ({os.path.getsize(MODEL_PATH):,} bytes)")
        except Exception as e:
            print(f"[-] Warning: Failed to download model: {e}")
    else:
        print(f"[+] AI Model ready: {MODEL_PATH}")


def open_browser(url: str, delay: float = 1.2):
    def _open():
        time.sleep(delay)
        print(f"[*] Opening browser at {url}...")
        webbrowser.open(url)
    threading.Thread(target=_open, daemon=True).start()


def main():
    parser = argparse.ArgumentParser(description="Start Unmute ASL Translation Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8090, help="Port to listen on (default: 8090)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    args = parser.parse_args()

    print(BANNER)
    print("=" * 60)
    print(f" Python Version : {sys.version.split()[0]}")
    print(f" Working Dir    : {SCRIPT_DIR}")
    print(f" Target Server  : http://{args.host}:{args.port}")
    print("=" * 60)

    # Verify model assets
    check_and_download_model()

    # Launch browser if requested
    if not args.no_browser:
        open_browser(f"http://{args.host}:{args.port}")

    # Start Uvicorn
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        app_dir=SCRIPT_DIR,
    )


if __name__ == "__main__":
    main()
