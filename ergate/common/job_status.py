from enum import IntEnum, auto


class JobStatus(IntEnum):
    ...  # Just here so the formatter doesn't think first string is docstring

    """Job has not been queued yet"""
    PENDING = auto()

    """Job is in the queue, awaiting processing"""
    QUEUED = auto()

    """Job has been taken by a worker and is currently running"""
    RUNNING = auto()

    """Job has been completed successfully - no further steps"""
    COMPLETED = auto()

    """An exception has been raised from one of the job's steps"""
    FAILED = auto()

    """Job has been aborted from within a step - execution stopped"""
    ABORTED = auto()

    """Job will be cancelled after the current step completes"""
    CANCELLING = auto()

    """Job has been cancelled - no further steps"""
    CANCELLED = auto()
