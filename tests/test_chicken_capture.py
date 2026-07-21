from PIL import Image

from app.combat.chicken_capture import (
    CaptureOutcome,
    ChickenCaptureConfig,
    ChickenCaptureService,
)
from app.vision.hp_state_reader import HpReadResult, HpState


class FakeActions:
    def __init__(self) -> None:
        self.calls = []

    def click(self, x, y): self.calls.append(("click", x, y))
    def wait(self, seconds): self.calls.append(("wait", seconds))
    def press(self, key): self.calls.append(("press", key))
    def double_click(self, x, y): self.calls.append(("double_click", x, y))
    def press_capture_azerty(self): self.calls.append(("capture",))


class SequenceReader:
    def __init__(self, states):
        self.states = iter(states)

    def read(self, _image):
        return HpReadResult(next(self.states), 0.0, 0.0, None)


def image():
    return Image.new("RGB", (10, 10))


def config(**overrides):
    values = {
        "max_attacks": 3,
        "confirmation_reads": 2,
        "max_capture_attempts": 4,
        "capture_success_reads": 2,
        "selection_delay_seconds": 0,
        "hp_update_delay_seconds": 0,
        "confirmation_delay_seconds": 0,
        "capture_result_delay_seconds": 0,
        "capture_retry_delay_seconds": 0,
    }
    values.update(overrides)
    return ChickenCaptureConfig(**values)


def test_capture_succeeds_on_first_attempt() -> None:
    actions = FakeActions()
    service = ChickenCaptureService(
        actions,
        SequenceReader([HpState.ONE, HpState.ONE, HpState.UNKNOWN, HpState.UNKNOWN]),
    )

    result = service.execute(x=10, y=20, capture_image=image, config=config())

    assert result.outcome is CaptureOutcome.CAPTURE_SENT
    assert result.attacks_sent == 1
    assert result.capture_attempts == 1
    assert actions.calls.count(("capture",)) == 1


def test_failed_capture_is_retried_without_new_attack() -> None:
    actions = FakeActions()
    service = ChickenCaptureService(
        actions,
        SequenceReader(
            [
                HpState.ONE,
                HpState.ONE,
                HpState.ONE,      # première capture échouée
                HpState.UNKNOWN,  # deuxième capture réussie
                HpState.UNKNOWN,
            ]
        ),
    )

    result = service.execute(x=10, y=20, capture_image=image, config=config())

    assert result.outcome is CaptureOutcome.CAPTURE_SENT
    assert result.capture_attempts == 2
    assert actions.calls.count(("capture",)) == 2
    assert actions.calls.count(("press", "space")) == 1
    assert not any(call[0] == "double_click" for call in actions.calls)


def test_capture_stops_after_configured_maximum() -> None:
    actions = FakeActions()
    service = ChickenCaptureService(
        actions,
        SequenceReader(
            [HpState.ONE, HpState.ONE, HpState.ONE, HpState.ONE, HpState.ONE]
        ),
    )

    result = service.execute(
        x=10,
        y=20,
        capture_image=image,
        config=config(max_capture_attempts=3),
    )

    assert result.outcome is CaptureOutcome.MAX_CAPTURE_ATTEMPTS_REACHED
    assert result.capture_attempts == 3
    assert actions.calls.count(("capture",)) == 3
    assert actions.calls.count(("press", "space")) == 1


def test_full_then_one_is_retried_and_captured() -> None:
    actions = FakeActions()
    service = ChickenCaptureService(
        actions,
        SequenceReader(
            [
                HpState.FULL,
                HpState.ONE,
                HpState.ONE,
                HpState.UNKNOWN,
                HpState.UNKNOWN,
            ]
        ),
    )

    result = service.execute(x=10, y=20, capture_image=image, config=config())

    assert result.outcome is CaptureOutcome.CAPTURE_SENT
    assert result.attacks_sent == 2
    assert ("press", "space") in actions.calls
    assert ("double_click", 10, 20) in actions.calls


def test_unknown_before_capture_never_sends_capture() -> None:
    actions = FakeActions()
    service = ChickenCaptureService(actions, SequenceReader([HpState.UNKNOWN]))

    result = service.execute(x=1, y=2, capture_image=image, config=config())

    assert result.outcome is CaptureOutcome.HP_UNKNOWN
    assert ("capture",) not in actions.calls
