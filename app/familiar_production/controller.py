from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Protocol


class FamiliarStage(Enum):
    TRAIN_TO_MAX = auto()
    UPGRADE_STAR = auto()
    EXTRACT_TOKEN = auto()


class FamiliarProductionStatus(Enum):
    COMPLETED = auto()
    STOPPED = auto()
    TRAINING_FAILED = auto()
    UPGRADE_FAILED = auto()
    EXTRACTION_FAILED = auto()


@dataclass(frozen=True, slots=True)
class FamiliarBatch:
    """Lot homogène de familiers ayant la même étoile de départ et le même objectif."""

    count: int
    start_stars: int
    target_token_stars: int

    def __post_init__(self) -> None:
        if self.count < 1:
            raise ValueError("count doit être supérieur ou égal à 1")
        if not 1 <= self.start_stars <= 5:
            raise ValueError("start_stars doit être compris entre 1 et 5")
        if not self.start_stars <= self.target_token_stars <= 5:
            raise ValueError(
                "target_token_stars doit être compris entre start_stars et 5"
            )


@dataclass(frozen=True, slots=True)
class FamiliarProductionResult:
    status: FamiliarProductionStatus
    completed_familiars: int
    requested_familiars: int
    extracted_tokens: int
    message: str

    @property
    def completed(self) -> bool:
        return self.status is FamiliarProductionStatus.COMPLETED


class FamiliarTrainingService(Protocol):
    def train_to_max(self, stars: int) -> bool:
        """Accompagne le familier, cible les protomonstres et attend son niveau max."""
        ...


class FamiliarUpgradeService(Protocol):
    def upgrade(self, from_stars: int, to_stars: int) -> bool:
        ...


class FamiliarExtractionService(Protocol):
    def extract_token(self, stars: int) -> bool:
        ...


class FamiliarProductionController:
    """Partie 2 : XP, étoiles et extraction, sans aucune logique de capture."""

    def __init__(
        self,
        training_service: FamiliarTrainingService,
        upgrade_service: FamiliarUpgradeService,
        extraction_service: FamiliarExtractionService,
        *,
        stop_requested: Callable[[], bool] | None = None,
        on_stage: Callable[[int, FamiliarStage, int], None] | None = None,
    ) -> None:
        self._training_service = training_service
        self._upgrade_service = upgrade_service
        self._extraction_service = extraction_service
        self._stop_requested = stop_requested or (lambda: False)
        self._on_stage = on_stage

    def run(self, batch: FamiliarBatch) -> FamiliarProductionResult:
        completed = 0
        extracted = 0

        for familiar_index in range(batch.count):
            if self._stop_requested():
                return self._result(
                    FamiliarProductionStatus.STOPPED,
                    completed,
                    batch,
                    extracted,
                    "Production arrêtée par l'utilisateur.",
                )

            current_stars = batch.start_stars

            while True:
                self._notify(familiar_index, FamiliarStage.TRAIN_TO_MAX, current_stars)
                if not self._training_service.train_to_max(current_stars):
                    return self._result(
                        FamiliarProductionStatus.TRAINING_FAILED,
                        completed,
                        batch,
                        extracted,
                        f"Échec de la montée au niveau maximum en {current_stars}★.",
                    )

                if current_stars == batch.target_token_stars:
                    self._notify(
                        familiar_index,
                        FamiliarStage.EXTRACT_TOKEN,
                        current_stars,
                    )
                    if not self._extraction_service.extract_token(current_stars):
                        return self._result(
                            FamiliarProductionStatus.EXTRACTION_FAILED,
                            completed,
                            batch,
                            extracted,
                            f"Échec de l'extraction du jeton {current_stars}★.",
                        )
                    extracted += 1
                    completed += 1
                    break

                self._notify(familiar_index, FamiliarStage.UPGRADE_STAR, current_stars)
                if not self._upgrade_service.upgrade(current_stars, current_stars + 1):
                    return self._result(
                        FamiliarProductionStatus.UPGRADE_FAILED,
                        completed,
                        batch,
                        extracted,
                        f"Échec de l'augmentation {current_stars}★ → {current_stars + 1}★.",
                    )

                # Règle métier : après une augmentation d'étoile, le niveau retombe à 1.
                # La boucle réentraîne donc le familier avant l'étape suivante.
                current_stars += 1

        return self._result(
            FamiliarProductionStatus.COMPLETED,
            completed,
            batch,
            extracted,
            f"{extracted} jeton(s) {batch.target_token_stars}★ extrait(s).",
        )

    def _notify(self, index: int, stage: FamiliarStage, stars: int) -> None:
        if self._on_stage is not None:
            self._on_stage(index, stage, stars)

    @staticmethod
    def _result(
        status: FamiliarProductionStatus,
        completed: int,
        batch: FamiliarBatch,
        extracted: int,
        message: str,
    ) -> FamiliarProductionResult:
        return FamiliarProductionResult(
            status=status,
            completed_familiars=completed,
            requested_familiars=batch.count,
            extracted_tokens=extracted,
            message=message,
        )
