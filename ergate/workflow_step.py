from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING, Any, Callable

from .depends_cache import DependsCache
from .inspect import build_function_arg_info

if TYPE_CHECKING:
    from .workflow import Workflow


class WorkflowStep:
    def __init__(self, workflow: Workflow, callable: Callable[..., Any]) -> None:
        self.workflow = workflow
        self.callable = callable
        self.arg_info = build_function_arg_info(callable)

    @property
    def name(self) -> str:
        return self.callable.__name__

    def __call__(self, last_return_value: Any, user_context: Any) -> Any:
        with ExitStack() as stack:
            args, kwargs = self.arg_info.build_args(
                stack,
                DependsCache(),
                user_context,
                last_return_value,
            )

            result = self.callable(*args, **kwargs)

        return result

    def __str__(self) -> str:
        return f"{self.workflow.unique_name}.{self.callable.__name__}"
