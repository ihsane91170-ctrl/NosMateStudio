from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from app.services.game_diagnostic_service import (
    GameDiagnosticResult,
    GameDiagnosticService,
)


class DiagnosticController(QObject):
    diagnostic_updated = Signal(object)
    diagnostic_checked = Signal(object)

    def __init__(
        self,
        service: GameDiagnosticService,
        interval_ms: int = 1500,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._last_result: GameDiagnosticResult | None = None

        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.refresh)

    def start(self) -> None:
        self.refresh()
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    @Slot()
    def refresh(self) -> None:
        result = self._service.run()
        self.diagnostic_checked.emit(result)

        if result != self._last_result:
            self._last_result = result
            self.diagnostic_updated.emit(result)