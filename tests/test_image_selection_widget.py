from PIL import Image
from PySide6.QtCore import QPoint, Qt

from app.ui.widgets import (
    ImageSelection,
    ImageSelectionWidget,
)


def test_selection_box_conversion() -> None:
    selection = ImageSelection(
        x=10,
        y=20,
        width=30,
        height=40,
    )

    assert selection.is_valid is True
    assert selection.to_box() == (
        10,
        20,
        40,
        60,
    )


def test_widget_crops_selected_image(qtbot) -> None:
    widget = ImageSelectionWidget()
    qtbot.addWidget(widget)

    widget.set_image(
        Image.new(
            "RGB",
            (200, 100),
        )
    )

    qtbot.mousePress(
        widget,
        Qt.MouseButton.LeftButton,
        pos=QPoint(10, 20),
    )
    qtbot.mouseMove(
        widget,
        QPoint(70, 60),
    )
    qtbot.mouseRelease(
        widget,
        Qt.MouseButton.LeftButton,
        pos=QPoint(70, 60),
    )

    cropped = widget.selected_image()

    assert widget.selection is not None
    assert cropped.size == (60, 40)


def test_clear_selection_removes_current_selection(qtbot) -> None:
    widget = ImageSelectionWidget()
    qtbot.addWidget(widget)

    widget.set_image(
        Image.new(
            "RGB",
            (200, 100),
        )
    )

    qtbot.mousePress(
        widget,
        Qt.MouseButton.LeftButton,
        pos=QPoint(10, 10),
    )
    qtbot.mouseRelease(
        widget,
        Qt.MouseButton.LeftButton,
        pos=QPoint(40, 40),
    )

    assert widget.selection is not None

    widget.clear_selection()

    assert widget.selection is None