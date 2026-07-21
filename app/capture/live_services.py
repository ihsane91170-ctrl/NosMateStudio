from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
from typing import Callable

from PIL import Image

from app.automation.action_engine import ActionEngine
from app.automation.input_controller import InputController
from app.capture.controller import CaptureAttemptKind
from app.capture.flight_recorder import CaptureFlightRecorder
from app.combat.chicken_capture import (
    CaptureOutcome,
    ChickenCaptureConfig,
    ChickenCaptureService,
)
from app.executors.mouse.pyautogui_executor import PyAutoGUIMouseExecutor
from app.vision.ai_detector import UltralyticsObjectDetector
from app.vision.ai_target_selector import AITargetSelector
from app.vision.hp_state_reader import HpStateReader
from app.vision.screenshot_provider import PillowScreenshotBackend, WindowScreenshotProvider
from app.vision.temporal_target_validator import TemporalTargetValidator
from app.vision.window_detector import WindowDetector


@dataclass(frozen=True, slots=True)
class LiveCaptureSettings:
    confidence: float = 0.25
    max_attacks: int = 3
    selection_delay_seconds: float = 0.35
    hp_update_delay_seconds: float = 0.65
    confirmation_reads: int = 2
    return_hotkey: str = "-"
    return_delay_seconds: float = 2.0
    standby_delay_seconds: float = 0.35
    real_click_confidence: float = 0.90
    validation_frames: int = 3
    required_confirmations: int = 2
    validation_frame_delay_seconds: float = 0.12


class LiveChickenCaptureAdapter:
    """Relie le contrôleur de lot aux briques réelles validées dans Vision Debug."""

    def __init__(
        self,
        *,
        project_root: Path,
        settings: LiveCaptureSettings | None = None,
        window_detector: WindowDetector | None = None,
        screenshot_provider: WindowScreenshotProvider | None = None,
        ai_detector: UltralyticsObjectDetector | None = None,
        target_selector: AITargetSelector | None = None,
        capture_service: ChickenCaptureService | None = None,
        flight_recorder: CaptureFlightRecorder | None = None,
        target_validator: TemporalTargetValidator | None = None,
    ) -> None:
        self._settings = settings or LiveCaptureSettings()
        self._window_detector = window_detector or WindowDetector("NosTale")
        self._screenshot_provider = screenshot_provider or WindowScreenshotProvider(
            PillowScreenshotBackend()
        )
        self._ai_detector = ai_detector or UltralyticsObjectDetector(
            project_root / "assets" / "models" / "chicken_detector.pt"
        )
        self._target_selector = target_selector or AITargetSelector()
        self._target_validator = target_validator or TemporalTargetValidator(
            selector=self._target_selector,
            minimum_confidence=self._settings.real_click_confidence,
            required_frames=self._settings.required_confirmations,
        )
        if capture_service is None:
            action_engine = ActionEngine(
                PyAutoGUIMouseExecutor(enabled=True),
                InputController(simulation_mode=False),
            )
            capture_service = ChickenCaptureService(action_engine, HpStateReader())
        self._capture_service = capture_service
        self._flight_recorder = flight_recorder or CaptureFlightRecorder(
            project_root / "vision_logs" / "capture_batch"
        )
        self._recording_enabled = True
        self._keyboard = InputController(simulation_mode=False)
        self.last_message = ""
        self.last_attempt_kind = CaptureAttemptKind.SEARCH_REJECTED
        self.last_diagnostic_dir: Path | None = None

    def set_recording_enabled(self, enabled: bool) -> None:
        self._recording_enabled = bool(enabled)

    def capture_one(self) -> bool:
        self.last_attempt_kind = CaptureAttemptKind.SEARCH_REJECTED
        # NosMate Studio conserve normalement le focus après le clic sur le bouton.
        # On remet explicitement NosTale au premier plan avant la capture écran et
        # avant toute injection souris/clavier.
        if not self._window_detector.activate():
            self.last_message = "Impossible d'activer la fenêtre NosTale."
            return False
        time.sleep(0.20)

        window = self._window_detector.detect()
        if window is None:
            self.last_message = "Fenêtre NosTale introuvable."
            return False

        try:
            screenshots: list[Image.Image] = []
            detection_frames = []
            for frame_index in range(self._settings.validation_frames):
                current_window = self._window_detector.detect()
                if current_window is None:
                    raise RuntimeError("Fenêtre NosTale perdue pendant la validation.")
                frame = self._screenshot_provider.capture(current_window)
                screenshots.append(frame)
                detection_frames.append(
                    self._ai_detector.detect(
                        frame,
                        confidence=self._settings.confidence,
                    )
                )
                if frame_index + 1 < self._settings.validation_frames:
                    time.sleep(self._settings.validation_frame_delay_seconds)

            screenshot = screenshots[-1]
            detections = detection_frames[-1]
            validation = self._target_validator.validate(
                tuple(detection_frames),
                image_width=screenshot.width,
                image_height=screenshot.height,
            )
            selected = validation.target if validation.accepted else None
        except Exception as exc:
            self.last_message = f"Détection IA impossible : {type(exc).__name__}: {exc}"
            return False

        diagnostic_dir = None
        if self._recording_enabled:
            try:
                diagnostic_dir = self._flight_recorder.record_detection(
                    image=screenshot,
                    detections=detections,
                    selected=selected,
                    window=window,
                    confidence_threshold=self._settings.confidence,
                )
                self.last_diagnostic_dir = diagnostic_dir
            except Exception as exc:
                # Le journal ne doit jamais bloquer la capture réelle.
                self.last_message = (
                    f"Avertissement Flight Recorder : {type(exc).__name__}: {exc}"
                )

        if selected is None:
            chicken_count = sum(
                1 for detection in detections
                if str(getattr(detection, "class_name", "")).casefold() == "chicken"
            )
            self.last_message = (
                f"Clic bloqué par sécurité : {validation.reason} "
                f"Dernière image : {len(detections)} détection(s), "
                f"dont {chicken_count} poule(s). "
                f"Seuil clic réel : {self._settings.real_click_confidence:.2f}."
            )
            if diagnostic_dir is not None:
                self._flight_recorder.record_result(
                    diagnostic_dir, success=False, message=self.last_message
                )
                self.last_message += f" Diagnostic : {diagnostic_dir}"
            return False

        local_x, local_y = selected.detection.center
        screen_x = window.left + local_x
        screen_y = window.top + local_y

        def capture_image() -> Image.Image:
            current = self._window_detector.detect()
            if current is None:
                raise RuntimeError("Fenêtre NosTale perdue pendant la capture.")
            return self._screenshot_provider.capture(current)

        try:
            result = self._capture_service.execute(
                x=screen_x,
                y=screen_y,
                capture_image=capture_image,
                config=ChickenCaptureConfig(
                    max_attacks=self._settings.max_attacks,
                    selection_delay_seconds=self._settings.selection_delay_seconds,
                    hp_update_delay_seconds=self._settings.hp_update_delay_seconds,
                    confirmation_reads=self._settings.confirmation_reads,
                ),
            )
        except Exception as exc:
            self.last_message = f"Attaque/capture impossible : {type(exc).__name__}: {exc}"
            return False

        success = result.outcome is CaptureOutcome.CAPTURE_SENT
        self.last_attempt_kind = (
            CaptureAttemptKind.CAPTURED if success
            else CaptureAttemptKind.CAPTURE_FAILED
        )
        self.last_message = (
            f"{result.outcome.name} — {result.attacks_sent} attaque(s), "
            f"{result.capture_attempts} tentative(s) de capture."
        )
        if diagnostic_dir is not None:
            self._flight_recorder.record_result(
                diagnostic_dir,
                success=success,
                message=self.last_message,
                outcome=result.outcome.name,
                attacks_sent=result.attacks_sent,
                capture_attempts=result.capture_attempts,
            )
            self.last_message += f" Diagnostic : {diagnostic_dir}"
        return success

    def put_first_companion_on_standby(self) -> bool:
        """Met la première poule capturée en mode Rester avec la touche S."""
        try:
            if not self._window_detector.activate():
                self.last_message = "Impossible d'activer NosTale pour envoyer S."
                return False
            time.sleep(0.15)
            self._keyboard.press("s")
            time.sleep(self._settings.standby_delay_seconds)
        except Exception as exc:
            self.last_message = f"Mise en standby impossible : {type(exc).__name__}: {exc}"
            return False
        self.last_message = "Première poule mise en standby avec S."
        return True


