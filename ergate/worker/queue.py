from typing import Protocol, TypeVar

from ..job import Job

JobType = TypeVar("JobType", bound=Job, covariant=True)


class QueueProtocol(Protocol[JobType]):
    def get_one(self) -> JobType: ...
