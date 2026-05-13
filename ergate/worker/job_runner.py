from typing import Generic, TypeVar

from ..exceptions import AbortJob, GoToEnd, GoToStep, ReverseGoToError
from ..interrupt import DelayedKeyboardInterrupt
from ..job import Job
from ..log import LOG
from ..paths import GoToStepPath, NextStepPath
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

    def _run_job(self, job: JobType) -> None:
        self.signal_handler.trigger(ErgateSignal.JOB_RUN_START, job)

        input_value = job.get_input_value()

        workflow = self.workflow_registry[job.workflow_name]
        paths = workflow.paths[job.current_step]
        step_to_run = workflow[job.current_step]

        job.mark_running(step_to_run)
        self.state_store.update(job)

        try:
            try:
                LOG.info("Running %s - input value: %s", str(step_to_run), input_value)

                with step_to_run.build_args(job.user_context, input_value) as all_args:
                    args, kwargs = all_args
                    retval = step_to_run(*args, **kwargs)
            except AbortJob as exc:
                LOG.info("User requested to abort job: %s", exc)

                job.mark_aborted(exc.message)
            except GoToEnd as exc:
                LOG.info(
                    "User requested to go to end of workflow - return value: %s",
                    exc.retval,
                )

                job.mark_step_n_completed(
                    job.steps_completed, exc.retval, job.steps_completed + 1
                )
            except GoToStep as exc:
                LOG.info(
                    "User requested to go to step: %s (%s) - return value: %s",
                    exc.step.name,
                    exc.step.index,
                    exc.retval,
                )

                if exc.step.index <= job.current_step:
                    raise ReverseGoToError(
                        "User attempted to go to an earlier step, "
                        "which is not permitted."
                    )

                remaining_steps = max(
                    (
                        len(path)
                        for path in paths
                        if isinstance(path[0][0], GoToStepPath)
                        and path[0][0].step_name == exc.step.name
                    ),
                    default=len(workflow) - job.current_step,
                )

                job.mark_step_n_completed(
                    exc.step.index, exc.retval, job.steps_completed + remaining_steps
                )
            except Exception as exc:
                # Since `except GoToStep` potentially raises an exception, the logic
                # for handling exceptions had to be moved to a higher scope.
                raise exc
            else:
                LOG.info("Step completed successfully - return value: %s", retval)

                remaining_steps = max(
                    (
                        len(path)
                        for path in paths
                        if isinstance(path[0][0], NextStepPath)
                    ),
                    default=len(workflow) - job.current_step + 1,
                )

                job.mark_step_n_completed(
                    job.current_step + 1, retval, job.steps_completed + remaining_steps
                )
        except Exception as exc:
            LOG.exception("Job raised an exception")
            job.mark_failed(exc)
            self.signal_handler.trigger(ErgateSignal.JOB_RUN_FAIL, job)

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
                    self._run_job(job)
            except KeyboardInterrupt:
                return
