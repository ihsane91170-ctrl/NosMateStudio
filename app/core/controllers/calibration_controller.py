from __future__ import annotations

from collections.abc import Callable

import pyautogui
from PySide6.QtCore import QObject, QTimer, Signal, Slot

from app.calibration.models import CalibrationTarget
from app.calibration.service import CalibrationError, CalibrationService
from app.vision.window_detector import WindowDetector


class CalibrationController(QObject):
    profile_loaded = Signal(object)
    countdown_changed = Signal(int)
    capture_succeeded = Signal(object)
    capture_failed = Signal(str)
    reset_succeeded = Signal(object)

    def __init__(
        self,
        service: CalibrationService,
        window_detector: WindowDetector,
        position_provider: Callable[[], tuple[int, int]] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._window_detector = window_detector
        self._position_provider = position_provider or self._mouse_position
        self._pending_target: CalibrationTarget | None = None
        self._remaining = 0

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    @Slot()
    def load(self) -> None:
        self.profile_loaded.emit(self._service.current())

    @Slot(str)
    def start_capture(self, target_value: str) -> None:
        if self._timer.isActive():
            return
        self._pending_target = CalibrationTarget(target_value)
        self._remaining = 3
        self.countdown_changed.emit(self._remaining)
        self._timer.start()

    @Slot()
    def reset(self) -> None:
        self._timer.stop()
        self._pending_target = None
        self.reset_succeeded.emit(self._service.reset())

    def _tick(self) -> None:
        self._remaining -= 1

        if self._remaining > 0:
            self.countdown_changed.emit(self._remaining)
            return

        self._timer.stop()
        self._capture_now()

    def _capture_now(self) -> None:
        target = self._pending_target
        self._pending_target = None

        if target is None:
            self.capture_failed.emit("Aucune cible de calibration sélectionnée.")
            return

        try:
            window = self._window_detector.detect()
            if window is None:
                raise CalibrationError("Le client NosTale est introuvable.")

            x, y = self._position_provider()
            capture = self._service.capture(target, x, y, window)
            self.capture_succeeded.emit(capture)
        except Exception as exc:
            self.capture_failed.emit(str(exc))

    @staticmethod
    def _mouse_position() -> tuple[int, int]:
        position = pyautogui.position()
        return int(position.x), int(position.y)
