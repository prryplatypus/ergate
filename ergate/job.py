from datetime import datetime
from json import dumps

from .constants import JSONABLE, JSONABLE_AS_TUPLE
from .exceptions import ValidationError
from .job_status import JobStatus


class Job:
    def __init__(
        self,
        id: JSONABLE,
        workflow_name: str,
        status: JobStatus = JobStatus.QUEUED,
        steps_completed: int = 0,
        percent_completed: int = 0,
        initial_input_value: JSONABLE = None,
        last_return_value: JSONABLE = None,
        requested_start_time: datetime | None = None,
        exception_traceback: str | None = None,
    ) -> None:
        self._validate_init_values(
            id,
            workflow_name,
            status,
            steps_completed,
            percent_completed,
            initial_input_value,
            last_return_value,
            requested_start_time,
            exception_traceback,
        )

        self.id = id
        self.workflow_name = workflow_name
        self.status = status
        self.steps_completed = steps_completed
        self.percent_completed = percent_completed
        self.initial_input_value = initial_input_value
        self.last_return_value = last_return_value
        self.requested_start_time = requested_start_time
        self.exception_traceback = exception_traceback

    def _validate_init_values(
        self,
        id: JSONABLE,
        workflow_name: str,
        status: JobStatus,
        steps_completed: int,
        percent_completed: int,
        initial_input_value: JSONABLE,
        last_return_value: JSONABLE,
        requested_start_time: datetime | None,
        exception_traceback: str | None,
    ) -> None:
        expected_var_types: dict[str, type | tuple[type, ...]] = {
            "id": JSONABLE_AS_TUPLE,
            "workflow_name": str,
            "status": JobStatus,
            "steps_completed": int,
            "percent_completed": int,
            "initial_input_value": JSONABLE_AS_TUPLE,
            "last_return_value": JSONABLE_AS_TUPLE,
            "requested_start_time": (datetime, type(None)),
            "exception_traceback": (str, type(None)),
        }

        for var_name, expected_type in expected_var_types.items():
            actual_value = locals()[var_name]
            if not isinstance(actual_value, expected_type):
                raise ValidationError(f'"{var_name}" is not of type {expected_type}')

        constraints = {
            "workflow_name": lambda x: x,
            "steps_completed": lambda x: x >= 0,
            "percent_completed": lambda x: 0 <= x <= 100,
        }

        for var_name, constraint in constraints.items():
            if not constraint(locals()[var_name]):
                raise ValidationError(f'"{var_name}" contains invalid data')

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

    def mark_completed(self, return_value: JSONABLE) -> None:
        self.status = JobStatus.COMPLETED
        self.percent_completed = 100
        self.last_return_value = return_value

    def mark_n_steps_completed(
        self,
        n: int,
        return_value: JSONABLE,
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

    def should_be_requeued(self) -> bool:
        return self.status not in (
            JobStatus.COMPLETED,
            JobStatus.FAILED,
        )

    def model_dump(
        self,
        include: set[str] | None = None,
        exclude: set[str] | None = None,
    ) -> dict[str, JSONABLE]:
        if include is not None and exclude is not None:
            raise ValueError("Cannot provide both include and exclude")

        dump_values = {
            "id": self.id,
            "workflow_name": self.workflow_name,
            "status": self.status,
            "steps_completed": self.steps_completed,
            "percent_completed": self.percent_completed,
            "initial_input_value": self.initial_input_value,
            "last_return_value": self.last_return_value,
            "requested_start_time": self.requested_start_time,
            "exception_traceback": self.exception_traceback,
        }

        if include is not None:
            dump_values = {k: v for k, v in dump_values.items() if k in include}

        if exclude is not None:
            dump_values = {k: v for k, v in dump_values.items() if k not in exclude}

        return dump_values

    def model_dump_json(
        self,
        include: set[str] | None,
        exclude: set[str] | None = None,
    ) -> str:
        return dumps(self.model_dump(include, exclude))
