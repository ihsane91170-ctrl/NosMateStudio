import pytest
from PIL import Image

from app.vision.template_repository import (
    TemplateAlreadyExistsError,
    TemplateNotFoundError,
    TemplateRepository,
)


def test_repository_saves_and_loads_template(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    source = Image.new("RGB", (120, 40))

    template = repository.save(
        "Bouton Accompagner",
        source,
    )

    loaded = repository.load_image(
        "bouton_accompagner"
    )

    assert template.name == "bouton_accompagner"
    assert template.path.exists()
    assert loaded.size == (120, 40)
    assert loaded.mode == "RGB"


def test_repository_lists_templates(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")

    repository.save(
        "pet_slot",
        Image.new("RGB", (50, 50)),
    )
    repository.save(
        "accompany_button",
        Image.new("RGB", (80, 30)),
    )

    templates = repository.list()

    assert tuple(
        template.name for template in templates
    ) == (
        "accompany_button",
        "pet_slot",
    )


def test_repository_rejects_duplicate_name(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    image = Image.new("RGB", (20, 20))

    repository.save("pet_slot", image)

    with pytest.raises(TemplateAlreadyExistsError):
        repository.save("pet_slot", image)


def test_repository_can_overwrite_template(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")

    repository.save(
        "pet_slot",
        Image.new("RGB", (20, 20)),
    )
    repository.save(
        "pet_slot",
        Image.new("RGB", (40, 30)),
        overwrite=True,
    )

    loaded = repository.load_image("pet_slot")

    assert loaded.size == (40, 30)


def test_repository_rejects_unknown_template(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")

    with pytest.raises(TemplateNotFoundError):
        repository.get("unknown")


def test_repository_deletes_template(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save(
        "pet_slot",
        Image.new("RGB", (20, 20)),
    )

    repository.delete("pet_slot")

    assert repository.list() == ()