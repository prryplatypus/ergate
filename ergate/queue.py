from typing import Protocol

from .job import Job


class QueueWriteProtocol(Protocol):
    def put(self, job: Job) -> None: ...


class QueueProtocol(QueueWriteProtocol):
    def get_one(self) -> Job: ...
