import traceback
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .job_status import JobStatus


class Job(BaseModel):
    id: Any = None
    workflow_name: str
    step_name: str | None = None
    status: JobStatus = JobStatus.QUEUED
    steps_completed: int = Field(default=0, ge=0)
    percent_completed: float = Field(default=0.0, ge=0.0, le=100.0)
    initial_input_value: Any = None
    last_return_value: Any = None
    exception_traceback: str | None = None
    user_context: Any = None
    requested_start_time: datetime | None = None

    def get_input_value(self) -> Any:
        return (
            self.initial_input_value
            if self.steps_completed == 0
            else self.last_return_value
        )

    def mark_running(self, step_name: str) -> None:
        self.status = JobStatus.RUNNING
        self.step_name = step_name

    def mark_failed(self, exception: Exception) -> None:
        self.status = JobStatus.FAILED
        self.step_name = None
        self.exception_traceback = traceback.format_exc()

    def mark_n_steps_completed(
        self,
        n: int,
        return_value: Any,
        total_steps: int,
    ) -> None:
        self.steps_completed = min(self.steps_completed + n, total_steps)
        self.percent_completed = float((self.steps_completed / total_steps) * 100)
        self.status = (
            JobStatus.COMPLETED
            if self.steps_completed == total_steps
            else JobStatus.QUEUED
        )
        self.step_name = None
        self.last_return_value = return_value

    def mark_aborted(self) -> None:
        self.status = JobStatus.ABORTED
        self.step_name = None

    def should_be_requeued(self) -> bool:
        return self.status not in (
            JobStatus.ABORTED,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
        )
