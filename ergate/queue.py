from typing import Protocol, TypeVar

from .job import Job

JobType = TypeVar("JobType", bound=Job)


class QueueProtocol(Protocol[JobType]):
    def put(self, job: JobType) -> None: ...
    def get_one(self) -> JobType: ...
