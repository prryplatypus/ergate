from contextlib import ExitStack
from inspect import Parameter
from inspect import signature as get_signature
from typing import Annotated, Any, Callable, get_args, get_origin

from .annotations import Context, Depends, Input
from .depends_cache import DependsCache
from .types import Annotation


class FunctionArgumentInfo:
    def __init__(self) -> None:
        self._args_types: list[Annotation] = []
        self._kwarg_types: dict[str, Annotation] = {}

    def add_param(self, param: Parameter, type_: Annotation) -> None:
        if param.kind == Parameter.POSITIONAL_ONLY:
            self._args_types.append(type_)
            return
        self._kwarg_types[param.name] = type_

    def build_type(
        self,
        type_: Annotation,
        stack: ExitStack,
        depends_cache: DependsCache,
        user_context: Any,
        input_value: Any,
    ) -> Any:
        if isinstance(type_, Input):
            return input_value

        if isinstance(type_, Depends):
            return stack.enter_context(
                type_.create(
                    stack,
                    depends_cache,
                    user_context,
                    input_value,
                )
            )

        assert isinstance(type_, Context)
        return user_context

    def build_args(
        self,
        stack: ExitStack,
        depends_cache: DependsCache,
        user_context: Any,
        input_value: Any,
    ) -> tuple[list[Any], dict[str, Any]]:
        args: list[Any] = []
        kwargs: dict[str, Any] = {}

        for type_ in self._args_types:
            args.append(
                self.build_type(
                    type_,
                    stack,
                    depends_cache,
                    user_context,
                    input_value,
                )
            )

        for name, type_ in self._kwarg_types.items():
            kwargs[name] = self.build_type(
                type_,
                stack,
                depends_cache,
                user_context,
                input_value,
            )

        return args, kwargs


def get_param_type(param: Parameter) -> Input | Depends | Context:
    origin = get_origin(param.annotation)
    if origin is not Annotated:
        return Input()

    args = get_args(param.annotation)

    dependencies = [arg for arg in args if isinstance(arg, Depends)]
    contexts = [arg for arg in args if isinstance(arg, Context)]

    if not dependencies and not contexts:
        return Input()

    if (dependencies and contexts) or len(dependencies) > 1 or len(contexts) > 1:
        raise ValueError(
            "Parameter annotations must contain no more than one dependency "
            f"or one context marker ({param.name=})"
        )

    if dependencies:
        return dependencies[0]

    assert contexts
    return contexts[0]


def build_function_arg_info(function: Callable[..., Any]) -> FunctionArgumentInfo:
    signature = get_signature(function)
    function_wrapper = FunctionArgumentInfo()

    for param in signature.parameters.values():
        param_type = get_param_type(param)
        function_wrapper.add_param(param, param_type)

        if isinstance(param_type, Depends):
            dependency_func_arg_info = build_function_arg_info(
                param_type.raw_dependency
            )
            param_type.initialize(dependency_func_arg_info)

    return function_wrapper
