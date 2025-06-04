from enum import IntEnum, auto


class JobStatus(IntEnum):
    """Represents the status of a job."""

    SCHEDULED = auto()
    """
    Job has been scheduled to run at a specific time,
    but has not yet been published to the queue.
    """

    QUEUED = auto()
    """
    Job has been published to the queue and is waiting
    to be picked up by a worker.
    """

    RUNNING = auto()
    """
    Job has been picked up by a worker and is running.
    """

    COMPLETED = auto()
    """
    All steps that needed to run have completed successfully
    and there is nothing else to do with the job.
    """

    FAILED = auto()
    """
    A step in the job raised an unhandled exception, and
    the job has failed.
    """

    ABORTED = auto()
    """
    A step within the job requested to abort the job, so no
    further steps will run.
    """

    PENDING = auto()
    """
    Job has been created and is waiting to be picked up by
    the publisher.
    """

    CANCELLING = auto()
    """
    Job has been marked for cancellation, but is already
    QUEUED or RUNNING. Once the execution of the current
    step is complete, the job should be marked as CANCELLED
    if other steps would otherwise run. Alternatively, the
    job may be marked as ABORTED/COMPLETED/FAILED as needed.

    Depending on your state store and queue implementations,
    this state may not be known by the publisher or worker
    logic, and it's possible that it will need to be handled
    by logic in the state store directly.
    """

    CANCELLED = auto()
    """
    Job was marked for cancellation and has now reached
    a state where no further steps will run.
    """
