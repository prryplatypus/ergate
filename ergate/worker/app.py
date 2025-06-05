from __future__ import annotations

from collections.abc import Callable
from contextlib import ExitStack
from typing import Generic, TypeVar

from ..job import Job
from ..types import Lifespan
from ..types import SignalHandler as SignalHandlerType
from ..workflow import Workflow
from ..workflow_registry import WorkflowRegistry
from .job_runner import JobRunner
from .queue import QueueProtocol
from .signals import ErgateSignal, SignalHandler
from .state_store import StateStoreProtocol

JobType = TypeVar("JobType", bound=Job)


class ErgateWorker(Generic[JobType]):
    def __init__(
        self,
        queue: QueueProtocol[JobType],
        state_store: StateStoreProtocol[JobType],
        lifespan: Lifespan[ErgateWorker[JobType]] | None = None,
        signal_handler: SignalHandler[JobType] | None = None,
    ) -> None:
        self.lifespan = lifespan
        self.signal_handler: SignalHandler[JobType] = signal_handler or SignalHandler()

        self.workflow_registry = WorkflowRegistry()
        self.job_runner: JobRunner[JobType] = JobRunner(
            queue,
            self.workflow_registry,
            state_store,
            self.signal_handler,
        )

    def signal(
        self, signal: ErgateSignal
    ) -> Callable[[SignalHandlerType[JobType]], SignalHandlerType[JobType]]:
        def decorator(func: SignalHandlerType[JobType]) -> SignalHandlerType[JobType]:
            self.signal_handler.register(signal, func)
            return func

        return decorator

    def register_workflow(self, workflow: Workflow) -> None:
        self.workflow_registry.register(workflow)

    def run(self) -> None:
        with ExitStack() as stack:
            if self.lifespan:
                stack.enter_context(self.lifespan(self))
            self.job_runner.run()
