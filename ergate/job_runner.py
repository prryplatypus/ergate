from typing import Generic, TypeVar

from .exceptions import AbortJob, GoToEnd, GoToStep, SkipNSteps
from .handler import ErrorHookHandler
from .interrupt import DelayedKeyboardInterrupt
from .job import Job
from .log import LOG
from .queue import QueueProtocol
from .state_store import StateStoreProtocol
from .workflow_registry import WorkflowRegistry

JobType = TypeVar("JobType", bound=Job)


class JobRunner(Generic[JobType]):
    def __init__(
        self,
        queue: QueueProtocol[JobType],
        workflow_registry: WorkflowRegistry,
        state_store: StateStoreProtocol[JobType],
        error_hook_handler: ErrorHookHandler[JobType],
    ) -> None:
        self.queue = queue
        self.workflow_registry = workflow_registry
        self.state_store = state_store
        self.error_hook_handler = error_hook_handler

    def _run_job(self, job: JobType) -> None:
        input_value = job.get_input_value()

        workflow = self.workflow_registry[job.workflow_name]
        step_to_run = workflow[job.steps_completed]

        job.mark_running(step_to_run)
        self.state_store.update(job)

        try:
            LOG.info("Running %s - input value: %s", str(step_to_run), input_value)
            with step_to_run.build_args(job.user_context, input_value) as all_args:
                args, kwargs = all_args
                retval = step_to_run(*args, **kwargs)
        except AbortJob as exc:
            LOG.info("User requested to abort job: %s", exc)
            job.mark_aborted(exc.message)
        except GoToEnd as exc:
            job.mark_step_n_completed(len(workflow), exc.retval, len(workflow))
        except GoToStep as exc:
            if not exc.has_step:
                err = 'No label or index provided for GoToStep'
                raise ValueError(err)

            if exc.n is not None:
                idx = exc.n
                LOG.info(f"User requested to go to step: {idx}")
            else:
                idx = workflow.get_label_index(exc.label)
                LOG.info(f"User requested to go to step: {exc.label} ({idx})")

            job.mark_step_n_completed(idx - 1, exc.retval, len(workflow))
        except SkipNSteps as exc:
            LOG.info("User requested to skip %d steps", exc.n)
            job.mark_n_steps_completed(exc.n + 1, exc.retval, len(workflow))
        except Exception as exc:
            LOG.exception("Job raised an exception")
            job.mark_failed(exc)
            self.error_hook_handler.notify(job, exc)
        else:
            LOG.info("Step completed successfully - return value: %s", retval)
            job.mark_n_steps_completed(1, retval, len(workflow))

        self.state_store.update(job)

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

            LOG.info("Job acquired")
            try:
                with DelayedKeyboardInterrupt():
                    self._run_job(job)
            except KeyboardInterrupt:
                return
