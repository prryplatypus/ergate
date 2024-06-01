from __future__ import annotations

from contextlib import ExitStack
from typing import Callable, ContextManager, Generic, TypeVar

from .job import Job
from .job_runner import JobRunner
from .job_state_store import JobStateStoreWorkerProtocol
from .queue import QueueProtocol
from .workflow import Workflow
from .workflow_registry import WorkflowRegistry

T = TypeVar("T", bound=Job)


class Ergate(Generic[T]):
    def __init__(
        self,
        queue: QueueProtocol[T],
        job_state_store: JobStateStoreWorkerProtocol[T],
        lifespan: Callable[[Ergate], ContextManager[None]] | None = None,
    ) -> None:
        self.lifespan = lifespan

        self.workflow_registry = WorkflowRegistry()
        self.job_runner = JobRunner(
            queue,
            self.workflow_registry,
            job_state_store,
            self.on_error,
        )

    def on_error(self, exc: Exception) -> None: ...

    def register_workflow(self, workflow: Workflow) -> None:
        self.workflow_registry.register(workflow)

    def run(self) -> None:
        with ExitStack() as stack:
            if self.lifespan:
                stack.enter_context(self.lifespan(self))
            self.job_runner.run()
