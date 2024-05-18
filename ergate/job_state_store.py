from typing import Protocol

from .job import Job


class JobStateStoreProtocol(Protocol):
    def save(self, job: Job) -> None: ...
