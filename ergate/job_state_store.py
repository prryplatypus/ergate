from typing import Protocol, TypeVar

from .job import Job

JobType = TypeVar("JobType", bound=Job, contravariant=True)


class JobStateStoreWorkerProtocol(Protocol[JobType]):
    def update(self, job: JobType) -> None: ...
