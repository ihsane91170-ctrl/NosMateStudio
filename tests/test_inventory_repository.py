import json

import pytest

from app.inventory import (
    InvalidPetProfileError,
    JsonPetProfileRepository,
    PetProfileRegistry,
)


def write_profile(tmp_path, filename: str, data: dict) -> None:
    directory = tmp_path / "profiles"
    directory.mkdir(exist_ok=True)

    (directory / filename).write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_repository_loads_profiles_from_json(tmp_path) -> None:
    write_profile(
        tmp_path,
        "chicken.json",
        {
            "id": "chicken",
            "display_name": "Poule",
            "disposable": True,
            "desired_stars": 0,
            "template_name": "pet_chicken_row",
        },
    )

    write_profile(
        tmp_path,
        "ratufu.json",
        {
            "id": "ratufu",
            "display_name": "Ratufu",
            "disposable": False,
            "desired_stars": 6,
            "template_name": "pet_ratufu_row",
        },
    )

    repository = JsonPetProfileRepository(
        tmp_path / "profiles"
    )

    profiles = repository.load_all()

    assert tuple(profile.id for profile in profiles) == (
        "chicken",
        "ratufu",
    )
    assert profiles[0].disposable is True
    assert profiles[1].desired_stars == 6


def test_repository_loads_profiles_into_registry(tmp_path) -> None:
    write_profile(
        tmp_path,
        "chicken.json",
        {
            "id": "chicken",
            "display_name": "Poule",
            "disposable": True,
            "desired_stars": 0,
        },
    )

    registry = PetProfileRegistry()
    repository = JsonPetProfileRepository(
        tmp_path / "profiles"
    )

    repository.load_into(registry)

    assert registry.exists("chicken") is True
    assert registry.get("chicken").display_name == "Poule"


def test_repository_returns_empty_when_directory_is_missing(
    tmp_path,
) -> None:
    repository = JsonPetProfileRepository(
        tmp_path / "unknown"
    )

    assert repository.load_all() == ()


def test_repository_rejects_invalid_json(tmp_path) -> None:
    directory = tmp_path / "profiles"
    directory.mkdir()

    (directory / "invalid.json").write_text(
        "{invalid",
        encoding="utf-8",
    )

    repository = JsonPetProfileRepository(directory)

    with pytest.raises(InvalidPetProfileError):
        repository.load_all()


def test_repository_rejects_missing_required_field(
    tmp_path,
) -> None:
    write_profile(
        tmp_path,
        "invalid.json",
        {
            "id": "chicken",
            "disposable": True,
        },
    )

    repository = JsonPetProfileRepository(
        tmp_path / "profiles"
    )

    with pytest.raises(InvalidPetProfileError):
        repository.load_all()