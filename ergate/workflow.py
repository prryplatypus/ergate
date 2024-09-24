from typing import Callable, Iterator, ParamSpec, TypeVar

from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")


class Workflow:
    def __init__(self, unique_name: str) -> None:
        self.unique_name = unique_name
        self._steps: list[WorkflowStep] = []

    def __getitem__(self, index: int) -> WorkflowStep:
        try:
            return self._steps[index]
        except IndexError:
            raise IndexError(
                f'Workflow "{self.unique_name}" has {len(self)} steps '
                f"- tried to access step #{index}"
            ) from None

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def step(
        self,
        callable: Callable[CallableSpec, CallableRetval],
    ) -> WorkflowStep[CallableSpec, CallableRetval]:
        step = WorkflowStep(self, callable)
        self._steps.append(step)
        return step
