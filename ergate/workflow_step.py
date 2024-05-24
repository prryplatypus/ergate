from __future__ import annotations

import inspect
from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING, Callable

from .constants import JSONABLE
from .depends import DependsArgument
from .exceptions import InvalidDefinitionError

if TYPE_CHECKING:
    from .workflow import Workflow


class WorkflowStep:
    def __init__(self, workflow: Workflow, callable: Callable[..., JSONABLE]) -> None:
        self.workflow = workflow
        self.callable = callable

        signature = inspect.signature(callable)

        self._validate_pos_or_kwrd_args(signature)
        self._takes_input_arg = self._validate_and_get_positional_arg(signature)
        self._kwarg_factories: dict[str, DependsArgument] = (
            self._validate_and_get_kwargs(signature)
        )

    def _validate_pos_or_kwrd_args(self, signature: inspect.Signature) -> None:
        positional_or_keyword = [
            param
            for param in signature.parameters.values()
            if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        ]

        if not positional_or_keyword:
            return

        raise InvalidDefinitionError(
            f"{self} has arguments that are accepted as both positional "
            "and keyword arguments. All arguments must be explicitly "
            "defined as positional-only or keyword-only."
        )

    def _validate_and_get_positional_arg(self, signature: inspect.Signature) -> bool:
        args = [
            param
            for param in signature.parameters.values()
            if param.kind == inspect.Parameter.POSITIONAL_ONLY
        ]

        if not args:
            return False

        if len(args) > 1:
            raise InvalidDefinitionError(
                f"{self} takes more than one positional argument "
                "- it must only take one"
            )

        arg = args[0]
        if args[0].annotation == inspect.Parameter.empty:
            raise InvalidDefinitionError(
                f'Positional argument "{arg.name}" in {self} is missing a '
                "type annotation"
            )

        return True

    def _validate_and_get_kwargs(
        self, signature: inspect.Signature
    ) -> dict[str, DependsArgument]:
        kwargs_depends: dict[str, DependsArgument] = {}
        kwargs = (
            (param_name, param)
            for param_name, param in signature.parameters.items()
            if param.kind == inspect.Parameter.KEYWORD_ONLY
        )

        for param_name, param in kwargs:
            if not isinstance(param.default, DependsArgument):
                raise InvalidDefinitionError(
                    f'Keyword argument "{param_name}" in {self} is missing '
                    "a Depends(...)"
                )

            if param.annotation == inspect.Parameter.empty:
                raise InvalidDefinitionError(
                    f'Keyword argument "{param_name}" in {self} is missing '
                    "a type annotation"
                )

            kwargs_depends[param_name] = param.default

        return kwargs_depends

    def __call__(self, last_return_value: JSONABLE) -> JSONABLE:
        args = (last_return_value,) if self._takes_input_arg else ()

        with ExitStack() as stack:
            kwargs = {
                name: stack.enter_context(contextmanager(depends.callable)())
                for name, depends in self._kwarg_factories.items()
            }

            result = self.callable(*args, **kwargs)

        return result

    def __str__(self) -> str:
        return f"{self.workflow.unique_name}.{self.callable.__name__}"
