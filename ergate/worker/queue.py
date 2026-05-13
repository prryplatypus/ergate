from typing import Protocol, TypeVar

from ..job import Job

JobType_co = TypeVar("JobType_co", bound=Job, covariant=True)


class QueueProtocol(Protocol[JobType_co]):
    def get_one(self) -> JobType_co: ...
