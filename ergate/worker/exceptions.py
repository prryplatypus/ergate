from typing import Any

from ..common.exceptions import ErgateError
from .workflow_step import WorkflowStep


class ReverseGoToError(ErgateError):
    """Raised when a workflow/step attempts to `go to` an earlier step."""


class UnknownStepError(ErgateError):
    """Raised when a workflow/step attempts to `go to` an unknown step."""


class AbortJob(ErgateError):  # noqa: N818
    """Raised from a step to abort a workflow.
    Should be interpreted as an expected failure.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class GoToEnd(ErgateError):  # noqa: N818
    """Raised from a step to immediately complete the job."""

    def __init__(self, retval: Any = None) -> None:
        self.retval = retval


class GoToStep(ErgateError):  # noqa: N818
    """Raised from a step to go to a specific step by its index or string label."""

    def __init__(self, step: WorkflowStep, *, retval: Any = None) -> None:
        self.retval = retval
        self.step = step
