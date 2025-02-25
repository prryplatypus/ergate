from typing import Protocol, TypeVar

from ..job import Job

JobType = TypeVar("JobType", bound=Job)


class PublisherStateStore(Protocol[JobType]):
    def fetch_many_and_transition_to_queued(self) -> list[JobType]: ...
