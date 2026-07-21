from app.automation.action_engine import ActionEngine
from app.combat.target_attack import AttackAttempt, AttackConfig, TargetAttackService


class MouseSpy:
    def __init__(self): self.calls=[]
    def click(self,x,y): self.calls.append(("click",x,y))
    def double_click(self,x,y): self.calls.append(("double_click",x,y))


class KeyboardSpy:
    def __init__(self): self.keys=[]
    def press(self,key): self.keys.append(key)


def test_attack_uses_space_then_double_click_and_never_capture():
    mouse=MouseSpy(); keyboard=KeyboardSpy(); waits=[]
    service=TargetAttackService(ActionEngine(mouse, keyboard, sleep_fn=waits.append))
    result=service.execute(x=120,y=240,config=AttackConfig(max_attempts=2,selection_delay_seconds=.4,retry_delay_seconds=.7))
    assert result.attempts == (AttackAttempt.SPACE, AttackAttempt.DOUBLE_CLICK)
    assert mouse.calls == [("click",120,240),("double_click",120,240)]
    assert keyboard.keys == ["space"]
    assert "&" not in keyboard.keys and "1" not in keyboard.keys
    assert waits == [.4,.7]


def test_single_attempt_only_presses_space():
    mouse=MouseSpy(); keyboard=KeyboardSpy()
    service=TargetAttackService(ActionEngine(mouse, keyboard, sleep_fn=lambda _: None))
    service.execute(x=10,y=20,config=AttackConfig(max_attempts=1))
    assert mouse.calls == [("click",10,20)]
    assert keyboard.keys == ["space"]
