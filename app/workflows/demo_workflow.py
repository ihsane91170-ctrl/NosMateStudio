from app.actions.click import ClickAction, ClickType
from app.actions.press_key import PressKeyAction
from app.actions.wait import WaitAction
from app.calibration.models import CalibrationTarget
from app.configuration.models import Action


class DemoWorkflow:
    def steps(self):
        return [
            PressKeyAction(Action.PET_STORAGE),
            WaitAction(0.5),
            ClickAction(
                CalibrationTarget.PET_ICON_1,
            ),
            WaitAction(0.2),
            ClickAction(
                CalibrationTarget.ACCOMPANY_BUTTON,
                ClickType.DOUBLE,
            ),
            WaitAction(1.0),
            PressKeyAction(Action.XP_MAP),
        ]