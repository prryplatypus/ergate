from .constants import JSONABLE


class ErgateError(Exception):
    """Base class for ergate exceptions."""


class InvalidDefinitionError(ErgateError):
    """Raised when a workflow/step definition is invalid."""


class CompleteJob(ErgateError):  # noqa: N818
    """Raised from a step to complete a workflow early."""

    def __init__(self, retval: JSONABLE = None):
        self.retval = retval


class SkipNSteps(ErgateError):  # noqa: N818
    """Raised from a step to skip N steps."""

    def __init__(self, n: int, retval: JSONABLE = None):
        self.n = n
        self.retval = retval


class ValidationError(ErgateError):
    """Raised when a value violates a schema."""
