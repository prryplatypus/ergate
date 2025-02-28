from typing import Protocol, TypeVar

from ..common.job import Job

JobType = TypeVar("JobType", bound=Job)


class PublisherQueueProtocol(Protocol[JobType]):
    def put_many(self, jobs: list[JobType]) -> None: ...
