import inspect
from collections.abc import Callable
from contextlib import ExitStack, contextmanager
from typing import Any

from .inspect import (
    validate_and_get_kwargs_defaults,
    validate_and_get_pos_args,
    validate_pos_or_kwrd_args,
)


class DependsArgument:
    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency

        signature = inspect.signature(dependency)
        validate_pos_or_kwrd_args(signature)
        validate_and_get_pos_args(signature)
        self._kwarg_depends = validate_and_get_kwargs_defaults(
            signature,
            self.__class__,
        )

    def __call__(self, exit_stack: ExitStack) -> Any:
        if not self._kwarg_depends:
            return self.dependency()

        kwargs = {
            name: exit_stack.enter_context(contextmanager(depends)(exit_stack))
            for name, depends in self._kwarg_depends.items()
        }

        return self.dependency(**kwargs)


def Depends(dependency: Callable[[], Any]) -> Any:  # noqa: N802
    return DependsArgument(dependency)
