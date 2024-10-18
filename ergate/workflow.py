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
        print("===211.1===", label)
        print("===212.1===", self._steps)
        print("===212.2===", self._labels)
        print("===211.2===", label in self._labels)

        try:
            return self._labels[label]
        except KeyError:
            raise KeyError(
                f'No label named "{label}" is registered in '
                f'Workflow "{self.unique_name}"'
            )

    def label(self, label: str) -> Callable[CallableSpec, CallableRetval]:
        def _decorate(
            func: Callable[CallableSpec, CallableRetval],
        ) -> Callable[CallableSpec, CallableRetval]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> WorkflowStep[CallableSpec, CallableRetval]:
                if label in self._labels:
                    err = (
                        f'A workflow step with label "{label}" '
                        "is already registered."
                    )
                    raise ValueError(err)

                result = func(*args, **kwargs)
                print("===111.1===", label)
                self._labels[label] = len(self._steps) - 1
                print("===111.2===", self._labels[label])

                print("===112.1===", self._steps)
                print("===112.2===", self._labels)
                return result

            return wrapper

        return _decorate

    def step(
        self, func: Callable[CallableSpec, CallableRetval]
    ) -> WorkflowStep[CallableSpec, CallableRetval]:
        step = WorkflowStep(self, func)
        self._steps.append(step)
        return step
