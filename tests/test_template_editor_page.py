from PIL import Image

from app.ui.pages.template_editor_page import TemplateEditorPage
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
        self.received_window: GameWindow | None = None

    def capture(self, window: GameWindow) -> Image.Image:
        self.received_window = window
        return self.image


def usable_window() -> GameWindow:
    return GameWindow(
        title="NosTale",
        left=100,
        top=200,
        width=1280,
        height=720,
    )


def test_template_editor_captures_window(qtbot, tmp_path) -> None:
    window = usable_window()
    image = Image.new("RGB", (1280, 720))
    provider = ScreenshotProviderStub(image)

    page = TemplateEditorPage(
        window_detector=WindowDetectorStub(window),
        screenshot_provider=provider,
        template_repository=TemplateRepository(
            tmp_path / "templates"
        ),
    )
    qtbot.addWidget(page)

    page.capture_button.click()

    assert provider.received_window is window
    assert page.image_widget.width() == 1280
    assert page.image_widget.height() == 720
    assert (
        page.status_label.text()
        == "Capture chargée : 1280 × 720 pixels."
    )


def test_template_editor_reports_missing_window(
    qtbot,
    tmp_path,
) -> None:
    provider = ScreenshotProviderStub(
        Image.new("RGB", (1280, 720))
    )

    page = TemplateEditorPage(
        window_detector=WindowDetectorStub(None),
        screenshot_provider=provider,
        template_repository=TemplateRepository(
            tmp_path / "templates"
        ),
    )
    qtbot.addWidget(page)

    page.capture_button.click()

    assert (
        page.status_label.text()
        == "Erreur : fenêtre NosTale introuvable."
    )
    assert provider.received_window is None


def test_template_editor_saves_selected_template(
    qtbot,
    tmp_path,
) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    image = Image.new("RGB", (200, 100))

    page = TemplateEditorPage(
        window_detector=WindowDetectorStub(usable_window()),
        screenshot_provider=ScreenshotProviderStub(image),
        template_repository=repository,
    )
    qtbot.addWidget(page)

    page.capture_button.click()

    page.image_widget._selection = (
        __import__(
            "app.ui.widgets",
            fromlist=["ImageSelection"],
        ).ImageSelection(
            x=10,
            y=20,
            width=60,
            height=40,
        )
    )

    page.template_name_input.setText(
        "Bouton Accompagner"
    )
    page._save_template()

    saved = repository.load_image(
        "bouton_accompagner"
    )

    assert saved.size == (60, 40)
    assert page.template_name_input.text() == ""
    assert page.image_widget.selection is None
    assert "Template enregistré" in page.status_label.text()