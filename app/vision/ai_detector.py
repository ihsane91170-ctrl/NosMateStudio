from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PIL import Image


@dataclass(frozen=True, slots=True)
class ObjectDetection:
    class_name: str
    confidence: float
    left: int
    top: int
    right: int
    bottom: int

    @property
    def center(self) -> tuple[int, int]:
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)


class ObjectDetector(Protocol):
    def detect(self, image: Image.Image, *, confidence: float = 0.50) -> tuple[ObjectDetection, ...]:
        ...


class ModelNotAvailableError(RuntimeError):
    pass


class UltralyticsObjectDetector:
    """Détecteur YOLO chargé à la demande.

    L'import ultralytics est volontairement différé pour ne pas rendre
    NosMate Studio inutilisable lorsque la dépendance ou le modèle manque.
    """

    def __init__(self, model_path: Path) -> None:
        self.model_path = Path(model_path)
        self._model = None

    def _load(self):
        if not self.model_path.is_file():
            raise ModelNotAvailableError(
                f"Modèle IA introuvable : {self.model_path}"
            )
        if self._model is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise ModelNotAvailableError(
                    "La dépendance ultralytics n'est pas installée. "
                    "Exécutez : python -m pip install ultralytics"
                ) from exc
            self._model = YOLO(str(self.model_path))
        return self._model

    def detect(self, image: Image.Image, *, confidence: float = 0.50) -> tuple[ObjectDetection, ...]:
        if not 0.0 < confidence <= 1.0:
            raise ValueError("confidence doit être comprise entre 0 et 1")
        model = self._load()
        results = model.predict(source=image, conf=confidence, verbose=False)
        detections: list[ObjectDetection] = []
        for result in results:
            names = result.names
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0].item())
                score = float(box.conf[0].item())
                left, top, right, bottom = [int(round(v)) for v in box.xyxy[0].tolist()]
                detections.append(
                    ObjectDetection(
                        class_name=str(names[cls_id]),
                        confidence=score,
                        left=left,
                        top=top,
                        right=right,
                        bottom=bottom,
                    )
                )
        return tuple(detections)
