import asyncio

from .factory_registry import FactoryRegistry
from .factory import Factory, FACTORY_MODEL
from .job_runner import JobRunner
from .job_state_store import JobStateStoreProtocol
from .queue import QueueProtocol
from .workflow_registry import WorkflowRegistry
from .workflow import Workflow


class Ergate:
    def __init__(
        self,
        queue: QueueProtocol,
        job_state_store: JobStateStoreProtocol,
    ) -> None:
        self.factory_registry = FactoryRegistry()
        self.workflow_registry = WorkflowRegistry()
        self.queue = queue
        self.job_runner = JobRunner(queue, self.workflow_registry, job_state_store)

        self._task: asyncio.Task | None = None

    def register_factory(self, factory: Factory[FACTORY_MODEL]) -> None:
        self.factory_registry.register(factory)

    def register_workflow(self, workflow: Workflow) -> None:
        self.workflow_registry.register(workflow)

    def _initialize_steps(self) -> None:
        workflows = self.workflow_registry
        steps = (step for workflow in workflows for step in workflow._steps)

        for step in steps:
            input_arg, kwarg_info = step.check_and_get_argument_info()
            kwarg_factories = {
                kwarg_name: self.factory_registry[kwarg_type]
                for kwarg_name, kwarg_type in kwarg_info.items()
            }
            step.initialize(input_arg, kwarg_factories)

    async def __aenter__(self) -> None:
        self._task = asyncio.create_task(self.job_runner.run())

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        print("Stopping job runner")
        assert self._task is not None
        self.job_runner.stop()
        await self.job_runner.wait_stopped()
        self._task = None

    async def _startup(self) -> None:
        self._initialize_steps()

        async with self:
            try:
                await self.job_runner.wait_stopped()
            except asyncio.CancelledError:
                pass

    def run(self) -> None:
        asyncio.run(self._startup())
