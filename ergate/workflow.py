from typing import (
    Callable,
    Iterator,
    ParamSpec,
    TypeAlias,
    TypeVar,
    overload,
)

from .exceptions import ReverseGoToError, UnknownStepError
from .paths import GoToEndPath, GoToStepPath, NextStepPath, SkipNStepsPath, WorkflowPath
from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")
CallableTypeHint: TypeAlias = Callable[CallableSpec, CallableRetval]
WorkflowStepTypeHint: TypeAlias = WorkflowStep[CallableSpec, CallableRetval]
WorkflowPathTypeHint: TypeAlias = tuple[WorkflowPath, int]


class Workflow:
    def __init__(self, unique_name: str) -> None:
        self.unique_name = unique_name
        self._steps: list[WorkflowStep] = []
        self._paths: dict[int, list[list[WorkflowPathTypeHint]]] = {}

    def __getitem__(self, key: int) -> WorkflowStep:
        try:
            return self._steps[key]
        except IndexError:
            raise IndexError(
                f'Workflow "{self.unique_name}" has {len(self)} steps '
                f"- tried to access index {key}"
            ) from None

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    @property
    def paths(self):
        return self._paths

    def _calculate_paths(
        self,
        index: int,
        *,
        initial: bool = False,
        path: WorkflowPath | None = None,
    ) -> list[list[WorkflowPathTypeHint]]:
        paths: list[list[WorkflowPathTypeHint]] = []

        if not initial:
            if path is None:
                err = (
                    f"Failed to calculate workflow path from step {index}: "
                    f"path cannot be null."
                )
                raise ValueError(err)

            if path not in self[index].paths:
                err = (
                    f"Failed to calculate workflow path from step {index}: "
                    f"path not registered: {path}"
                )
                raise ValueError(err)

            next_index = self._find_next_step(index, path)

            if next_index <= index:
                raise ReverseGoToError(
                    "User attempted to go to an earlier step, "
                    "which is not permitted."
                )
        else:
            path = NextStepPath()
            next_index = index

        current_step = (path, index)

        if next_index >= len(self):
            paths.append([current_step])
            return paths

        for next_path in self[next_index].paths:
            paths += self._calculate_paths(next_index, path=next_path)

        if not initial:
            paths = [[current_step, *next_path] for next_path in paths]

        return paths

    def calculate_paths(self, index: int) -> list[list[WorkflowPathTypeHint]]:
        print(
            f"===411.1=== Calculating paths in workflow {self.unique_name} "
            f"from step {self[index].name} ({index})"
        )
        return self._calculate_paths(index, initial=True)

    def update_paths(self) -> None:
        self._paths = {step.index: self.calculate_paths(step.index) for step in self}

    def _find_next_step(self, index: int, path: WorkflowPath) -> int:
        if isinstance(path, GoToEndPath):
            return len(self)

        if isinstance(path, GoToStepPath):
            return self.get_step_index_by_name(path.step_name)

        if isinstance(path, SkipNStepsPath):
            return index + 1 + path.n

        return index + 1

    def get_step_index_by_name(self, step_name: str) -> int:
        try:
            return next(step.index for step in self if step.name == step_name)
        except StopIteration:
            raise UnknownStepError(
                f'No step named "{step_name}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    @overload
    def step(self, func: CallableTypeHint) -> WorkflowStepTypeHint: ...

    @overload
    def step(
        self,
        *,
        paths: list[WorkflowPath] | None = None,
    ) -> CallableTypeHint: ...

    def step(
        self,
        func: CallableTypeHint | None = None,
        *,
        paths: list[WorkflowPath] | None = None,
    ) -> CallableTypeHint | WorkflowStepTypeHint:
        def _decorate(func: CallableTypeHint) -> WorkflowStepTypeHint:
            step = WorkflowStep(self, func, len(self), paths=paths)
            self._steps.append(step)
            self.update_paths()
            return step

        if func is None:
            return _decorate

        return _decorate(func)
