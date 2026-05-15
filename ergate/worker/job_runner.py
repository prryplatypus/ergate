from datetime import datetime, timedelta, timezone
from typing import Generic, TypeVar

from ..exceptions import (
    AbortJob,
    GoToEnd,
    GoToStep,
    RetryStepAfterSeconds,
    ReverseGoToError,
    UnknownStepError,
    UnknownWorkflowError,
)
from ..interrupt import DelayedKeyboardInterrupt
from ..job import Job
from ..log import LOG
from ..paths import GoToStepPath, NextStepPath
from ..workflow import WorkflowStep
from ..workflow_registry import WorkflowRegistry
from .queue import QueueProtocol
from .signals import ErgateSignal, SignalHandler
from .state_store import StateStoreProtocol

JobType = TypeVar("JobType", bound=Job)


class JobRunner(Generic[JobType]):
    def __init__(
        self,
        queue: QueueProtocol[JobType],
        workflow_registry: WorkflowRegistry,
        state_store: StateStoreProtocol[JobType],
        signal_handler: SignalHandler[JobType],
    ) -> None:
        self.queue = queue
        self.workflow_registry = workflow_registry
        self.state_store = state_store
        self.signal_handler = signal_handler

    def _run_job(self, job: JobType, step_to_run: WorkflowStep) -> None:
        input_value = job.get_input_value()

        LOG.info("Running %s - input value: %s", str(step_to_run), input_value)

        try:
            with step_to_run.build_args(job.user_context, input_value) as all_args:
                args, kwargs = all_args
                retval = step_to_run(*args, **kwargs)
        except AbortJob as exc:
            LOG.info("User requested to abort job: %s", exc)

            job.mark_aborted(exc.message)
        except RetryStepAfterSeconds as exc:
            LOG.info(
                "User requested to retry step after %d seconds - return value: %s",
                exc.seconds,
                exc.retval,
            )

            job.mark_scheduled(
                datetime.now(timezone.utc) + timedelta(seconds=exc.seconds),
                exc.retval,
            )
        except GoToEnd as exc:
            LOG.info("User requested to go to end of workflow - retval: %s", exc.retval)

            job.mark_step_n_completed(
                job.steps_completed,
                exc.retval,
                job.steps_completed + 1,
            )
        except GoToStep as exc:
            LOG.info(
                "User requested to go to step: %s (%d) - return value: %s",
                exc.step.name,
                exc.step.index,
                exc.retval,
            )

            if exc.step.index <= job.current_step:
                raise ReverseGoToError(
                    "User attempted to go to an earlier step, which is not permitted."
                )

            remaining_steps = max(
                (
                    len(path)
                    for path in step_to_run.workflow.paths[job.current_step]
                    if isinstance(path[0][0], GoToStepPath)
                    and path[0][0].step_name == exc.step.name
                ),
                default=len(step_to_run.workflow) - job.current_step,
            )

            job.mark_step_n_completed(
                exc.step.index,
                exc.retval,
                job.steps_completed + remaining_steps,
            )
        else:
            LOG.info("Step completed successfully - return value: %s", retval)

            remaining_steps = max(
                (
                    len(path)
                    for path in step_to_run.workflow.paths[job.current_step]
                    if isinstance(path[0][0], NextStepPath)
                ),
                default=len(step_to_run.workflow) - job.current_step + 1,
            )

            job.mark_step_n_completed(
                job.current_step + 1,
                retval,
                job.steps_completed + remaining_steps,
            )

    def _handle_job_lifetime(self, job: JobType) -> None:
        self.signal_handler.trigger(ErgateSignal.JOB_RUN_START, job)

        try:
            workflow = self.workflow_registry[job.workflow_name]
            step_to_run = workflow[job.current_step]
        except UnknownWorkflowError as uwe:
            LOG.exception(
                "Job makes reference to an unknown workflow ('%s')",
                job.workflow_name,
            )
            job.mark_failed(uwe)
            self.signal_handler.trigger(ErgateSignal.JOB_RUN_FAIL, job)
        except UnknownStepError as use:
            LOG.exception(
                "Job makes reference to an unknown step (#%d) in workflow '%s'",
                job.current_step,
                job.workflow_name,
            )
            job.mark_failed(use)
            self.signal_handler.trigger(ErgateSignal.JOB_RUN_FAIL, job)
        else:
            try:
                job.mark_running(step_to_run)
                self.state_store.update(job)
                self._run_job(job, step_to_run)
            except Exception as exc:  # noqa: BLE001
                LOG.exception("Job raised an exception")
                job.mark_failed(exc)
                self.signal_handler.trigger(ErgateSignal.JOB_RUN_FAIL, job)
        finally:
            self.state_store.update(job)
            self.signal_handler.trigger(ErgateSignal.JOB_RUN_END, job)

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
                    self._handle_job_lifetime(job)
            except KeyboardInterrupt:
                return
