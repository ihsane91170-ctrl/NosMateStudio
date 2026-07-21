import json
from pathlib import Path

from PIL import Image, ImageDraw

from app.vision.hp_diagnostic import HpDiagnosticExporter
from app.vision.hp_state_reader import HpState, HpStateReader


def _screen(full: bool) -> Image.Image:
    image = Image.new("RGB", (400, 240), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 80, 219, 88), fill=(20, 80, 180))
    if full:
        draw.rectangle((20, 61, 219, 69), fill=(30, 170, 40))
    else:
        draw.rectangle((20, 61, 23, 69), fill=(190, 25, 25))
    return image


def test_diagnostic_exports_images_and_json(tmp_path: Path) -> None:
    exporter = HpDiagnosticExporter(HpStateReader(), tmp_path)
    diagnostic = exporter.export(_screen(full=False))

    assert diagnostic.result.state is HpState.ONE
    assert diagnostic.original_path.exists()
    assert diagnostic.annotated_path.exists()
    assert diagnostic.search_zone_path.exists()
    assert diagnostic.hp_zone_path is not None and diagnostic.hp_zone_path.exists()
    payload = json.loads(diagnostic.json_path.read_text(encoding="utf-8"))
    assert payload["state"] == "ONE_HP"
    assert payload["hp_box"] is not None
