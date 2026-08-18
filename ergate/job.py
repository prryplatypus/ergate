import copy
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from .job_status import JobStatus

if TYPE_CHECKING:
    from .workflow import WorkflowStep


class Job(BaseModel):
    id: Any = None
    workflow_name: str
    status: JobStatus = JobStatus.PENDING
    current_step: int = Field(default=0, ge=0)
    steps_completed: int = Field(default=0, ge=0)
    percent_completed: float = Field(default=0.0, ge=0.0, le=100.0)
    initial_input_value: Any = None
    last_return_value: Any = None
    user_context: Any = None
    requested_start_time: datetime | None = None

    def get_input_value(self) -> Any:
        input_val = (
            self.initial_input_value
            if self.steps_completed == 0 and not self.last_return_value
            else self.last_return_value
        )

        return copy.deepcopy(input_val)

    def mark_aborted(self, message: str) -> None:
        self.status = JobStatus.ABORTED

    def mark_failed(self, exception: Exception) -> None:
        self.status = JobStatus.FAILED

    def mark_running(self, step: "WorkflowStep") -> None:
        self.status = JobStatus.RUNNING

    def mark_scheduled(
        self,
        requested_start_time: datetime | timedelta,
        modified_input_value: Any,
    ) -> None:
        self.status = JobStatus.SCHEDULED
        self.last_return_value = modified_input_value

        if isinstance(requested_start_time, timedelta):
            requested_start_time = datetime.now(timezone.utc) + requested_start_time

        self.requested_start_time = requested_start_time

    def mark_step_n_completed(
        self,
        n: int,
        return_value: Any,
        total_steps: int,
        *,
        requested_start_time: datetime | timedelta | None = None,
    ) -> None:
        self.current_step = n
        self.steps_completed = min(self.steps_completed + 1, total_steps)
        self.percent_completed = float((self.steps_completed / total_steps) * 100)

        if requested_start_time:
            self.mark_scheduled(requested_start_time, return_value)
            return

        if self.steps_completed == total_steps:
            self.status = JobStatus.COMPLETED
        else:
            self.status = JobStatus.PENDING

        self.last_return_value = return_value
