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

from .exceptions import ErgateError, GoToEnd, GoToStep, SkipNSteps
from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")
CallableTypeHint: TypeAlias = Callable[CallableSpec, CallableRetval]
WorkflowStepTypeHint: TypeAlias = WorkflowStep[CallableSpec, CallableRetval]
WorkflowPathTypeHint: TypeAlias = tuple[ErgateError | None, int]


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
        all: bool = False,
        exc: ErgateError | None = None,
    ) -> list[list[WorkflowPathTypeHint]]:
        # TODO: better way of determining range for infinite loop detection.
        if depth >= max(len(self) * 5, 100):
            err = (
                "Aborting path calculation due to potential infinite loop: "
                f"(depth: {depth})"
            )
            raise RecursionError(err)

        if not all and exc not in self._steps[index].paths:
            err = (
                f"Failed to calculate workflow path from step {index}: "
                f"exception not supported: {exc}"
            )
            raise ValueError(err)

        current_step = (exc, index)
        paths: list[list[WorkflowPathTypeHint]] = []

        next_index = index if all else self._find_next_step(index, exc)
        if next_index >= len(self):
            paths.append([current_step])
            return paths

        for next_exc in self._steps[next_index].paths:
            paths += self._calculate_paths(next_index, depth + 1, exc=next_exc)

        if not all:
            paths = [[current_step, *next_path] for next_path in paths]

        return paths

    def calculate_paths(self, index: int) -> list[list[WorkflowPathTypeHint]]:
        return self._calculate_paths(index, depth=0, all=True)

    def _find_next_step(self, index: int, exc: ErgateError | None) -> int:
        if isinstance(exc, GoToEnd):
            return len(self)

        if isinstance(exc, GoToStep):
            return self.get_index_by_step_name(exc.step_name) if exc.is_step_name else exc.n

        if isinstance(exc, SkipNSteps):
            return index + 1 + exc.n

        return index + 1

    def get_index_by_step_name(self, step_name: str) -> int:
        try:
            return self._step_names[step_name]
        except KeyError:
            raise KeyError(
                f'No step named "{step_name}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    @overload
    def step(self, func: CallableTypeHint) -> WorkflowStepTypeHint: ...

    @overload
    def step(
        self,
        *,
        paths: list[ErgateError | None] | None = None,
    ) -> CallableTypeHint: ...

    def step(
        self,
        func: CallableTypeHint | None = None,
        *,
        paths: list[ErgateError | None] | None = None,
    ) -> CallableTypeHint | WorkflowStepTypeHint:
        def _decorate(func: CallableTypeHint) -> WorkflowStepTypeHint:
            step = WorkflowStep(self, func)

            self._step_names[step.name] = len(self)

            self._steps.append(step)

            if paths:
                step.paths = paths

            hints = get_type_hints(func)
            if hints["return"] is not NoneType and None not in step.paths:
                step.paths.append(None)

            return step

        if func is None:
            return _decorate

        return _decorate(func)
