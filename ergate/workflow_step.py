import inspect

from contextlib import ExitStack, contextmanager
from typing import Any, Callable, TypeVar

from .constants import JSONABLE
from .factory import Factory


T = TypeVar("T")


class WorkflowStep:
    def __init__(self, callable: Callable[..., JSONABLE]) -> None:
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

        raise ValueError(
            "Workflow steps can only have positional-only and/or "
            "keyword-only arguments"
        )

    def _check_and_get_takes_positional_arg(self, signature: inspect.Signature) -> bool:
        input_args = [
            param
            for param in signature.parameters.values()
            if param.kind == inspect.Parameter.POSITIONAL_ONLY
        ]

        input_args_qty = len(input_args)
        if input_args_qty > 1:
            raise ValueError("Workflow steps can only have 0 or 1 input arguments")

        return bool(input_args_qty)

    def _check_and_get_kwargs(self, signature: inspect.Signature) -> dict[str, Any]:
        kwargs = {
            param_name: param.annotation
            for param_name, param in signature.parameters.items()
            if param.kind == inspect.Parameter.KEYWORD_ONLY
        }

        if any(
            param.annotation == inspect.Parameter.empty for param in kwargs.values()
        ):
            raise ValueError("Workflow steps must have type annotations for all kwargs")

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

            return self.callable(*args, **kwargs)
