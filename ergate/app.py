import asyncio

from .job_runner import JobRunner
from .job_state_store import JobStateStoreUpdateProtocol
from .queue import QueueProtocol
from .workflow import Workflow
from .workflow_registry import WorkflowRegistry


class Ergate:
    def __init__(
        self,
        queue: QueueProtocol,
        job_state_store: JobStateStoreUpdateProtocol,
    ) -> None:
        self.workflow_registry = WorkflowRegistry()
        self.queue = queue
        self.job_runner = JobRunner(
            queue,
            self.workflow_registry,
            job_state_store,
            self.on_error,
        )

        self._task: asyncio.Task | None = None

    def on_error(self, exc: Exception) -> None: ...

    def register_workflow(self, workflow: Workflow) -> None:
        self.workflow_registry.register(workflow)

    def run(self) -> None:
        self.job_runner.run()
