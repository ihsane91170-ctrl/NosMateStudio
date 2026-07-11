from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.configuration.models import Environment, Hotkeys, Settings
from app.configuration.validators import ValidationIssue
from app.core.controllers.settings_controller import SettingsController


class SettingsPage(QWidget):
    ACTION_ROWS = (
        ("Accès à la zone des familiers", "pet_storage"),
        ("Capturer un nouveau familier", "capture_new_pet"),
        ("Accès à la zone d'XP", "xp_map"),
        ("Invocation du Protomonstre faible", "summon_weak"),
        ("Invocation du Protomonstre", "summon_normal"),
        ("Invocation du Protomonstre fort", "summon_strong"),
    )

    def __init__(
        self,
        controller: SettingsController,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._current_settings: Settings | None = None
        self._selectors: dict[str, QLineEdit] = {}

        title = QLabel("Paramètres")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Configurez les raccourcis utilisés par les automatisations."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        card = QFrame()
        card.setObjectName("Card")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        section_title = QLabel("Raccourcis du workflow")
        section_title.setStyleSheet(
            "font-size: 16px; font-weight: 700;"
        )

        info = QLabel(
            "Chaque action possède un raccourci configurable. "
            "Une même touche ne peut pas être utilisée deux fois."
        )
        info.setObjectName("Muted")
        info.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(24)
        form.setVerticalSpacing(12)

        for label_text, field_name in self.ACTION_ROWS:
            selector = QLineEdit()
            selector.setMaximumWidth(160)
            selector.setPlaceholderText("Ex. Q, _, F1, space")

            self._selectors[field_name] = selector
            form.addRow(label_text, selector)

        self.environment_value = QLabel("—")
        self.environment_value.setObjectName("Muted")
        form.addRow("Environnement", self.environment_value)

        self.profile_value = QLabel("—")
        self.profile_value.setObjectName("Muted")
        form.addRow("Profil", self.profile_value)

        buttons = QHBoxLayout()
        buttons.addStretch(1)

        self.reset_button = QPushButton(
            "Restaurer les valeurs par défaut"
        )

        self.save_button = QPushButton("Enregistrer")
        self.save_button.setObjectName("PrimaryButton")

        buttons.addWidget(self.reset_button)
        buttons.addWidget(self.save_button)

        card_layout.addWidget(section_title)
        card_layout.addWidget(info)
        card_layout.addLayout(form)
        card_layout.addLayout(buttons)

        self.feedback = QLabel("")
        self.feedback.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.feedback.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(card)
        layout.addWidget(self.feedback)
        layout.addStretch(1)

        self.save_button.clicked.connect(self._save)
        self.reset_button.clicked.connect(self._confirm_reset)

        controller.settings_loaded.connect(self._apply_settings)
        controller.settings_saved.connect(self._on_saved)
        controller.settings_reset.connect(self._on_reset)
        controller.validation_failed.connect(
            self._show_validation_errors
        )
        controller.unexpected_error.connect(
            self._show_unexpected_error
        )

        controller.load()

    def _build_settings_from_form(self) -> Settings:
        if self._current_settings is None:
            raise RuntimeError(
                "Les paramètres ne sont pas encore chargés."
            )

        return Settings(
            profile=self._current_settings.profile,
            environment=self._current_settings.environment,
            hotkeys=Hotkeys(
                pet_storage=self._selectors["pet_storage"].text(),
                capture_new_pet=self._selectors[
                    "capture_new_pet"
                ].text(),
                xp_map=self._selectors["xp_map"].text(),
                summon_weak=self._selectors["summon_weak"].text(),
                summon_normal=self._selectors[
                    "summon_normal"
                ].text(),
                summon_strong=self._selectors[
                    "summon_strong"
                ].text(),
            ),
        )

    def _save(self) -> None:
        settings = self._build_settings_from_form()
        self._controller.save(settings)

    def _confirm_reset(self) -> None:
        answer = QMessageBox.question(
            self,
            "Restaurer les valeurs par défaut",
            "Voulez-vous restaurer tous les raccourcis par défaut ?",
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if answer is QMessageBox.StandardButton.Yes:
            self._controller.reset()

    def _apply_settings(self, settings: Settings) -> None:
        self._current_settings = settings

        for _, field_name in self.ACTION_ROWS:
            value = getattr(settings.hotkeys, field_name)
            self._selectors[field_name].setText(value)

        self.environment_value.setText(
            self._environment_label(settings.environment)
        )
        self.profile_value.setText(settings.profile)
        self.feedback.setText("Paramètres chargés.")

    def _on_saved(self, settings: Settings) -> None:
        self._apply_settings(settings)
        self.feedback.setText(
            "Paramètres enregistrés avec succès."
        )

    def _on_reset(self, settings: Settings) -> None:
        self._apply_settings(settings)
        self.feedback.setText(
            "Valeurs par défaut restaurées."
        )

    def _show_validation_errors(
        self,
        issues: Iterable[ValidationIssue],
    ) -> None:
        messages = "\n".join(
            f"• {issue.message}" for issue in issues
        )

        self.feedback.setText(messages)

        QMessageBox.warning(
            self,
            "Configuration invalide",
            messages,
        )

    def _show_unexpected_error(self, message: str) -> None:
        self.feedback.setText(message)

        QMessageBox.critical(
            self,
            "Erreur",
            message,
        )

    @staticmethod
    def _environment_label(
        environment: Environment,
    ) -> str:
        labels = {
            Environment.DEVELOPMENT: "Développement",
            Environment.RECETTE: "Recette",
            Environment.PRODUCTION: "Production",
        }

        return labels[environment]