from enum import IntEnum, auto


class JobStatus(IntEnum):
    SCHEDULED = auto()
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    ABORTED = auto()
