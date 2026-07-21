from app.familiar_production import (
    FamiliarBatch,
    FamiliarProductionController,
    FamiliarProductionStatus,
    FamiliarStage,
)


class TrainingStub:
    def __init__(self, outcomes=None):
        self.outcomes = iter(outcomes or [])
        self.calls = []
        self.use_default = outcomes is None

    def train_to_max(self, stars):
        self.calls.append(stars)
        return True if self.use_default else next(self.outcomes)


class UpgradeStub:
    def __init__(self, outcomes=None):
        self.outcomes = iter(outcomes or [])
        self.calls = []
        self.use_default = outcomes is None

    def upgrade(self, from_stars, to_stars):
        self.calls.append((from_stars, to_stars))
        return True if self.use_default else next(self.outcomes)


class ExtractionStub:
    def __init__(self, outcomes=None):
        self.outcomes = iter(outcomes or [])
        self.calls = []
        self.use_default = outcomes is None

    def extract_token(self, stars):
        self.calls.append(stars)
        return True if self.use_default else next(self.outcomes)


def test_extract_one_star_without_upgrade():
    training = TrainingStub()
    upgrade = UpgradeStub()
    extraction = ExtractionStub()

    result = FamiliarProductionController(training, upgrade, extraction).run(
        FamiliarBatch(count=2, start_stars=1, target_token_stars=1)
    )

    assert result.completed
    assert result.extracted_tokens == 2
    assert training.calls == [1, 1]
    assert upgrade.calls == []
    assert extraction.calls == [1, 1]


def test_train_upgrade_retrain_then_extract_three_star_token():
    training = TrainingStub()
    upgrade = UpgradeStub()
    extraction = ExtractionStub()
    stages = []

    result = FamiliarProductionController(
        training,
        upgrade,
        extraction,
        on_stage=lambda index, stage, stars: stages.append((index, stage, stars)),
    ).run(FamiliarBatch(count=1, start_stars=1, target_token_stars=3))

    assert result.completed
    assert training.calls == [1, 2, 3]
    assert upgrade.calls == [(1, 2), (2, 3)]
    assert extraction.calls == [3]
    assert stages == [
        (0, FamiliarStage.TRAIN_TO_MAX, 1),
        (0, FamiliarStage.UPGRADE_STAR, 1),
        (0, FamiliarStage.TRAIN_TO_MAX, 2),
        (0, FamiliarStage.UPGRADE_STAR, 2),
        (0, FamiliarStage.TRAIN_TO_MAX, 3),
        (0, FamiliarStage.EXTRACT_TOKEN, 3),
    ]


def test_failure_during_upgrade_stops_before_extraction():
    training = TrainingStub()
    upgrade = UpgradeStub([False])
    extraction = ExtractionStub()

    result = FamiliarProductionController(training, upgrade, extraction).run(
        FamiliarBatch(count=1, start_stars=1, target_token_stars=2)
    )

    assert result.status is FamiliarProductionStatus.UPGRADE_FAILED
    assert extraction.calls == []


def test_failure_during_training_stops_current_batch():
    training = TrainingStub([False])
    upgrade = UpgradeStub()
    extraction = ExtractionStub()

    result = FamiliarProductionController(training, upgrade, extraction).run(
        FamiliarBatch(count=3, start_stars=2, target_token_stars=2)
    )

    assert result.status is FamiliarProductionStatus.TRAINING_FAILED
    assert result.completed_familiars == 0
    assert extraction.calls == []
