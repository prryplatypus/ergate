from typing import Protocol, TypeVar

from ...job import Job

JobType = TypeVar("JobType", bound=Job, contravariant=True)


class PublisherQueueProtocol(Protocol[JobType]):
    def publish_job(self, job: JobType) -> None: ...
