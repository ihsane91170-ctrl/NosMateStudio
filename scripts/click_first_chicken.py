from __future__ import annotations

import time
from pathlib import Path

import pyautogui
from PIL import ImageDraw

from app.vision.coordinates import CaptureCoordinateMapper
from app.vision.screenshot_provider import (
    PillowScreenshotBackend,
    WindowScreenshotProvider,
)
from app.vision.template_matcher import TemplateMatcher
from app.vision.template_repository import TemplateRepository
from app.vision.window_detector import WindowDetector

TEMPLATE_NAME = "pet_chicken_row"
THRESHOLD = 0.60
MINIMUM_DISTANCE = 10


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    template_directory = project_root / "assets" / "templates"
    capture_directory = project_root / "captures"
    capture_directory.mkdir(parents=True, exist_ok=True)

    window_detector = WindowDetector("NosTale")
    game_window = window_detector.detect()

    if game_window is None:
        raise RuntimeError("Fenêtre NosTale introuvable.")

    print(
        "Dans les 3 secondes : clique sur NosTale "
        "et laisse la liste des familiers visible."
    )
    time.sleep(3)

    # On redétecte la fenêtre après la mise au premier plan,
    # au cas où sa position aurait changé.
    game_window = window_detector.detect()

    if game_window is None:
        raise RuntimeError("Fenêtre NosTale introuvable après le délai.")

    screenshot_provider = WindowScreenshotProvider(
        PillowScreenshotBackend()
    )
    screenshot = screenshot_provider.capture(game_window)

    capture_path = (
        capture_directory / "click_test_capture.png"
    )
    screenshot.save(capture_path)
    print(f"Capture analysée : {capture_path}")

    matcher = TemplateMatcher(
        TemplateRepository(template_directory)
    )
    chickens = matcher.find_all(
        screenshot,
        TEMPLATE_NAME,
        threshold=THRESHOLD,
        minimum_distance=MINIMUM_DISTANCE,
    )

    if not chickens:
        screenshot.save(
            capture_directory / "click_test_no_detection.png"
        )
        raise RuntimeError("Aucune poule détectée.")

    chicken = chickens[0]

    # Point situé dans la partie gauche du template, sur l’icône.
    relative_click = (
        chicken.left + min(18, chicken.width // 4),
        chicken.top + chicken.height // 2,
    )

    mapper = CaptureCoordinateMapper(
        window=game_window,
        capture_width=screenshot.width,
        capture_height=screenshot.height,
    )
    screen_click = mapper.to_screen(relative_click)

    annotated = screenshot.convert("RGB").copy()
    draw = ImageDraw.Draw(annotated)

    draw.rectangle(
        (
            chicken.left,
            chicken.top,
            chicken.right,
            chicken.bottom,
        ),
        outline="red",
        width=3,
    )

    click_x, click_y = relative_click
    draw.ellipse(
        (
            click_x - 6,
            click_y - 6,
            click_x + 6,
            click_y + 6,
        ),
        fill="lime",
    )

    debug_path = capture_directory / "click_first_chicken.png"
    annotated.save(debug_path)

    print(
        f"Détection : left={chicken.left}, top={chicken.top}, "
        f"width={chicken.width}, height={chicken.height}"
    )
    print(f"Clic relatif : {relative_click}")
    print(f"Clic écran : {screen_click}")
    print(f"Capture debug : {debug_path}")

    print("Clic dans 3 secondes...")
    time.sleep(3)

    window_detector.activate()
    time.sleep(0.5)

    pyautogui.moveTo(*screen_click, duration=0.5)
    pyautogui.click()

    time.sleep(1)

    game_window = window_detector.detect()

    if game_window is None:
        raise RuntimeError(
            "Fenêtre NosTale introuvable après le clic."
        )

    after_click = screenshot_provider.capture(game_window)
 
    after_click_path = (
        capture_directory / "click_test_after_click.png"
    )
    after_click.save(after_click_path)

    print(f"Clic effectué à l’écran : {screen_click}")
    print(f"Capture après clic : {after_click_path}")


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    main()