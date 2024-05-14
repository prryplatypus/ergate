from typing import Protocol
from .job import Job


class QueueProtocol(Protocol):
    async def put(self, job: Job) -> None: ...

    async def get_one(self) -> Job: ...

    async def task_done(self) -> None: ...
