from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.configuration.defaults import ALLOWED_KEYS
from app.configuration.models import Environment, Hotkeys, Settings
from app.configuration.validators import ValidationIssue
from app.core.controllers.settings_controller import SettingsController


class SettingsPage(QWidget):
    ACTION_ROWS = (
        ("Accès au stockage des familiers", "pet_storage"),
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
        self._selectors: dict[str, QComboBox] = {}

        title = QLabel("Paramètres")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Configurez les touches utilisées par les futures automatisations."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        section_title = QLabel("Raccourcis du workflow")
        section_title.setStyleSheet("font-size: 16px; font-weight: 700;")

        info = QLabel(
            "Touches autorisées : 1, 2, 3, 4, 5, Q, W, E, R et T. "
            "Une même touche ne peut pas être utilisée deux fois."
        )
        info.setObjectName("Muted")
        info.setWordWrap(True)

        form = QFormLayout()
        form.setHorizontalSpacing(24)
        form.setVerticalSpacing(12)

        ordered_keys = ["1", "2", "3", "4", "5", "Q", "W", "E", "R", "T"]
        assert set(ordered_keys) == set(ALLOWED_KEYS)

        for label_text, field_name in self.ACTION_ROWS:
            selector = QComboBox()
            selector.addItems(ordered_keys)
            selector.setMinimumWidth(130)
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

        self.reset_button = QPushButton("Restaurer les valeurs par défaut")
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
        controller.validation_failed.connect(self._show_validation_errors)
        controller.unexpected_error.connect(self._show_unexpected_error)

        controller.load()

    def _build_settings_from_form(self) -> Settings:
        if self._current_settings is None:
            raise RuntimeError("Les paramètres ne sont pas encore chargés.")

        return Settings(
            profile=self._current_settings.profile,
            environment=self._current_settings.environment,
            hotkeys=Hotkeys(
                pet_storage=self._selectors["pet_storage"].currentText(),
                xp_map=self._selectors["xp_map"].currentText(),
                summon_weak=self._selectors["summon_weak"].currentText(),
                summon_normal=self._selectors["summon_normal"].currentText(),
                summon_strong=self._selectors["summon_strong"].currentText(),
            ),
        )

    def _save(self) -> None:
        self._controller.save(self._build_settings_from_form())

    def _confirm_reset(self) -> None:
        answer = QMessageBox.question(
            self,
            "Restaurer les valeurs par défaut",
            "Voulez-vous restaurer tous les raccourcis par défaut ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer is QMessageBox.StandardButton.Yes:
            self._controller.reset()

    def _apply_settings(self, settings: Settings) -> None:
        self._current_settings = settings

        for _, field_name in self.ACTION_ROWS:
            selector = self._selectors[field_name]
            value = getattr(settings.hotkeys, field_name)
            selector.setCurrentText(value)

        self.environment_value.setText(self._environment_label(settings.environment))
        self.profile_value.setText(settings.profile)
        self.feedback.setText("Paramètres chargés.")

    def _on_saved(self, settings: Settings) -> None:
        self._apply_settings(settings)
        self.feedback.setText("Paramètres enregistrés avec succès.")

    def _on_reset(self, settings: Settings) -> None:
        self._apply_settings(settings)
        self.feedback.setText("Valeurs par défaut restaurées.")

    def _show_validation_errors(
        self,
        issues: Iterable[ValidationIssue],
    ) -> None:
        messages = "\n".join(f"• {issue.message}" for issue in issues)
        self.feedback.setText(messages)
        QMessageBox.warning(self, "Configuration invalide", messages)

    def _show_unexpected_error(self, message: str) -> None:
        self.feedback.setText(message)
        QMessageBox.critical(self, "Erreur", message)

    @staticmethod
    def _environment_label(environment: Environment) -> str:
        labels = {
            Environment.DEVELOPMENT: "Développement",
            Environment.RECETTE: "Recette",
            Environment.PRODUCTION: "Production",
        }
        return labels[environment]
