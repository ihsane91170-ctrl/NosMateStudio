from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from PIL import Image, ImageDraw

from app.vision.ai_detector import ObjectDetection
from app.vision.ai_target_selector import RankedTarget


class CaptureFlightRecorder:
    """Journalise ce que le pipeline de capture a réellement vu et choisi."""

    def __init__(self, root_dir: Path) -> None:
        self._root_dir = Path(root_dir)
        self._lock = Lock()
        self._sequence = 0

    def record_detection(
        self,
        *,
        image: Image.Image,
        detections: tuple[ObjectDetection, ...],
        selected: RankedTarget | None,
        window: Any,
        confidence_threshold: float,
    ) -> Path:
        with self._lock:
            self._sequence += 1
            sequence = self._sequence

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        attempt_dir = self._root_dir / f"{stamp}_{sequence:04d}"
        attempt_dir.mkdir(parents=True, exist_ok=False)

        original = image.convert("RGB")
        original.save(attempt_dir / "capture_originale.png")

        annotated = original.copy()
        draw = ImageDraw.Draw(annotated)
        selected_detection = selected.detection if selected is not None else None

        for detection in detections:
            is_selected = detection is selected_detection
            # Rouge = cible retenue ; blanc = autre détection. Les couleurs sont
            # volontairement très contrastées pour faciliter le diagnostic.
            color = "red" if is_selected else "white"
            width = 4 if is_selected else 2
            box = (detection.left, detection.top, detection.right, detection.bottom)
            draw.rectangle(box, outline=color, width=width)
            draw.text(
                (detection.left, max(0, detection.top - 14)),
                f"{detection.class_name} {detection.confidence:.3f}",
                fill=color,
            )

        if selected_detection is not None:
            x, y = selected_detection.center
            draw.line((x - 10, y, x + 10, y), fill="red", width=3)
            draw.line((x, y - 10, x, y + 10), fill="red", width=3)

        annotated.save(attempt_dir / "capture_annotee.png")

        payload = {
            "created_at": datetime.now().isoformat(timespec="milliseconds"),
            "confidence_threshold": confidence_threshold,
            "window": {
                "left": int(getattr(window, "left", 0)),
                "top": int(getattr(window, "top", 0)),
                "width": int(getattr(window, "width", image.width)),
                "height": int(getattr(window, "height", image.height)),
            },
            "detections": [asdict(detection) for detection in detections],
            "selected": (
                {
                    "detection": asdict(selected.detection),
                    "score": selected.score,
                    "confidence_score": selected.confidence_score,
                    "center_score": selected.center_score,
                    "local_click": list(selected.detection.center),
                    "screen_click": [
                        int(getattr(window, "left", 0)) + selected.detection.center[0],
                        int(getattr(window, "top", 0)) + selected.detection.center[1],
                    ],
                }
                if selected is not None
                else None
            ),
            "result": None,
        }
        self._write_json(attempt_dir, payload)
        return attempt_dir

    def record_result(
        self,
        attempt_dir: Path,
        *,
        success: bool,
        message: str,
        outcome: str | None = None,
        attacks_sent: int | None = None,
        capture_attempts: int | None = None,
    ) -> None:
        path = Path(attempt_dir) / "diagnostic.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        payload["result"] = {
            "success": bool(success),
            "message": message,
            "outcome": outcome,
            "attacks_sent": attacks_sent,
            "capture_attempts": capture_attempts,
            "completed_at": datetime.now().isoformat(timespec="milliseconds"),
        }
        self._write_json(Path(attempt_dir), payload)

    @staticmethod
    def _write_json(attempt_dir: Path, payload: dict[str, Any]) -> None:
        (attempt_dir / "diagnostic.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
