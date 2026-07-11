from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WorkflowPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        title = QLabel("Workflow")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Le Workflow Engine est installé. "
            "Son intégration à l'interface sera réalisée après la stabilisation."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch(1)