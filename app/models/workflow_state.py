from enum import Enum, auto


class WorkflowState(Enum):
    IDLE = auto()
    CHECKING_PREREQUISITES = auto()
    CAPTURING = auto()
    TELEPORTING = auto()
    SUMMONING = auto()
    ASSIGNING_FIRST_PET = auto()
    ASSIGNING_SECOND_PET = auto()
    ASSIGNING_THIRD_PET = auto()
    COMPLETE = auto()
    PAUSED = auto()
    STOPPED = auto()
    ERROR = auto()
