import pytest
from PIL import Image

pytest.importorskip("PySide6")
pytest.importorskip("pygetwindow")

from app.ui.pages.vision_debug_page import VisionDebugPage
from app.vision.ai_detector import ObjectDetection
from app.vision.window_detector import GameWindow


class WindowDetectorStub:
    def detect(self):
        return GameWindow("NosTale", 100, 200, 800, 600)


class ScreenshotProviderStub:
    def capture(self, window):
        return Image.new("RGB", (window.width, window.height))


class AIDetectorStub:
    def __init__(self):
        self.calls = 0

    def detect(self, image, *, confidence=0.50):
        self.calls += 1
        return (
            ObjectDetection("not_chicken", 0.99, 380, 280, 420, 320),
            ObjectDetection("chicken", 0.95, 190, 270, 230, 310),
            ObjectDetection("chicken", 0.90, 380, 280, 420, 320),
        )


class MouseStub:
    def __init__(self):
        self.clicks = []

    def click(self, x, y):
        self.clicks.append((x, y))


def test_ai_detection_enables_and_clicks_best_chicken(qtbot, tmp_path):
    mouse = MouseStub()
    detector = AIDetectorStub()
    page = VisionDebugPage(
        window_detector=WindowDetectorStub(),
        screenshot_provider=ScreenshotProviderStub(),
        mouse_executor=mouse,
        ai_detector=detector,
    )
    qtbot.addWidget(page)
    page.threshold_input.setValue(0.25)

    page.detect_ai_button.click()

    assert page.select_chicken_button.isEnabled()
    assert "Meilleure cible" in page.status_label.text()
    assert any("MEILLEURE CIBLE" in page.results_list.item(i).text() for i in range(page.results_list.count()))

    page.arm_real_click.setChecked(True)
    page.select_chicken_button.click()

    # Le candidat centré est choisi malgré le not_chicken très confiant.
    assert mouse.clicks == [(500, 500)]
    assert detector.calls == 2  # détection + revalidation juste avant le clic
    assert "Clic IA envoyé" in page.status_label.text()
