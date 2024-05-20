from typing import Protocol

from .job import Job


class JobStateStoreCreateProtocol(Protocol):
    def create(self, job: Job) -> None: ...


class JobStateStoreUpdateProtocol(Protocol):
    def update(self, job: Job) -> None: ...
