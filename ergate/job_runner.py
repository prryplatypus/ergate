import traceback
from typing import Callable, TypeVar

from .exceptions import AbortJob, SkipNSteps
from .interrupt import DelayedKeyboardInterrupt
from .job import Job
from .job_state_store import JobStateStoreWorkerProtocol
from .log import LOG
from .queue import QueueProtocol
from .workflow_registry import WorkflowRegistry

T = TypeVar("T", bound=Job)


class JobRunner:
    def __init__(
        self,
        queue: QueueProtocol[T],
        workflow_registry: WorkflowRegistry,
        job_state_store: JobStateStoreWorkerProtocol[T],
        on_error_callback: Callable[[Exception], None],
    ) -> None:
        self.queue = queue
        self.workflow_registry = workflow_registry
        self.job_state_store = job_state_store
        self.on_error_callback = on_error_callback

    def _run_job(self, job: T) -> None:
        input_value = job.get_input_value()

        try:
            workflow = self.workflow_registry[job.workflow_name]
            step_to_run = workflow[job.steps_completed]
            job.mark_running(step_to_run.name)
            self.job_state_store.update(job)
            LOG.info("Running %s - input value: %s", str(step_to_run), input_value)
            retval = step_to_run(input_value, job.user_context)
        except AbortJob as exc:
            LOG.info("User requested to abort job: %s", exc)
            job.mark_aborted()
        except SkipNSteps as exc:
            LOG.info("User requested to skip %d steps", exc.n)
            job.mark_n_steps_completed(exc.n + 1, exc.retval, len(workflow))
        except Exception as exc:
            LOG.exception("Job raised an exception")
            job.mark_failed(traceback.format_exc())
            self.on_error_callback(exc)
        else:
            LOG.info("Step completed successfully - return value: %s", retval)
            job.mark_n_steps_completed(1, retval, len(workflow))

        self.job_state_store.update(job)

        if job.should_be_requeued():
            LOG.info("Requeuing job")
            self.queue.put(job)

    def run(self) -> None:
        while True:
            LOG.info("Listening for next job")
            try:
                job = self.queue.get_one()
            except KeyboardInterrupt:
                return
            except Exception as exc:
                self.on_error_callback(exc)
                raise

            LOG.info("Job acquired")
            try:
                with DelayedKeyboardInterrupt():
                    try:
                        self._run_job(job)
                    except Exception as exc:
                        self.on_error_callback(exc)
                        raise
            except KeyboardInterrupt:
                return
