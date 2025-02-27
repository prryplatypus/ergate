from typing import Protocol, TypeVar

from ..common.job import Job

JobType = TypeVar("JobType", bound=Job, contravariant=True)


class WorkerStateStoreProtocol(Protocol[JobType]):
    def update(self, job: JobType) -> None: ...
