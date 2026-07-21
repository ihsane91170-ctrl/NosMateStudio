from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path

from PIL import Image, ImageDraw

from app.vision.hp_state_reader import HpReadResult, HpStateReader


@dataclass(frozen=True, slots=True)
class HpDiagnosticExport:
    directory: Path
    result: HpReadResult
    original_path: Path
    annotated_path: Path
    search_zone_path: Path
    hp_zone_path: Path | None
    json_path: Path


class HpDiagnosticExporter:
    """Exporte exactement ce que le lecteur de PV analyse."""

    def __init__(self, reader: HpStateReader, output_root: Path) -> None:
        self._reader = reader
        self._output_root = output_root

    def export(self, image: Image.Image) -> HpDiagnosticExport:
        result = self._reader.read(image)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        directory = self._output_root / f"hp_{stamp}"
        directory.mkdir(parents=True, exist_ok=False)

        original = image.convert("RGB")
        original_path = directory / "capture_originale.png"
        original.save(original_path)

        search_box = self._reader.search_box(original)
        search_zone_path = directory / "zone_recherche.png"
        original.crop(search_box).save(search_zone_path)

        annotated = original.copy()
        painter = ImageDraw.Draw(annotated)
        painter.rectangle(search_box, outline="cyan", width=3)
        painter.text((search_box[0] + 4, search_box[1] + 4), "ZONE RECHERCHE PV", fill="cyan")

        hp_zone_path: Path | None = None
        if result.hp_box is not None:
            painter.rectangle(result.hp_box, outline="yellow", width=3)
            painter.text(
                (result.hp_box[0], max(0, result.hp_box[1] - 18)),
                f"HP {result.state.value}",
                fill="yellow",
            )
            hp_zone_path = directory / "zone_hp.png"
            # PIL crop exclut les bornes droite/basse.
            left, top, right, bottom = result.hp_box
            original.crop((left, top, right + 1, bottom + 1)).save(hp_zone_path)

        annotated_path = directory / "capture_annotee.png"
        annotated.save(annotated_path)

        payload = {
            "state": result.state.value,
            "green_ratio": result.green_ratio,
            "red_ratio": result.red_ratio,
            "hp_box": result.hp_box,
            "search_box": search_box,
            "image_size": [original.width, original.height],
            "files": {
                "original": original_path.name,
                "annotated": annotated_path.name,
                "search_zone": search_zone_path.name,
                "hp_zone": hp_zone_path.name if hp_zone_path else None,
            },
        }
        json_path = directory / "diagnostic.json"
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return HpDiagnosticExport(
            directory=directory,
            result=result,
            original_path=original_path,
            annotated_path=annotated_path,
            search_zone_path=search_zone_path,
            hp_zone_path=hp_zone_path,
            json_path=json_path,
        )
