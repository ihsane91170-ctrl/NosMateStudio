from __future__ import annotations

from dataclasses import dataclass

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import (
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True, slots=True)
class ImageSelection:
    x: int
    y: int
    width: int
    height: int

    @property
    def is_valid(self) -> bool:
        return self.width > 0 and self.height > 0

    def to_box(self) -> tuple[int, int, int, int]:
        return (
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height,
        )


class ImageSelectionWidget(QWidget):
    selection_changed = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._image: Image.Image | None = None
        self._pixmap = QPixmap()

        self._selection: ImageSelection | None = None
        self._drag_start: QPoint | None = None
        self._drag_current: QPoint | None = None

        self.setMouseTracking(True)
        self.setMinimumSize(320, 240)

    @property
    def selection(self) -> ImageSelection | None:
        return self._selection

    def set_image(self, image: Image.Image) -> None:
        self._image = image.convert("RGB")
        self._pixmap = QPixmap.fromImage(ImageQt(self._image))

        self._selection = None
        self._drag_start = None
        self._drag_current = None

        self.setFixedSize(self._pixmap.size())
        self.update()

    def clear_selection(self) -> None:
        self._selection = None
        self._drag_start = None
        self._drag_current = None

        self.selection_changed.emit(None)
        self.update()

    def selected_image(self) -> Image.Image:
        if self._image is None:
            raise RuntimeError("Aucune image n'est chargée.")

        if self._selection is None or not self._selection.is_valid:
            raise RuntimeError("Aucune zone valide n'est sélectionnée.")

        return self._image.crop(self._selection.to_box())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (
            event.button() is Qt.MouseButton.LeftButton
            and not self._pixmap.isNull()
        ):
            point = event.position().toPoint()

            self._drag_start = self._clamp_point(point)
            self._drag_current = self._drag_start
            self._selection = None

            self.update()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_start is not None:
            self._drag_current = self._clamp_point(
                event.position().toPoint()
            )
            self.update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (
            event.button() is Qt.MouseButton.LeftButton
            and self._drag_start is not None
        ):
            self._drag_current = self._clamp_point(
                event.position().toPoint()
            )

            start_x = self._drag_start.x()
            start_y = self._drag_start.y()
            end_x = self._drag_current.x()
            end_y = self._drag_current.y()

            left = min(start_x, end_x)
            top = min(start_y, end_y)
            width = abs(end_x - start_x)
            height = abs(end_y - start_y)

            self._selection = ImageSelection(
                x=left,
                y=top,
                width=width,
                height=height,
            )

            self._drag_start = None
            self._drag_current = None

            self.selection_changed.emit(self._selection)
            self.update()

        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        if not self._pixmap.isNull():
            painter.drawPixmap(0, 0, self._pixmap)

        rectangle = self._current_rectangle()

        if rectangle is not None:
            pen = QPen()
            pen.setWidth(2)
            pen.setStyle(Qt.PenStyle.SolidLine)

            painter.setPen(pen)
            painter.drawRect(rectangle)

        painter.end()
        super().paintEvent(event)

    def _current_rectangle(self) -> QRect | None:
        if (
            self._drag_start is not None
            and self._drag_current is not None
        ):
            return QRect(
                self._drag_start,
                self._drag_current,
            ).normalized()

        if self._selection is None:
            return None

        return QRect(
            self._selection.x,
            self._selection.y,
            self._selection.width,
            self._selection.height,
        )

    def _clamp_point(self, point: QPoint) -> QPoint:
        if self._pixmap.isNull():
            return QPoint()

        x = min(
            max(point.x(), 0),
            self._pixmap.width() - 1,
        )
        y = min(
            max(point.y(), 0),
            self._pixmap.height() - 1,
        )

        return QPoint(x, y)