class HotkeyReturnToExpZone:
    """Ouvre le retour XP, attend le dialogue puis confirme avec Entrée."""

    def __init__(
        self,
        hotkey: str,
        *,
        delay_seconds: float = 4.0,
        confirmation_delay_seconds: float = 0.80,
        activation_delay_seconds: float = 0.20,
        keyboard: InputController | None = None,
        window_detector: WindowDetector | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._hotkey = hotkey
        self._delay_seconds = delay_seconds
        self._confirmation_delay_seconds = confirmation_delay_seconds
        self._activation_delay_seconds = activation_delay_seconds
        self._keyboard = keyboard or InputController(simulation_mode=False)
        self._window_detector = window_detector or WindowDetector("NosTale")
        self._sleep = sleep_fn
        self.last_message = ""

    def return_to_exp_zone(self) -> bool:
        try:
            if not self._window_detector.activate():
                self.last_message = (
                    "Retour zone XP impossible : fenêtre NosTale non activée."
                )
                return False

            self._sleep(self._activation_delay_seconds)
            self._keyboard.press(self._hotkey)

            # Le dialogue de confirmation n'est pas instantané dans NosTale.
            # L'ancien délai de 350 ms pouvait envoyer Entrée avant son affichage.
            self._sleep(self._confirmation_delay_seconds)
            self._keyboard.press("enter")

            # Laisse le temps au changement de carte de se terminer avant que
            # le contrôleur ne considère le retour comme achevé.
            self._sleep(self._delay_seconds)
        except Exception as exc:
            self.last_message = f"Retour zone XP impossible : {type(exc).__name__}: {exc}"
            return False

        self.last_message = (
            f"Retour XP : touche « {self._hotkey} », attente "
            f"{self._confirmation_delay_seconds:.2f}s, confirmation Entrée, "
            f"puis attente chargement {self._delay_seconds:.2f}s."
        )
        return True
