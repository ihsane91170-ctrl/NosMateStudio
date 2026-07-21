from __future__ import annotations

from app.production.capture_pilot import CapturePilot
from app.runtime import RuntimeFactory, RuntimeMode
from app.vision.screenshot_provider import PillowScreenshotBackend, WindowScreenshotProvider
from app.vision.window_detector import WindowDetector


def build_real_capture_pilot(window_detector: WindowDetector) -> CapturePilot:
    runtime = RuntimeFactory.create(RuntimeMode.REAL)
    return CapturePilot(
        keyboard=runtime.keyboard,
        waiter=runtime.wait,
        screenshots=WindowScreenshotProvider(PillowScreenshotBackend()),
        activator=window_detector,
    )
