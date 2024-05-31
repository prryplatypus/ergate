from typing import Any, Protocol, TypeVar

from .job import Job

T = TypeVar("T", bound=Job)
U = TypeVar("U", bound=Job, contravariant=True)


class JobStateStoreClientProtocol(Protocol[T]):
    def create(self, job: T) -> None: ...

    def get(self, job_id: Any) -> T: ...


class JobStateStoreWorkerProtocol(Protocol[U]):
    def update(self, job: U) -> None: ...
