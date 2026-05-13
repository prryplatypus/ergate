from collections.abc import Generator
from typing import Protocol, TypeVar

from ...job import Job

JobType_co = TypeVar("JobType_co", bound=Job, covariant=True)


class PublisherDriverProtocol(Protocol[JobType_co]):
    def generate_jobs(self) -> Generator[JobType_co, None, None]: ...
