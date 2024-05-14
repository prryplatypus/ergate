from typing import Protocol

from .job import Job


class JobStateStoreProtocol(Protocol):
    async def save(self, job: Job) -> None: ...
