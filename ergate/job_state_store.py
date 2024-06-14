from typing import Protocol, TypeVar

from .job import Job

T = TypeVar("T", bound=Job, contravariant=True)


class JobStateStoreWorkerProtocol(Protocol[T]):
    def update(self, job: T) -> None: ...
