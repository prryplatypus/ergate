from .constants import JSONABLE, JSONABLE_AS_TUPLE
from .exceptions import ValidationError
from .job_status import JobStatus


class Job:
    def __init__(
        self,
        id: str,
        workflow_name: str,
        status: JobStatus = JobStatus.QUEUED,
        steps_completed: int = 0,
        percent_completed: int = 0,
        initial_input_value: JSONABLE = None,
        last_return_value: JSONABLE = None,
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
            exception_traceback,
        )

        self.id = id
        self.workflow_name = workflow_name
        self.status = status
        self.steps_completed = steps_completed
        self.percent_completed = percent_completed
        self.initial_input_value = initial_input_value
        self.last_return_value = last_return_value
        self.exception_traceback = exception_traceback

    def _validate_init_values(
        self,
        id: str,
        workflow_name: str,
        status: JobStatus = JobStatus.QUEUED,
        steps_completed: int = 0,
        percent_completed: int = 0,
        initial_input_value: JSONABLE = None,
        last_return_value: JSONABLE = None,
        exception_traceback: str | None = None,
    ) -> None:
        expected_var_types: dict[str, type | tuple[type, ...]] = {
            "id": str,
            "workflow_name": str,
            "status": JobStatus,
            "steps_completed": int,
            "percent_completed": int,
            "initial_input_value": JSONABLE_AS_TUPLE,
            "last_return_value": JSONABLE_AS_TUPLE,
            "exception_traceback": (str, type(None)),
        }

        for var_name, expected_type in expected_var_types.items():
            actual_value = locals()[var_name]
            if not isinstance(actual_value, expected_type):
                raise ValidationError(f'"{var_name}" is not of type {expected_type}')

        constraints = {
            "id": lambda x: x,
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
