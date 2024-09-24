from __future__ import annotations

from collections.abc import Callable
from contextlib import ExitStack
from typing import Generic, TypeVar

from .handler import ErrorHookHandler
from .job import Job
from .job_runner import JobRunner
from .queue import QueueProtocol
from .state_store import StateStoreProtocol
from .types import ExceptionHook, Lifespan
from .workflow import Workflow
from .workflow_registry import WorkflowRegistry

JobType = TypeVar("JobType", bound=Job)


class Ergate(Generic[JobType]):
    def __init__(
        self,
        queue: QueueProtocol[JobType],
        state_store: StateStoreProtocol[JobType],
        lifespan: Lifespan[Ergate[JobType]] | None = None,
        error_hook_handler: ErrorHookHandler[JobType] | None = None,
    ) -> None:
        self.lifespan = lifespan
        self.error_hook_handler: ErrorHookHandler[JobType] = (
            error_hook_handler or ErrorHookHandler()
        )

        self.workflow_registry = WorkflowRegistry()
        self.job_runner: JobRunner[JobType] = JobRunner(
            queue,
            self.workflow_registry,
            state_store,
            self.error_hook_handler,
        )

    def exception_hook(
        self, *exceptions: type[Exception]
    ) -> Callable[[ExceptionHook[JobType]], ExceptionHook[JobType]]:
        def decorator(func: ExceptionHook[JobType]) -> ExceptionHook[JobType]:
            for exception in exceptions:
                self.error_hook_handler.register(exception, func)
            return func

        return decorator

    def register_workflow(self, workflow: Workflow) -> None:
        self.workflow_registry.register(workflow)

    def run(self: Ergate[JobType]) -> None:
        with ExitStack() as stack:
            if self.lifespan:
                stack.enter_context(self.lifespan(self))
            self.job_runner.run()
