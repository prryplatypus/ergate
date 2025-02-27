from typing import Protocol, TypeVar

from ..common.job import Job

JobType = TypeVar("JobType", bound=Job, covariant=True)


class WorkerQueueProtocol(Protocol[JobType]):
    def get_one(self) -> JobType: ...
