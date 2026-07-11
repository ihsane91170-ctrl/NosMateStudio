from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.vision.template import VisionTemplate


class TemplateNotFoundError(LookupError):
    """Raised when a requested template does not exist."""


class TemplateAlreadyExistsError(ValueError):
    """Raised when a template name is already used."""


class TemplateRepository:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def save(
        self,
        name: str,
        image: Image.Image,
        *,
        overwrite: bool = False,
    ) -> VisionTemplate:
        normalized_name = self._normalize_name(name)
        path = self.directory / f"{normalized_name}.png"

        if path.exists() and not overwrite:
            raise TemplateAlreadyExistsError(
                f"Le template {normalized_name!r} existe déjà."
            )

        self.directory.mkdir(parents=True, exist_ok=True)
        image.save(path, format="PNG")

        return VisionTemplate(
            name=normalized_name,
            path=path,
        )

    def get(self, name: str) -> VisionTemplate:
        normalized_name = self._normalize_name(name)
        path = self.directory / f"{normalized_name}.png"

        if not path.exists():
            raise TemplateNotFoundError(
                f"Le template {normalized_name!r} est introuvable."
            )

        return VisionTemplate(
            name=normalized_name,
            path=path,
        )

    def load_image(self, name: str) -> Image.Image:
        template = self.get(name)

        with Image.open(template.path) as image:
            return image.convert("RGB")

    def list(self) -> tuple[VisionTemplate, ...]:
        if not self.directory.exists():
            return ()

        templates = [
            VisionTemplate(
                name=path.stem,
                path=path,
            )
            for path in sorted(self.directory.glob("*.png"))
        ]

        return tuple(templates)

    def delete(self, name: str) -> None:
        template = self.get(name)
        template.path.unlink()

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = name.strip().lower()
        normalized = normalized.replace(" ", "_")

        if not normalized:
            raise ValueError(
                "Le nom du template ne peut pas être vide."
            )

        allowed = set(
            "abcdefghijklmnopqrstuvwxyz0123456789_-"
        )

        if any(character not in allowed for character in normalized):
            raise ValueError(
                "Le nom du template contient des caractères invalides."
            )

        return normalized