from pathlib import Path

from PIL import Image
import pytest

from app.vision.detection_dataset import BoundingBox, DetectionDataset


def test_box_converts_to_yolo() -> None:
    box = BoundingBox("chicken", 10, 20, 30, 60)
    assert box.to_yolo(100, 100) == "0 0.200000 0.400000 0.200000 0.400000"


def test_negative_class_uses_id_one() -> None:
    box = BoundingBox("not_chicken", 0, 0, 20, 20)
    assert box.to_yolo(100, 100).startswith("1 ")


def test_invalid_box_is_rejected() -> None:
    with pytest.raises(ValueError):
        BoundingBox("chicken", 10, 10, 5, 20)


def test_dataset_writes_image_label_and_metadata(tmp_path: Path) -> None:
    source = tmp_path / "capture.png"
    Image.new("RGB", (200, 100)).save(source)
    dataset = DetectionDataset(tmp_path / "dataset")
    image_path, label_path = dataset.add(
        source, [BoundingBox("chicken", 10, 10, 50, 50)]
    )
    assert image_path.exists()
    assert label_path.read_text(encoding="utf-8").startswith("0 ")
    assert (dataset.root / "dataset.yaml").exists()
    assert (dataset.root / "manifest.json").exists()


def test_dataset_does_not_overwrite_same_filename(tmp_path: Path) -> None:
    source = tmp_path / "capture.png"
    Image.new("RGB", (20, 20)).save(source)
    dataset = DetectionDataset(tmp_path / "dataset")
    first, _ = dataset.add(source, [])
    second, _ = dataset.add(source, [])
    assert first != second
