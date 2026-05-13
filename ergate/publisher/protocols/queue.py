from typing import Protocol, TypeVar

from ...job import Job

JobType_contra = TypeVar("JobType_contra", bound=Job, contravariant=True)


class PublisherQueueProtocol(Protocol[JobType_contra]):
    def publish_job(self, job: JobType_contra) -> None: ...
