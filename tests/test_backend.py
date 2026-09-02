"""
Unit and integration tests for FastAPI backend routes.
"""

import os
import sys
import base64
import numpy as np
import cv2
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.main import app

client = TestClient(app)


def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "dictionary_size" in data
    assert data["dictionary_size"] > 20


def test_dictionary_endpoint():
    response = client.get("/api/dictionary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 20
    assert any(item["sign"] == "A" for item in data["dictionary"])
    assert any(item["sign"] == "HELLO" for item in data["dictionary"])


def test_predict_frame_blank_image():
    # Create blank black image
    blank = np.zeros((240, 320, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", blank)
    b64 = base64.b64encode(buffer).decode("utf-8")

    response = client.post("/api/predict-frame", json={"image_base64": b64})
    assert response.status_code == 200
    data = response.json()
    assert data["has_hands"] is False


def test_custom_gesture_endpoints():
    mock_lms = [[0.5, 0.8, 0.0]] * 21
    payload = {
        "gesture_name": "TEST_GESTURE",
        "landmarks_batch": [mock_lms, mock_lms, mock_lms, mock_lms],
    }
    # Save custom gesture
    save_res = client.post("/api/custom-gesture/save", json=payload)
    assert save_res.status_code == 200
    assert save_res.json()["status"] == "success"

    # List custom gestures
    list_res = client.get("/api/custom-gesture/list")
    assert list_res.status_code == 200
    assert any(g["name"] == "TEST_GESTURE" for g in list_res.json()["gestures"])

    # Delete custom gesture
    del_res = client.delete("/api/custom-gesture/TEST_GESTURE")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"
