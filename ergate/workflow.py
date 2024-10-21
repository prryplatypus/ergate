from typing import Callable, Iterator, ParamSpec, TypeVar

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
        print("===211.11===", idx, all, depth, exc)
        if depth > max(len(self) * 5, 100):
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

        paths: list[list[WorkflowPath]] = []

        next_idx = idx if all else self._find_next_step(idx, exc)
        print("===211.12===", next_idx)
        if next_idx >= len(self):
            print("===211.2===", paths)
            return paths

        for next_exc in self._steps[next_idx].paths:
            for next_path in self._calculate_paths(next_idx, depth + 1, exc=next_exc):
                paths.append([(next_exc, next_idx), *next_path])

        print("===211.3===", paths)
        return paths

    def calculate_paths(self, idx: int) -> list[list[WorkflowPath]]:
        ret = self._calculate_paths(idx, depth=0, all=True)
        print("===111.1===", len(ret))
        for i, path in enumerate(ret):
            print("===111.2.{i}===", path)
        return ret

    def _find_next_step(self, idx: int, exc: ErgateError) -> int:
        print("===411.1===", idx, exc)
        if isinstance(exc, GoToEnd):
            print("===411.2===", len(self))
            return len(self)
        if isinstance(exc, GoToStep):
            print("===411.31===")
            if not exc.has_step:
                err = (
                    f"Failed to calculate workflow path from step {idx}: "
                    "No label or index provided for GoToStep."
                )
                raise ValueError(err)

            print(
                "===411.32===",
                exc.next_step,
                exc.n if exc.n is not None else self.get_label_index(exc.label),
            )
            return exc.n if exc.n is not None else self.get_label_index(exc.label)
        if isinstance(exc, SkipNSteps):
            print("===411.4===", idx + 1 + exc.n)
            return idx + 1 + exc.n

        print("===411.5===", idx + 1)
        return idx + 1

    def get_label_index(self, label: str) -> int:
        try:
            return self._labels[label]
        except KeyError:
            raise KeyError(
                f'No label named "{label}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def paths(
        self, paths: list[ErgateError | None] | None = None
    ) -> Callable[CallableSpec, CallableRetval]:
        def _decorate(
            func: WorkflowStep[CallableSpec, CallableRetval],
        ) -> WorkflowStep[CallableSpec, CallableRetval]:
            if not isinstance(func, WorkflowStep):
                # This guard clause isn't strictly necessary with the type hints.
                # It is included as a helpful hint to the developer.
                err = (
                    "@label decorator method must be called on a WorkflowStep.  "
                    "Did you remember to invoke @step first?"
                )
                raise ValueError(err)

            func.paths = paths

            return func

        return _decorate

    def label(self, label: str) -> Callable[CallableSpec, CallableRetval]:
        def _decorate(
            func: WorkflowStep[CallableSpec, CallableRetval],
        ) -> WorkflowStep[CallableSpec, CallableRetval]:
            if not isinstance(func, WorkflowStep):
                # This guard clause isn't strictly necessary with the type hints.
                # It is included as a helpful hint to the developer.
                err = (
                    "@label decorator method must be called on a WorkflowStep.  "
                    "Did you remember to invoke @step first?"
                )
                raise ValueError(err)

            if label in self._labels:
                err = f'A workflow step with label "{label}" is already registered.'
                raise ValueError(err)

            self._labels[label] = len(self) - 1

            return func

        return _decorate

    def step(
        self, func: Callable[CallableSpec, CallableRetval]
    ) -> WorkflowStep[CallableSpec, CallableRetval]:
        step = WorkflowStep(self, func)
        self._steps.append(step)
        return step
