import pytest
from PIL import Image

from app.automation.action_engine import ActionEngine
from app.combat.target_attack import AttackState, TargetAttackController, TargetValidator
from app.vision.ai_detector import ObjectDetection
from app.vision.ai_target_selector import AITargetSelector
from app.vision.window_detector import GameWindow


class DetectorStub:
    def __init__(self, batches): self.batches = list(batches); self.calls = 0
    def detect(self, image, *, confidence=0.5):
        self.calls += 1
        return self.batches.pop(0)


class ScreenshotStub:
    def capture(self, window): return Image.new("RGB", (window.width, window.height))


class MouseStub:
    def __init__(self): self.clicks=[]
    def click(self,x,y): self.clicks.append((x,y))
    def double_click(self,x,y): pass


class KeyboardStub:
    def __init__(self): self.keys=[]
    def press(self,key): self.keys.append(key)


class WaitStub:
    def __init__(self): self.waits=[]
    def wait(self,s): self.waits.append(s)


def make_controller(detector, mouse, keyboard, waiter, *, attempts=2, retry_delay=.7):
    return TargetAttackController(
        detector=detector,
        selector=AITargetSelector(),
        validator=TargetValidator(maximum_center_distance=60),
        action_engine=ActionEngine(mouse=mouse, keyboard=keyboard, waiter=waiter),
        screenshot_provider=ScreenshotStub(),
        attack_key="1",
        click_to_validation_delay=.4,
        validation_to_attack_delay=.2,
        attack_retry_delay=retry_delay,
        maximum_attack_attempts=attempts,
    )


def chicken(x=100, y=100):
    return ObjectDetection("chicken", .95, x, y, x + 40, y + 40)


def test_sends_bounded_attack_retries_while_target_remains_visible():
    detector=DetectorStub([(chicken(),), (chicken(8+100,4+100),), (chicken(12+100,6+100),)])
    mouse=MouseStub(); keyboard=KeyboardStub(); waiter=WaitStub()
    result=make_controller(detector,mouse,keyboard,waiter,attempts=2).run_once(GameWindow("NosTale",50,70,800,600))
    assert result.success
    assert result.attempts_sent == 2
    assert mouse.clicks == [(170,190)]
    assert keyboard.keys == ["1", "1"]
    assert detector.calls == 3
    assert waiter.waits == [.4, .2, .7]
    assert [e.state for e in result.events].count(AttackState.ATTACK_ATTEMPT) == 2


def test_stops_retry_when_target_disappears_after_first_attempt():
    detector=DetectorStub([(chicken(),), (chicken(108,104),), ()])
    mouse=MouseStub(); keyboard=KeyboardStub(); waiter=WaitStub()
    result=make_controller(detector,mouse,keyboard,waiter,attempts=3).run_once(GameWindow("NosTale",0,0,800,600))
    assert result.success
    assert result.attempts_sent == 1
    assert keyboard.keys == ["1"]
    assert "disparition" in result.message


def test_attack_is_cancelled_when_target_cannot_be_revalidated_after_click():
    detector=DetectorStub([(chicken(),), ()]); mouse=MouseStub(); keyboard=KeyboardStub(); waiter=WaitStub()
    result=make_controller(detector,mouse,keyboard,waiter).run_once(GameWindow("NosTale",0,0,800,600))
    assert not result.success
    assert result.state is AttackState.FAILED
    assert keyboard.keys == []
    assert "annulée" in result.message


def test_target_validator_rejects_distant_chicken():
    validator=TargetValidator(maximum_center_distance=20)
    original=ObjectDetection("chicken",.9,0,0,20,20)
    distant=ObjectDetection("chicken",.9,100,100,120,120)
    assert validator.find_matching(original,(distant,)) is None


def test_controller_rejects_invalid_attempt_count():
    with pytest.raises(ValueError):
        make_controller(DetectorStub([]), MouseStub(), KeyboardStub(), WaitStub(), attempts=0)
