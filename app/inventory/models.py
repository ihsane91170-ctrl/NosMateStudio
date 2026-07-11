from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PetProfile:
    id: str
    display_name: str
    disposable: bool
    desired_stars: int = 6
    template_name: str | None = None

    def __post_init__(self) -> None:
        normalized_id = self.id.strip().lower()
        normalized_name = self.display_name.strip()

        if not normalized_id:
            raise ValueError(
                "L'identifiant du profil ne peut pas être vide."
            )

        if not normalized_name:
            raise ValueError(
                "Le nom du familier ne peut pas être vide."
            )

        if not 0 <= self.desired_stars <= 6:
            raise ValueError(
                "Le nombre d'étoiles souhaité doit être compris entre 0 et 6."
            )

        normalized_template = (
            self.template_name.strip()
            if self.template_name is not None
            else None
        )

        if normalized_template == "":
            normalized_template = None

        object.__setattr__(self, "id", normalized_id)
        object.__setattr__(self, "display_name", normalized_name)
        object.__setattr__(self, "template_name", normalized_template)

@dataclass(slots=True)
class PetInstance:
    profile: PetProfile
    level: int = 1
    stars: int = 1
    locked: bool = False
    favorite: bool = False

    def __post_init__(self) -> None:
        if not 1 <= self.level <= 99:
            raise ValueError(
                "Le niveau du familier doit être compris entre 1 et 99."
            )

        if not 0 <= self.stars <= 6:
            raise ValueError(
                "Le nombre d'étoiles doit être compris entre 0 et 6."
            )

    @property
    def can_be_sacrificed(self) -> bool:
        return (
            self.profile.disposable
            and not self.locked
            and not self.favorite
        )

    @property
    def needs_upgrade(self) -> bool:
        return self.stars < self.profile.desired_stars


@dataclass(slots=True)
class Inventory:
    _pets: list[PetInstance] = field(default_factory=list)

    def add(self, pet: PetInstance) -> None:
        self._pets.append(pet)

    def remove(self, pet: PetInstance) -> None:
        try:
            self._pets.remove(pet)
        except ValueError as exc:
            raise ValueError(
                "Le familier n'existe pas dans l'inventaire."
            ) from exc

    def count(self, profile_id: str) -> int:
        normalized_id = profile_id.strip().lower()

        return sum(
            pet.profile.id == normalized_id
            for pet in self._pets
        )

    def disposable_pets(self) -> tuple[PetInstance, ...]:
        return tuple(
            pet
            for pet in self._pets
            if pet.can_be_sacrificed
        )

    def protected_pets(self) -> tuple[PetInstance, ...]:
        return tuple(
            pet
            for pet in self._pets
            if not pet.can_be_sacrificed
        )

    def pets_needing_upgrade(self) -> tuple[PetInstance, ...]:
        return tuple(
            pet
            for pet in self._pets
            if pet.needs_upgrade
        )

    def __len__(self) -> int:
        return len(self._pets)

    def __iter__(self) -> Iterator[PetInstance]:
        return iter(self._pets)