from typing import Any, Protocol, TypeVar

from .job import Job

T = TypeVar("T", bound=Job)


class JobStateStoreClientProtocol(Protocol):
    def create(self, job: Job) -> None: ...

    def get(self, job_id: Any) -> Job: ...


class JobStateStoreWorkerProtocol(Protocol):
    def update(self, job: Job) -> None: ...
