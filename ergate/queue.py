from typing import Protocol, TypeVar

from .job import Job

T = TypeVar("T", bound=Job)


class QueueProtocol(Protocol[T]):
    def put(self, job: T) -> None: ...
    def get_one(self) -> T: ...
