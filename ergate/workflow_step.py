from __future__ import annotations

import inspect
from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from .constants import JSONABLE
from .exceptions import InvalidDefinitionError
from .factory import Factory

if TYPE_CHECKING:
    from .workflow import Workflow


T = TypeVar("T")


class WorkflowStep:
    def __init__(self, workflow: Workflow, callable: Callable[..., JSONABLE]) -> None:
        self.workflow = workflow
        self.callable = callable

        self._initialized = False
        self._takes_input_arg = False
        self._kwarg_factories: dict[str, Factory] = {}

    def check_and_get_argument_info(self) -> tuple[bool, dict[str, Any]]:
        signature = inspect.signature(self.callable)
        self._check_positional_or_keyword_args(signature)
        takes_input_arg = self._check_and_get_takes_positional_arg(signature)
        kwargs = self._check_and_get_kwargs(signature)
        return takes_input_arg, kwargs

    def initialize(
        self,
        takes_input_arg: bool,
        kwarg_factories: dict[str, Factory],
    ) -> None:
        self._takes_input_arg = takes_input_arg
        self._kwarg_factories = kwarg_factories
        self._initialized = True

    def _check_positional_or_keyword_args(self, signature: inspect.Signature) -> None:
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

    def _check_and_get_takes_positional_arg(self, signature: inspect.Signature) -> bool:
        input_args = [
            param
            for param in signature.parameters.values()
            if param.kind == inspect.Parameter.POSITIONAL_ONLY
        ]

        input_args_qty = len(input_args)
        if input_args_qty > 1:
            raise InvalidDefinitionError(
                f"{self} takes more than one input argument. It must only take one."
            )

        return bool(input_args_qty)

    def _check_and_get_kwargs(self, signature: inspect.Signature) -> dict[str, Any]:
        kwargs = {
            param_name: param.annotation
            for param_name, param in signature.parameters.items()
            if param.kind == inspect.Parameter.KEYWORD_ONLY
        }

        if any(
            param_annotation == inspect.Parameter.empty
            for param_annotation in kwargs.values()
        ):
            raise InvalidDefinitionError(
                f"{self} has keyword arguments with no type annotations. "
                "All keyword arguments must be properly typed."
            )

        return kwargs

    def __call__(self, last_return_value: JSONABLE) -> JSONABLE:
        if not self._initialized:
            raise ValueError(
                f"{self.__class__.__name__} must be initialized before calling"
            )

        args = (last_return_value,) if self._takes_input_arg else ()

        with ExitStack() as stack:
            kwargs = {
                name: stack.enter_context(contextmanager(factory.create)())
                for name, factory in self._kwarg_factories.items()
            }

            result = self.callable(*args, **kwargs)

        return result

    def __str__(self) -> str:
        return f"{self.workflow.unique_name}.{self.callable.__name__}"
