import copy
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .job_status import JobStatus
from .workflow import WorkflowStep


class Job(BaseModel):
    id: Any = None
    workflow_name: str
    status: JobStatus = JobStatus.QUEUED
    steps_completed: int = Field(default=0, ge=0)
    percent_completed: float = Field(default=0.0, ge=0.0, le=100.0)
    initial_input_value: Any = None
    last_return_value: Any = None
    user_context: Any = None
    requested_start_time: datetime | None = None

    def get_input_value(self) -> Any:
        input_val = (
            self.initial_input_value
            if self.steps_completed == 0
            else self.last_return_value
        )

        return copy.deepcopy(input_val)

    def mark_running(self, step: WorkflowStep) -> None:
        self.status = JobStatus.RUNNING

    def mark_failed(self, exception: Exception) -> None:
        self.status = JobStatus.FAILED

    def mark_step_n_completed(
        self,
        n: int,
        return_value: Any,
        total_steps: int,
    ) -> None:
        self.mark_n_steps_completed(
            n - self.steps_completed,
            return_value,
            total_steps,
        )

    def mark_n_steps_completed(
        self,
        n: int,
        return_value: Any,
        total_steps: int,
    ) -> None:
        print(f"===111.1=== n: {n}")
        print(f"===111.2=== steps_completed: {self.steps_completed}")
        print(f"===111.3=== steps_completed + n: {self.steps_completed + n}")
        print(f"===111.4=== total_steps: {total_steps}")
        self.steps_completed = min(self.steps_completed + n, total_steps)
        print(f"===112.1=== steps_completed: {self.steps_completed}")
        self.percent_completed = float((self.steps_completed / total_steps) * 100)
        print(f"===112.2=== percent_completed: {self.percent_completed}")
        self.status = (
            JobStatus.COMPLETED
            if self.steps_completed == total_steps
            else JobStatus.QUEUED
        )
        print(f"===112.2=== status: {self.status}")
        self.last_return_value = return_value

    def mark_aborted(self, message: str) -> None:
        self.status = JobStatus.ABORTED

    def should_be_requeued(self) -> bool:
        return self.status not in (
            JobStatus.ABORTED,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
        )
