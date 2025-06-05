from enum import Enum, auto


class ErgateSignal(Enum):
    JOB_RUN_START = auto()
    JOB_RUN_END = auto()
    JOB_RUN_FAIL = auto()
