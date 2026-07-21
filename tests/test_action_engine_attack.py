from app.automation.action_engine import ActionEngine


class MouseSpy:
    def __init__(self): self.calls=[]
    def click(self,x,y): self.calls.append(("click",x,y))
    def double_click(self,x,y): self.calls.append(("double_click",x,y))


class KeyboardSpy:
    def __init__(self): self.keys=[]
    def press(self,key): self.keys.append(key)


def test_capture_key_is_forbidden():
    engine=ActionEngine(MouseSpy(), KeyboardSpy(), sleep_fn=lambda _: None)
    for key in ("&", "1", "ampersand"):
        try:
            engine.press(key)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{key} aurait dû être refusée")
