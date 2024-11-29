class WorkflowPath:
    """Base class for workflow paths."""


class GoToEndPath(WorkflowPath):
    """WorkflowPath class for the `GoToEnd` exception."""


class GoToStepPath(WorkflowPath):
    """WorkflowPath class for the `GoToStep` exception."""

    def __init__(self, step_name: str) -> None:
        self.step_name = step_name


class NextStepPath(WorkflowPath):
    """WorkflowPath class for the default `return` from function."""
