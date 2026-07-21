from PIL import Image

from app.ui.pages.vision_debug_page import VisionDebugPage
from app.vision.match import TemplateMatch
from app.vision.template_repository import TemplateRepository
from app.vision.window_detector import GameWindow


class WindowDetectorStub:
    def __init__(self, window: GameWindow | None) -> None:
        self.window = window

    def detect(self) -> GameWindow | None:
        return self.window


class ScreenshotProviderStub:
    def __init__(self, image: Image.Image) -> None:
        self.image = image

    def capture(self, window: GameWindow) -> Image.Image:
        return self.image


class MatcherStub:
    def __init__(
        self,
        matches: tuple[TemplateMatch, ...],
    ) -> None:
        self.matches = matches
        self.calls: list[tuple[str, float | None, int]] = []

    def find_all(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
        minimum_distance: int = 10,
    ) -> tuple[TemplateMatch, ...]:
        self.calls.append(
            (
                template_name,
                threshold,
                minimum_distance,
            )
        )
        return self.matches


def usable_window() -> GameWindow:
    return GameWindow(
        title="NosTale",
        left=100,
        top=200,
        width=1280,
        height=720,
    )


def test_debug_page_lists_templates(qtbot, tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save(
        "pet_row",
        Image.new("RGB", (30, 20)),
    )

    page = VisionDebugPage(
        window_detector=WindowDetectorStub(usable_window()),
        screenshot_provider=ScreenshotProviderStub(
            Image.new("RGB", (1280, 720))
        ),
        template_repository=repository,
        matcher=MatcherStub(()),
    )
    qtbot.addWidget(page)

    assert page.template_selector.count() == 1
    assert page.template_selector.currentText() == "pet_row"
    assert page.detect_button.isEnabled() is True


def test_debug_page_displays_matches(qtbot, tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save(
        "pet_row",
        Image.new("RGB", (30, 20)),
    )

    matcher = MatcherStub(
        (
            TemplateMatch(
                template_name="pet_row",
                confidence=0.96,
                left=30,
                top=20,
                width=30,
                height=20,
            ),
            TemplateMatch(
                template_name="pet_row",
                confidence=0.91,
                left=120,
                top=80,
                width=30,
                height=20,
            ),
        )
    )

    page = VisionDebugPage(
        window_detector=WindowDetectorStub(usable_window()),
        screenshot_provider=ScreenshotProviderStub(
            Image.new("RGB", (1280, 720))
        ),
        template_repository=repository,
        matcher=matcher,
    )
    qtbot.addWidget(page)

    page.threshold_input.setValue(0.82)
    page.minimum_distance_input.setValue(25)
    page.detect_button.click()

    assert page.results_list.count() == 2
    assert (
        page.status_label.text()
        == "2 détection(s) pour « pet_row »."
    )
    assert matcher.calls == [
        (
            "pet_row",
            0.82,
            25,
        )
    ]
    assert page.image_widget.width() == 1280
    assert page.image_widget.height() == 720


def test_debug_page_reports_missing_window(
    qtbot,
    tmp_path,
) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save(
        "pet_row",
        Image.new("RGB", (30, 20)),
    )

    page = VisionDebugPage(
        window_detector=WindowDetectorStub(None),
        screenshot_provider=ScreenshotProviderStub(
            Image.new("RGB", (1280, 720))
        ),
        template_repository=repository,
        matcher=MatcherStub(()),
    )
    qtbot.addWidget(page)

    page.detect_button.click()

    assert (
        page.status_label.text()
        == "Erreur : fenêtre NosTale introuvable."
    )

def test_debug_page_scans_visible_pets(
    qtbot,
    tmp_path,
) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save(
        "pet_row",
        Image.new("RGB", (30, 20)),
    )

    matcher = MatcherStub(
        (
            TemplateMatch(
                template_name="pet_row",
                confidence=0.97,
                left=100,
                top=160,
                width=80,
                height=30,
            ),
            TemplateMatch(
                template_name="pet_row",
                confidence=0.95,
                left=100,
                top=80,
                width=80,
                height=30,
            ),
        )
    )

    page = VisionDebugPage(
        window_detector=WindowDetectorStub(usable_window()),
        screenshot_provider=ScreenshotProviderStub(
            Image.new("RGB", (1280, 720))
        ),
        template_repository=repository,
        matcher=matcher,
    )
    qtbot.addWidget(page)

    page.threshold_input.setValue(0.82)
    page.minimum_distance_input.setValue(40)

    page.scan_pets_button.click()

    assert page.results_list.count() == 2

    assert (
        "Familier #01"
        in page.results_list.item(0).text()
    )
    assert "y=80" in page.results_list.item(0).text()

    assert (
        "Familier #02"
        in page.results_list.item(1).text()
    )
    assert "y=160" in page.results_list.item(1).text()

    assert (
        page.status_label.text()
        == "2 familier(s) visible(s) détecté(s)."
    )

def test_chicken_detection_without_negative_template_disables_selection(qtbot, tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save("chicken", Image.new("RGB", (30, 20)))
    matches = (
        TemplateMatch("chicken", 0.95, 100, 100, 30, 20),
    )
    page = VisionDebugPage(
        window_detector=WindowDetectorStub(usable_window()),
        screenshot_provider=ScreenshotProviderStub(Image.new("RGB", (1280, 720))),
        template_repository=repository,
        matcher=MatcherStub(matches),
    )
    qtbot.addWidget(page)

    page.detect_chickens_button.click()

    assert page.select_chicken_button.isEnabled() is False
    assert "mode diagnostic uniquement" in page.status_label.text()
    assert "REFUSÉE" in page.results_list.item(0).text()


def test_export_chicken_diagnostic_creates_files(qtbot, tmp_path, monkeypatch) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save("chicken", Image.new("RGB", (30, 20)))
    repository.save("not_chicken", Image.new("RGB", (30, 20)))
    matches = (TemplateMatch("chicken", 0.91, 100, 100, 30, 20),)
    page = VisionDebugPage(
        window_detector=WindowDetectorStub(usable_window()),
        screenshot_provider=ScreenshotProviderStub(Image.new("RGB", (1280, 720))),
        template_repository=repository,
        matcher=MatcherStub(matches),
    )
    qtbot.addWidget(page)
    monkeypatch.setattr(page, "PROJECT_ROOT", tmp_path)
    page.detect_chickens_button.click()
    page.export_diagnostic_button.click()
    exports = list((tmp_path / "vision_logs").glob("chicken_*"))
    assert len(exports) == 1
    assert (exports[0] / "capture_originale.png").exists()
    assert (exports[0] / "capture_annotee.png").exists()
    assert (exports[0] / "diagnostic.json").exists()
