from enum import IntEnum, auto


class JobStatus(IntEnum):
    QUEUED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CREATED = auto()
