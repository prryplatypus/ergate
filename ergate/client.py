from typing import Any, Generic, TypeVar

from .job import Job
from .job_state_store import JobStateStoreClientProtocol
from .queue import QueueWriteProtocol

T = TypeVar("T", bound=Job)


class ErgateClient(Generic[T]):
    def __init__(
        self,
        job_state_store: JobStateStoreClientProtocol[T],
        queue: QueueWriteProtocol[T],
    ) -> None:
        self.job_state_store = job_state_store
        self.queue = queue

    def submit(self, job: T) -> None:
        self.job_state_store.create(job)
        self.queue.put(job)

    def get(self, job_id: Any) -> T:
        return self.job_state_store.get(job_id)
