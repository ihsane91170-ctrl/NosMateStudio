from __future__ import annotations

import json
from dataclasses import dataclass

from PIL import Image

from app.capture.flight_recorder import CaptureFlightRecorder
from app.vision.ai_detector import ObjectDetection
from app.vision.ai_target_selector import AITargetSelector


@dataclass
class Window:
    left: int = 100
    top: int = 200
    width: int = 640
    height: int = 480


def test_recorder_exports_images_and_json(tmp_path) -> None:
    detections = (
        ObjectDetection("chicken", 0.93, 10, 20, 60, 80),
        ObjectDetection("not_chicken", 0.88, 100, 120, 170, 200),
    )
    selected = AITargetSelector().choose(
        detections, image_width=640, image_height=480
    )
    recorder = CaptureFlightRecorder(tmp_path)

    directory = recorder.record_detection(
        image=Image.new("RGB", (640, 480)),
        detections=detections,
        selected=selected,
        window=Window(),
        confidence_threshold=0.80,
    )
    recorder.record_result(
        directory,
        success=False,
        message="Faux positif suspect",
        outcome="HP_UNKNOWN",
        attacks_sent=1,
        capture_attempts=0,
    )

    assert (directory / "capture_originale.png").is_file()
    assert (directory / "capture_annotee.png").is_file()
    data = json.loads((directory / "diagnostic.json").read_text(encoding="utf-8"))
    assert len(data["detections"]) == 2
    assert data["selected"]["detection"]["class_name"] == "chicken"
    assert data["selected"]["screen_click"] == [135, 250]
    assert data["result"]["success"] is False
    assert data["result"]["outcome"] == "HP_UNKNOWN"


def test_recorder_supports_no_selected_target(tmp_path) -> None:
    recorder = CaptureFlightRecorder(tmp_path)
    directory = recorder.record_detection(
        image=Image.new("RGB", (100, 100)),
        detections=(),
        selected=None,
        window=Window(width=100, height=100),
        confidence_threshold=0.80,
    )
    data = json.loads((directory / "diagnostic.json").read_text(encoding="utf-8"))
    assert data["selected"] is None
    assert data["detections"] == []
