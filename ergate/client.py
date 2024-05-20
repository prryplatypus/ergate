from .job import Job
from .job_state_store import JobStateStoreCreateProtocol
from .queue import QueueWriteProtocol


class ErgateClient:
    def __init__(
        self,
        job_state_store: JobStateStoreCreateProtocol,
        queue: QueueWriteProtocol,
    ) -> None:
        self.job_state_store = job_state_store
        self.queue = queue

    def submit(self, job: Job) -> None:
        self.job_state_store.create(job)
        self.queue.put(job)
