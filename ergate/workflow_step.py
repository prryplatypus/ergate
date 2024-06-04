from __future__ import annotations

import inspect
from contextlib import ExitStack
from typing import TYPE_CHECKING, Any, Callable

from .depends import DependsArgument
from .depends_cache import DependsCache
from .inspect import (
    validate_and_get_kwargs_defaults,
    validate_and_get_pos_args,
    validate_pos_or_kwrd_args,
)

if TYPE_CHECKING:
    from .workflow import Workflow


class WorkflowStep:
    def __init__(self, workflow: Workflow, callable: Callable[..., Any]) -> None:
        self.workflow = workflow
        self.callable = callable

        signature = inspect.signature(callable)
        validate_pos_or_kwrd_args(signature)

        input_arg = validate_and_get_pos_args(signature, allow_one=True)
        self._takes_input_arg = bool(input_arg)
        self._kwarg_factories = validate_and_get_kwargs_defaults(
            signature,
            DependsArgument,
        )

    @property
    def name(self) -> str:
        return self.callable.__name__

    def __call__(self, last_return_value: Any) -> Any:
        args = (last_return_value,) if self._takes_input_arg else ()

        depends_cache = DependsCache()
        with ExitStack() as stack:
            kwargs: dict[str, Any] = {
                name: stack.enter_context(depends.create(stack, depends_cache))
                for name, depends in self._kwarg_factories.items()
            }

            result = self.callable(*args, **kwargs)

        return result

    def __str__(self) -> str:
        return f"{self.workflow.unique_name}.{self.callable.__name__}"
