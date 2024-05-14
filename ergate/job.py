from pydantic import BaseModel

from .constants import JSONABLE
from .job_status import JobStatus


class Job(BaseModel):
    workflow_name: str
    id: str
    status: JobStatus = JobStatus.QUEUED
    steps_completed: int = 0
    percent_completed: int = 0
    initial_input_value: JSONABLE = None
    last_return_value: JSONABLE = None
    exception_traceback: str | None = None

    def get_input_value(self) -> JSONABLE:
        return (
            self.initial_input_value
            if self.steps_completed == 0
            else self.last_return_value
        )

    def mark_running(self) -> None:
        self.status = JobStatus.RUNNING

    def mark_failed(self, exception_traceback: str) -> None:
        self.status = JobStatus.FAILED
        self.exception_traceback = exception_traceback

    def mark_step_completed(self, return_value: JSONABLE, total_steps: int) -> None:
        self.steps_completed += 1
        self.percent_completed = int((self.steps_completed / total_steps) * 100)
        self.status = (
            JobStatus.COMPLETED
            if self.steps_completed == total_steps
            else JobStatus.QUEUED
        )
        self.last_return_value = return_value

    def should_be_requeued(self) -> bool:
        return self.status not in (
            JobStatus.COMPLETED,
            JobStatus.FAILED,
        )
