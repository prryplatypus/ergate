from types import NoneType
from typing import (
    Callable,
    Iterator,
    ParamSpec,
    TypeAlias,
    TypeVar,
    get_type_hints,
    overload,
)

from .exceptions import ReverseGoToError, UnknownStepNameError
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
        self._step_names: dict[str, int] = {}

    def __getitem__(self, key: int | str) -> WorkflowStep:
        try:
            index = self.get_index_by_step_name(key) if isinstance(key, str) else key
            return self._steps[index]
        except IndexError:
            raise IndexError(
                f'Workflow "{self.unique_name}" has {len(self)} steps '
                f"- tried to access step #{key}"
            ) from None

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def _calculate_paths(
        self,
        index: int,
        depth: int,
        *,
        initial: bool = False,
        path: WorkflowPath | None = None,
    ) -> list[list[WorkflowPathTypeHint]]:
        # TODO: better way of determining range for infinite loop detection.
        if depth >= max(len(self) * 5, 100):
            err = (
                "Aborting path calculation due to potential infinite loop: "
                f"(depth: {depth})"
            )
            raise RecursionError(err)

        if not initial and path not in self._steps[index].paths:
            err = (
                f"Failed to calculate workflow path from step {index}: "
                f"exception not supported: {path}"
            )
            raise ValueError(err)

        current_step = (path, index)
        paths: list[list[WorkflowPathTypeHint]] = []

        next_index = index if initial else self._find_next_step(index, path)
        if next_index >= len(self):
            paths.append([current_step])
            return paths

        for next_path in self._steps[next_index].paths:
            paths += self._calculate_paths(next_index, depth + 1, path=next_path)

        if not initial:
            paths = [[current_step, *next_path] for next_path in paths]

        return paths

    def calculate_paths(self, index: int) -> list[list[WorkflowPathTypeHint]]:
        return self._calculate_paths(index, depth=0, initial=True)

    def _find_next_step(self, index: int, path: WorkflowPath | None) -> int:
        if isinstance(path, GoToEndPath):
            return len(self)

        if isinstance(path, GoToStepPath):
            return path.n if path.is_index else self.get_index_by_step_name(path.step_name)

        if isinstance(path, SkipNStepsPath):
            return index + 1 + path.n

        return index + 1

    def get_index_by_step_name(self, step_name: str) -> int:
        try:
            return self._step_names[step_name]
        except KeyError:
            raise UnknownStepNameError(
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
            step = WorkflowStep(self, func)

            self._step_names[step.name] = len(self)

            self._steps.append(step)

            if paths:
                step.paths = paths

            hints = get_type_hints(func)
            if hints["return"] is not NoneType and not any(
                isinstance(path, NextStepPath) for path in step.paths
            ):
                step.paths.append(NextStepPath())

            return step

        if func is None:
            return _decorate

        return _decorate(func)
