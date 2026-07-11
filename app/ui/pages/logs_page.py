from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LogsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        title = QLabel("Logs")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Le journal détaillé sera intégré dans une prochaine évolution."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch(1)