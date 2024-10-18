import functools
from typing import Callable, Iterator, ParamSpec, TypeVar

from .workflow_step import WorkflowStep

CallableSpec = ParamSpec("CallableSpec")
CallableRetval = TypeVar("CallableRetval")


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

    def get_label_index(self, label: str) -> int:
        return self._labels[label]

    def step(self, *args):
        if callable(args[0]):
            label = None
        elif isinstance(args[0], str):
            label = args[0]
        else:
            err = f"A workflow step label must be a string value."
            raise ValueError(err)

        def _decorate(
            func: Callable[CallableSpec, CallableRetval],
        ) -> Callable[CallableSpec, CallableRetval]:
            @functools.wraps(func)
            def wrapper() -> WorkflowStep[CallableSpec, CallableRetval]:
                step = WorkflowStep(self, func)
                self._steps.append(step)

                if label:
                    if label in self._labels:
                        err = (
                            f'A workflow step with label "{label}" '
                            "is already registered."
                        )
                        raise ValueError(err)
                    idx = len(self._steps) - 1
                    self._labels[label] = idx

                return step

            return wrapper

        if len(args) == 1 and callable(args[0]):
            return _decorate(args[0])

        return _decorate
