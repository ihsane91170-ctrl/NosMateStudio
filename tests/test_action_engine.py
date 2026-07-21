from random import Random

import pytest

from app.automation.action_engine import ActionEngine, ActionEngineConfig


class MouseStub:
    def __init__(self): self.calls = []
    def click(self, x, y): self.calls.append(("click", x, y))
    def double_click(self, x, y): self.calls.append(("double", x, y))


class KeyboardStub:
    def __init__(self): self.keys = []
    def press(self, key): self.keys.append(key)


class WaitStub:
    def __init__(self): self.values = []
    def wait(self, seconds): self.values.append(seconds)


def test_action_engine_delegates_actions():
    mouse, keyboard, waiter = MouseStub(), KeyboardStub(), WaitStub()
    engine = ActionEngine(mouse=mouse, keyboard=keyboard, waiter=waiter)

    assert engine.click(10, 20) == (10, 20)
    assert engine.double_click(30, 40) == (30, 40)
    engine.press_key("1")
    assert engine.wait(0.15) == 0.15

    assert mouse.calls == [("click", 10, 20), ("double", 30, 40)]
    assert keyboard.keys == ["1"]
    assert waiter.values == [0.15]


def test_action_engine_supports_bounded_jitter():
    mouse, keyboard, waiter = MouseStub(), KeyboardStub(), WaitStub()
    engine = ActionEngine(
        mouse=mouse,
        keyboard=keyboard,
        waiter=waiter,
        config=ActionEngineConfig(click_jitter_pixels=3, delay_jitter_seconds=0.02),
        random_source=Random(42),
    )
    x, y = engine.click(100, 100)
    duration = engine.wait(0.10)
    assert 97 <= x <= 103 and 97 <= y <= 103
    assert 0.08 <= duration <= 0.12


def test_action_engine_rejects_blank_key():
    engine = ActionEngine(mouse=MouseStub(), keyboard=KeyboardStub(), waiter=WaitStub())
    with pytest.raises(ValueError):
        engine.press_key("  ")
