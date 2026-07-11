from __future__ import annotations

from app.inventory.models import PetProfile


class PetProfileAlreadyExistsError(ValueError):
    """Raised when a profile identifier is already registered."""


class PetProfileNotFoundError(KeyError):
    """Raised when a requested profile does not exist."""


class PetProfileTemplateAlreadyExistsError(ValueError):
    """Raised when a visual template is already assigned."""


class PetProfileRegistry:
    def __init__(self) -> None:
        self._profiles: dict[str, PetProfile] = {}
        self._profiles_by_template: dict[str, PetProfile] = {}

    def register(self, profile: PetProfile) -> None:
        if profile.id in self._profiles:
            raise PetProfileAlreadyExistsError(
                f"Le profil {profile.id!r} existe déjà."
            )

        if (
            profile.template_name is not None
            and profile.template_name in self._profiles_by_template
        ):
            raise PetProfileTemplateAlreadyExistsError(
                
                    f"Le template {profile.template_name!r} "
                    "est déjà associé à un profil."
                
            )

        self._profiles[profile.id] = profile

        if profile.template_name is not None:
            self._profiles_by_template[
                profile.template_name
            ] = profile

    def get(self, profile_id: str) -> PetProfile:
        normalized_id = self._normalize_id(profile_id)

        try:
            return self._profiles[normalized_id]
        except KeyError as exc:
            raise PetProfileNotFoundError(
                f"Le profil {normalized_id!r} est introuvable."
            ) from exc

    def get_by_template(
        self,
        template_name: str,
    ) -> PetProfile:
        normalized_template = self._normalize_template_name(
            template_name
        )

        try:
            return self._profiles_by_template[
                normalized_template
            ]
        except KeyError as exc:
            raise PetProfileNotFoundError(
                
                    "Aucun profil n'est associé au template "
                    f"{normalized_template!r}."
                
            ) from exc

    def exists(self, profile_id: str) -> bool:
        normalized_id = self._normalize_id(profile_id)
        return normalized_id in self._profiles

    def exists_by_template(
        self,
        template_name: str,
    ) -> bool:
        normalized_template = self._normalize_template_name(
            template_name
        )
        return normalized_template in self._profiles_by_template

    def remove(self, profile_id: str) -> PetProfile:
        normalized_id = self._normalize_id(profile_id)

        try:
            profile = self._profiles.pop(normalized_id)
        except KeyError as exc:
            raise PetProfileNotFoundError(
                f"Le profil {normalized_id!r} est introuvable."
            ) from exc

        if profile.template_name is not None:
            self._profiles_by_template.pop(
                profile.template_name,
                None,
            )

        return profile

    def all(self) -> tuple[PetProfile, ...]:
        return tuple(
            sorted(
                self._profiles.values(),
                key=lambda profile: profile.id,
            )
        )

    def __len__(self) -> int:
        return len(self._profiles)

    @staticmethod
    def _normalize_id(profile_id: str) -> str:
        normalized_id = profile_id.strip().lower()

        if not normalized_id:
            raise ValueError(
                "L'identifiant du profil ne peut pas être vide."
            )

        return normalized_id

    @staticmethod
    def _normalize_template_name(
        template_name: str,
    ) -> str:
        normalized_template = template_name.strip()

        if not normalized_template:
            raise ValueError(
                "Le nom du template ne peut pas être vide."
            )

        return normalized_template