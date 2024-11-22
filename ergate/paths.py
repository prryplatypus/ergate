class WorkflowPath:
    """Base class for workflow paths."""


class GoToEndPath(WorkflowPath):
    """WorkflowPath class for the `GoToEnd` exception."""


class GoToStepPath(WorkflowPath):
    """WorkflowPath class for the `GoToStep` exception."""

    def __init__(self, value: int | str) -> None:
        self.value = value

    @property
    def is_index(self) -> bool:
        return isinstance(self.value, int)

    @property
    def n(self) -> int:
        assert isinstance(self.value, int)
        return self.value

    @property
    def is_step_name(self) -> bool:
        return isinstance(self.value, str)

    @property
    def step_name(self) -> str:
        assert isinstance(self.value, str)
        return self.value


class NextStepPath(WorkflowPath):
    """WorkflowPath class for the default `return` from function."""


class SkipNStepsPath(WorkflowPath):
    """WorkflowPath class for the `SkipNSteps` exception."""

    def __init__(self, n: int) -> None:
        self.n = n
