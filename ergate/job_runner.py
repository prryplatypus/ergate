import traceback

from typing import Callable

from .interrupt import DelayedKeyboardInterrupt
from .job import Job
from .job_state_store import JobStateStoreProtocol
from .queue import QueueProtocol
from .workflow_registry import WorkflowRegistry


class JobRunner:
    def __init__(
        self,
        queue: QueueProtocol,
        workflow_registry: WorkflowRegistry,
        job_state_store: JobStateStoreProtocol,
        on_error_callback: Callable[[Exception], None],
    ) -> None:
        self.queue = queue
        self.workflow_registry = workflow_registry
        self.job_state_store = job_state_store
        self.on_error_callback = on_error_callback

    def _run_job(self, job: Job) -> None:
        job.mark_running()
        self.job_state_store.save(job)

        input_value = job.get_input_value()

        try:
            workflow = self.workflow_registry[job.workflow_name]
            step_to_run = workflow[job.steps_completed]
            retval = step_to_run(input_value)
        except Exception as exc:
            self.on_error_callback(exc)
            job.mark_failed(traceback.format_exc())
            self.job_state_store.save(job)
            return
        finally:
            self.queue.task_done()

        job.mark_step_completed(retval, len(workflow))
        self.job_state_store.save(job)

        if job.should_be_requeued():
            self.queue.put(job)

    def run(self) -> None:
        while True:
            try:
                job = self.queue.get_one()
            except KeyboardInterrupt:
                return
            except Exception as exc:
                self.on_error_callback(exc)
                raise

            try:
                with DelayedKeyboardInterrupt():
                    try:
                        self._run_job(job)
                    except Exception as exc:
                        self.on_error_callback(exc)
                        raise
            except KeyboardInterrupt:
                return
