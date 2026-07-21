from __future__ import annotations

from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from app.capture.controller import (
    CaptureBatchConfig,
    CaptureBatchController,
    CaptureBatchProgress,
    CaptureBatchResult,
)


class CaptureBatchWorker(QObject):
    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, capture_service, return_service, target_count: int) -> None:
        super().__init__()
        self._stop_event = Event()
        self._capture_service = capture_service
        self._return_service = return_service
        self._target_count = target_count

    @Slot()
    def run(self) -> None:
        try:
            controller = CaptureBatchController(
                self._capture_service,
                self._return_service,
                stop_requested=self._stop_event.is_set,
                on_progress=self._emit_progress,
            )
            result = controller.run(CaptureBatchConfig(target_count=self._target_count))
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            return
        self.finished.emit(result)

    def request_stop(self) -> None:
        self._stop_event.set()

    def _emit_progress(self, progress: CaptureBatchProgress) -> None:
        self.progress.emit(progress)
