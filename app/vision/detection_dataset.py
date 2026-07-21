from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import shutil

from PIL import Image

CLASS_NAMES = ("chicken", "not_chicken")


@dataclass(frozen=True, slots=True)
class BoundingBox:
    class_name: str
    left: int
    top: int
    right: int
    bottom: int

    def __post_init__(self) -> None:
        if self.class_name not in CLASS_NAMES:
            raise ValueError(f"Classe inconnue: {self.class_name}")
        if self.right <= self.left or self.bottom <= self.top:
            raise ValueError("La boîte doit avoir une largeur et une hauteur positives")
        if self.left < 0 or self.top < 0:
            raise ValueError("Les coordonnées ne peuvent pas être négatives")

    def to_yolo(self, image_width: int, image_height: int) -> str:
        if image_width <= 0 or image_height <= 0:
            raise ValueError("Dimensions d'image invalides")
        if self.right > image_width or self.bottom > image_height:
            raise ValueError("La boîte dépasse les dimensions de l'image")
        class_id = CLASS_NAMES.index(self.class_name)
        center_x = ((self.left + self.right) / 2) / image_width
        center_y = ((self.top + self.bottom) / 2) / image_height
        width = (self.right - self.left) / image_width
        height = (self.bottom - self.top) / image_height
        return f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}"


class DetectionDataset:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.images_dir = self.root / "images"
        self.labels_dir = self.root / "labels"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.labels_dir.mkdir(parents=True, exist_ok=True)

    def add(self, source_image: Path, boxes: list[BoundingBox]) -> tuple[Path, Path]:
        source_image = Path(source_image)
        with Image.open(source_image) as image:
            width, height = image.size

        destination_image = self._unique_destination(source_image.name)
        shutil.copy2(source_image, destination_image)
        label_path = self.labels_dir / f"{destination_image.stem}.txt"
        label_path.write_text(
            "\n".join(box.to_yolo(width, height) for box in boxes) + ("\n" if boxes else ""),
            encoding="utf-8",
        )
        self._write_metadata()
        return destination_image, label_path

    def _unique_destination(self, filename: str) -> Path:
        candidate = self.images_dir / filename
        index = 1
        while candidate.exists():
            candidate = self.images_dir / f"{Path(filename).stem}_{index}{Path(filename).suffix}"
            index += 1
        return candidate

    def _write_metadata(self) -> None:
        yaml_text = (
            f"path: {self.root.resolve().as_posix()}\n"
            "train: images\n"
            "val: images\n"
            "names:\n"
            "  0: chicken\n"
            "  1: not_chicken\n"
        )
        (self.root / "dataset.yaml").write_text(yaml_text, encoding="utf-8")
        manifest = {
            "classes": list(CLASS_NAMES),
            "images": len(list(self.images_dir.glob("*"))),
            "labels": len(list(self.labels_dir.glob("*.txt"))),
        }
        (self.root / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
