from threading import Event


class StopToken:
    def __init__(self) -> None:
        self._event = Event()

    @property
    def is_requested(self) -> bool:
        return self._event.is_set()

    def request(self) -> None:
        self._event.set()

    def reset(self) -> None:
        self._event.clear()