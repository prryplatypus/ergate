from typing import Any

from .job import Job
from .job_state_store import JobStateStoreClientProtocol
from .queue import QueueWriteProtocol


class ErgateClient:
    def __init__(
        self,
        job_state_store: JobStateStoreClientProtocol,
        queue: QueueWriteProtocol,
    ) -> None:
        self.job_state_store = job_state_store
        self.queue = queue

    def submit(self, job: Job) -> None:
        self.job_state_store.create(job)
        self.queue.put(job)

    def get(self, job_id: Any) -> Job:
        return self.job_state_store.get(job_id)
