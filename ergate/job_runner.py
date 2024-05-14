import traceback

from asyncio import Event, wait, FIRST_COMPLETED, ensure_future

from .job_state_store import JobStateStoreProtocol
from .job import Job
from .queue import QueueProtocol
from .workflow_registry import WorkflowRegistry


class JobRunner:
    def __init__(
        self,
        queue: QueueProtocol,
        workflow_registry: WorkflowRegistry,
        job_state_store: JobStateStoreProtocol,
    ) -> None:
        self.queue = queue
        self.workflow_registry = workflow_registry
        self.job_state_store = job_state_store

        self._stop = Event()
        self._stopped = Event()

    async def _run(self) -> None:
        pending = [ensure_future(self._stop.wait())]
        done, pending = await wait(
            [
                ensure_future(self.queue.get_one()),
                *[p for p in pending],
            ],
            return_when=FIRST_COMPLETED,
        )

        if self._stop.is_set():
            for pending_task in pending:
                pending_task.cancel()
            return

        job = done.pop().result()
        assert isinstance(job, Job)

        try:
            job.mark_running()
            await self.job_state_store.save(job)

            input_value = job.get_input_value()

            workflow = self.workflow_registry[job.workflow_name]
            step_to_run = workflow[job.steps_completed]

            retval = step_to_run(input_value)
        except Exception:
            job.mark_failed(traceback.format_exc())
            await self.job_state_store.save(job)
            return
        finally:
            await self.queue.task_done()

        job.mark_step_completed(retval, len(workflow))
        await self.job_state_store.save(job)

        if job.should_be_requeued():
            await self.queue.put(job)

    async def run(self) -> None:
        while not self._stop.is_set():
            try:
                await self._run()
            except Exception:
                self.stop()
        self._stopped.set()

    def stop(self) -> None:
        self._stop.set()

    async def wait_stopped(self) -> None:
        await self._stopped.wait()
