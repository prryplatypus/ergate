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
        paths = workflow.calculate_paths(job.steps_completed)

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
            job.mark_step_n_completed(job.steps_completed + 1, exc.retval, job.steps_completed + 1)
            LOG.info(
                "User requested to go to end of workflow - return value: %s", exc.retval
            )
        except GoToStep as exc:
            if not exc.has_step:
                err = "No label or index provided for GoToStep."
                raise ValueError(err)

            if exc.n is not None:
                idx = exc.n
                LOG.info(
                    "User requested to go to step: %s - return value: %s",
                    idx,
                    exc.retval,
                )
            else:
                idx = workflow.get_label_index(exc.label)
                LOG.info(
                    "User requested to go to step: %s (%s) - return value: %s",
                    exc.label,
                    idx,
                    exc.retval,
                )

            remaining_steps = max(map(len, filter(lambda steps: isinstance(steps[0][1], GoToStep) and steps[0][1].next_step == exc.next_step, paths)), default=0)
            job.mark_step_n_completed(idx, exc.retval, job.steps_completed + 1 + remaining_steps)
        except SkipNSteps as exc:
            LOG.info("User requested to skip %d steps", exc.n)

            remaining_steps = max(map(len, filter(lambda steps: isinstance(steps[0][1], SkipNSteps) and steps[0][1].n == exc.n, paths)), default=0)
            job.mark_n_steps_completed(exc.n + 1, exc.retval, job.steps_completed + 1 + remaining_steps)
        except Exception as exc:
            LOG.exception("Job raised an exception")
            job.mark_failed(exc)
            self.error_hook_handler.notify(job, exc)
        else:
            LOG.info("Step completed successfully - return value: %s", retval)
            remaining_steps = max(map(len, filter(lambda steps: steps[0][1] is None)), default=0)
            job.mark_n_steps_completed(1, retval, job.steps_completed + 1 + remaining_steps)

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
