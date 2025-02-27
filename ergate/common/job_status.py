from enum import IntEnum, auto


class JobStatus(IntEnum):
    PENDING = auto()
    """Job has not been queued yet"""

    QUEUED = auto()
    """Job is in the queue, awaiting processing"""

    RUNNING = auto()
    """Job has been taken by a worker and is currently running"""

    COMPLETED = auto()
    """Job has been completed successfully - no further steps"""

    FAILED = auto()
    """An exception has been raised from one of the job's steps"""

    ABORTED = auto()
    """Job has been aborted from within a step - execution stopped"""

    CANCELLING = auto()
    """Job will be cancelled after the current step completes"""

    CANCELLED = auto()
    """Job has been cancelled - no further steps"""
