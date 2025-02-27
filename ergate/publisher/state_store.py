from typing import Protocol, TypeVar

from ..common.job import Job

JobType = TypeVar("JobType", bound=Job)


class PublisherStateStoreProtocol(Protocol[JobType]):
    def fetch_many_and_transition_to_queued(self) -> list[JobType]: ...
