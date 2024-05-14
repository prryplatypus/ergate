from typing import Callable, Iterator

from .constants import JSONABLE
from .workflow_step import WorkflowStep


class Workflow:
    def __init__(self, unique_name: str) -> None:
        self.unique_name = unique_name
        self._steps: list[WorkflowStep] = []

    def __getitem__(self, index: int) -> WorkflowStep:
        return self._steps[index]

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def step(self, callable: Callable[..., JSONABLE]) -> None:
        step = WorkflowStep(callable)
        self._steps.append(step)
        return step
