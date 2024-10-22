from typing import Callable, Iterator, ParamSpec, TypeVar, get_type_hints

from .exceptions import ErgateError, GoToEnd, GoToStep, SkipNSteps
from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")
WorkflowPath = tuple[ErgateError | None, int]


class Workflow:
    def __init__(self, unique_name: str) -> None:
        self.unique_name = unique_name
        self._steps: list[WorkflowStep] = []
        self._labels: dict[str, int] = {}

    def __getitem__(self, key: int | str) -> WorkflowStep:
        try:
            if isinstance(key, int):
                return self._steps[key]
            else:
                idx = self._labels[key]
                return self._steps[idx]
        except IndexError:
            raise IndexError(
                f'Workflow "{self.unique_name}" has {len(self)} steps '
                f"- tried to access step #{key}"
            ) from None
        except KeyError:
            raise KeyError(
                f'No label named "{key}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def __iter__(self) -> Iterator[WorkflowStep]:
        return iter(self._steps)

    def __len__(self) -> int:
        return len(self._steps)

    def _calculate_paths(
        self, idx: int, depth: int, *, exc: ErgateError | None = None, all: bool = False
    ) -> list[list[WorkflowPath]]:
        # TODO: better way of determining range for infinite loop detection.
        if depth >= max(len(self) * 5, 100):
            err = (
                "Aborting path calculation due to potential infinite loop: "
                f"(depth: {depth})"
            )
            raise RecursionError(err)

        if not all and exc not in self._steps[idx].paths:
            err = (
                f"Failed to calculate workflow path from step {idx}: "
                f"exception not supported: {exc}"
            )
            raise ValueError(err)

        current_step = (exc, idx)
        paths: list[list[WorkflowPath]] = []

        next_idx = idx if all else self._find_next_step(idx, exc)
        if next_idx >= len(self):
            paths.append([current_step])
            return paths

        for next_exc in self._steps[next_idx].paths:
            paths += self._calculate_paths(next_idx, depth + 1, exc=next_exc)

        if not all:
            paths = [[current_step, *next_path] for next_path in paths]

        return paths

    def calculate_paths(self, idx: int) -> list[list[WorkflowPath]]:
        return self._calculate_paths(idx, depth=0, all=True)

    def _find_next_step(self, idx: int, exc: ErgateError) -> int:
        if isinstance(exc, GoToEnd):
            return len(self)
        if isinstance(exc, GoToStep):
            if not exc.has_step:
                err = (
                    f"Failed to calculate workflow path from step {idx}: "
                    "No label or index provided for GoToStep."
                )
                raise ValueError(err)

            return exc.n if exc.n is not None else self.get_label_index(exc.label)
        if isinstance(exc, SkipNSteps):
            return idx + 1 + exc.n

        return idx + 1

    def get_label_index(self, label: str) -> int:
        try:
            return self._labels[label]
        except KeyError:
            raise KeyError(
                f'No label named "{label}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def step(
        self,
        func: Callable[CallableSpec, CallableRetval] | None = None,
        *,
        label: str = None,
        paths: list[ErgateError | None] | None = None,
    ) -> Callable[CallableSpec, CallableRetval]:
        def _decorate(
            func: Callable[CallableSpec, CallableRetval],
        ) -> WorkflowStep[CallableSpec, CallableRetval]:
            if label and label in self._labels:
                err = f'A workflow step with label "{label}" is already registered.'
                raise ValueError(err)

            step = WorkflowStep(self, func)

            if label:
                self._labels[label] = len(self)

            self._steps.append(step)

            if paths:
                step.paths = paths

            hints = get_type_hints(func)
            if not isinstance(None, hints["return"]) and None not in step.paths:
                step.paths.append(None)

            return step

        if func is None:
            return _decorate

        return _decorate(func)
