from pathlib import Path

from PIL import Image

from app.vision.hp_state_reader import HpState, HpStateReader


def test_reads_one_hp_reference() -> None:
    image = Image.open(Path(__file__).parent / 'fixtures' / 'hp_one.png')
    result = HpStateReader().read(image)
    assert result.state is HpState.ONE


def test_reads_full_hp_reference() -> None:
    image = Image.open(Path(__file__).parent / 'fixtures' / 'hp_full.png')
    result = HpStateReader().read(image)
    assert result.state is HpState.FULL
