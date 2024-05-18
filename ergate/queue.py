from typing import Protocol

from .job import Job


class QueueProtocol(Protocol):
    def put(self, job: Job) -> None: ...

    def get_one(self) -> Job: ...
