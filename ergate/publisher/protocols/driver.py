from collections.abc import Generator
from typing import Protocol, TypeVar

from ...job import Job

JobType = TypeVar("JobType", bound=Job, covariant=True)


class PublisherDriverProtocol(Protocol[JobType]):
    def generate_jobs(self) -> Generator[JobType, None, None]: ...
