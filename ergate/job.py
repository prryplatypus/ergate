from typing import Any

from pydantic import BaseModel, Field

from .job_status import JobStatus


class Job(BaseModel):
    id: Any = None
    workflow_name: str
    status: JobStatus = JobStatus.QUEUED
    steps_completed: int = Field(default=0, ge=0)
    percent_completed: int = Field(default=0, ge=0, le=100)
    initial_input_value: Any = None
    last_return_value: Any = None
    exception_traceback: str | None = None
    user_context: Any = None

    def get_input_value(self) -> Any:
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

    def mark_n_steps_completed(
        self,
        n: int,
        return_value: Any,
        total_steps: int,
    ) -> None:
        self.steps_completed = min(self.steps_completed + n, total_steps)
        self.percent_completed = int((self.steps_completed / total_steps) * 100)
        self.status = (
            JobStatus.COMPLETED
            if self.steps_completed == total_steps
            else JobStatus.QUEUED
        )
        self.last_return_value = return_value

    def mark_aborted(self) -> None:
        self.status = JobStatus.ABORTED

    def should_be_requeued(self) -> bool:
        return self.status not in (
            JobStatus.ABORTED,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
        )
