from typing import Protocol, TypeVar

from ..job import Job

JobType = TypeVar("JobType", bound=Job)


class PublisherQueueProtocol(Protocol[JobType]):
    def put_many(self, job: list[JobType]) -> None: ...
