from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.vision.detection_dataset import BoundingBox, DetectionDataset


class Canvas(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setMouseTracking(True)
        self.image: Image.Image | None = None
        self.boxes: list[BoundingBox] = []
        self.class_name = "chicken"
        self._start: QPoint | None = None
        self._current: QPoint | None = None

    def load_image(self, path: Path) -> None:
        self.image = Image.open(path).convert("RGB")
        self.boxes.clear()
        self._refresh()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if self.image is not None and event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._current = self._start

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._start is not None:
            self._current = event.position().toPoint()
            self._refresh()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self.image is None or self._start is None:
            return
        end = event.position().toPoint()
        left, right = sorted((self._start.x(), end.x()))
        top, bottom = sorted((self._start.y(), end.y()))
        left = max(0, min(left, self.image.width - 1))
        right = max(0, min(right, self.image.width))
        top = max(0, min(top, self.image.height - 1))
        bottom = max(0, min(bottom, self.image.height))
        if right - left >= 4 and bottom - top >= 4:
            self.boxes.append(BoundingBox(self.class_name, left, top, right, bottom))
        self._start = None
        self._current = None
        self._refresh()

    def undo(self) -> None:
        if self.boxes:
            self.boxes.pop()
            self._refresh()

    def _refresh(self) -> None:
        if self.image is None:
            return
        pixmap = QPixmap.fromImage(ImageQt(self.image))
        painter = QPainter(pixmap)
        for box in self.boxes:
            color = QColor("green") if box.class_name == "chicken" else QColor("red")
            painter.setPen(QPen(color, 2))
            painter.drawRect(QRect(box.left, box.top, box.right - box.left, box.bottom - box.top))
            painter.drawText(box.left, max(12, box.top - 3), box.class_name)
        if self._start is not None and self._current is not None:
            painter.setPen(QPen(QColor("yellow"), 2, Qt.PenStyle.DashLine))
            painter.drawRect(QRect(self._start, self._current).normalized())
        painter.end()
        self.setPixmap(pixmap)
        self.resize(pixmap.size())


class Annotator(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NosMate Studio — Annotation poules")
        self.canvas = Canvas()
        self.source: Path | None = None
        self.dataset = DetectionDataset(Path("vision_dataset"))

        open_button = QPushButton("Ouvrir une capture")
        open_button.clicked.connect(self.open_image)
        chicken_button = QPushButton("Classe : poule")
        chicken_button.clicked.connect(lambda: self.set_class("chicken"))
        other_button = QPushButton("Classe : autre monstre")
        other_button.clicked.connect(lambda: self.set_class("not_chicken"))
        undo_button = QPushButton("Annuler la dernière boîte")
        undo_button.clicked.connect(self.canvas.undo)
        save_button = QPushButton("Enregistrer dans le dataset")
        save_button.clicked.connect(self.save)
        self.status = QLabel("Ouvre capture_originale.png, puis dessine un rectangle par monstre.")

        toolbar = QHBoxLayout()
        for widget in (open_button, chicken_button, other_button, undo_button, save_button):
            toolbar.addWidget(widget)
        toolbar.addStretch(1)
        layout = QVBoxLayout()
        layout.addLayout(toolbar)
        layout.addWidget(self.status)
        layout.addWidget(self.canvas)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.resize(1200, 800)

    def set_class(self, class_name: str) -> None:
        self.canvas.class_name = class_name
        self.status.setText(f"Classe active : {class_name}")

    def open_image(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Capture", "vision_logs", "Images (*.png *.jpg)")
        if filename:
            self.source = Path(filename)
            self.canvas.load_image(self.source)
            self.status.setText(f"Capture chargée : {self.source.name}")

    def save(self) -> None:
        if self.source is None:
            QMessageBox.warning(self, "NosMate", "Aucune capture chargée.")
            return
        image_path, label_path = self.dataset.add(self.source, self.canvas.boxes)
        self.status.setText(
            f"Enregistré : {image_path.name} — {len(self.canvas.boxes)} annotation(s)."
        )
        QMessageBox.information(self, "NosMate", f"Dataset mis à jour.\n{label_path}")


def main() -> int:
    app = QApplication(sys.argv)
    window = Annotator()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
