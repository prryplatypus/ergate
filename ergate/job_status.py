from enum import IntEnum, auto


class JobStatus(IntEnum):
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    SCHEDULED = auto()
    FAILED = auto()
    ABORTED = auto()
