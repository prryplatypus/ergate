from enum import IntEnum, auto


class JobStatus(IntEnum):
    PENDING = auto()
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    ABORTED = auto()
    CANCELLED = auto()
