from pathlib import Path

from PIL import Image

from app.vision.hp_state_reader import HpState, HpStateReader

FIXTURES = Path(__file__).parent / "fixtures"


def test_reads_one_hp_from_target_panel_crop() -> None:
    result = HpStateReader().read(Image.open(FIXTURES / "target_hp_one.png"))
    assert result.state is HpState.ONE
    assert result.hp_box is not None


def test_reads_full_hp_from_target_panel_crop() -> None:
    result = HpStateReader().read(Image.open(FIXTURES / "target_hp_full.png"))
    assert result.state is HpState.FULL
    assert result.hp_box is not None


def test_fullscreen_ignores_player_hp_and_reads_target_one_hp() -> None:
    image = Image.open(FIXTURES / "fullscreen_target_hp_one.png")
    reader = HpStateReader()
    result = reader.read(image)

    assert result.state is HpState.ONE
    assert result.hp_box is not None
    # Le panneau joueur est à gauche (~x 80-240). La cible est au centre.
    assert result.hp_box[0] > image.width * 0.28
