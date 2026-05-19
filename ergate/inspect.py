import copy
from collections.abc import Callable
from contextlib import ExitStack
from inspect import Parameter
from inspect import signature as get_signature
from typing import Annotated, Any, Generic, TypeVar, get_args, get_origin

from .annotations import Context, Depends, Input, JobObject
from .depends_cache import DependsCache
from .job import Job
from .types import Annotation

JobType = TypeVar("JobType", bound=Job)


class FunctionArgumentInfo(Generic[JobType]):
    def __init__(self) -> None:
        self._args_types: list[Annotation] = []
        self._kwarg_types: dict[str, Annotation] = {}

    @property
    def args_types(self) -> list[Annotation]:
        return self._args_types

    @property
    def kwarg_types(self) -> dict[str, Annotation]:
        return self._kwarg_types

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
        job: JobType,
        input_value: Any,
    ) -> Any:
        if isinstance(type_, Input):
            return input_value

        if isinstance(type_, Depends):
            return stack.enter_context(
                type_.create(
                    stack,
                    depends_cache,
                    job,
                    input_value,
                )
            )

        if isinstance(type_, Context):
            return job.user_context

        if isinstance(type_, JobObject):
            return job

        raise ValueError(f"Unsupported annotation type: {type_}")

    def build_args(
        self,
        stack: ExitStack,
        depends_cache: DependsCache,
        job: JobType,
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
                    job,
                    input_value,
                )
            )

        for name, type_ in self._kwarg_types.items():
            kwargs[name] = self.build_type(
                type_,
                stack,
                depends_cache,
                job,
                input_value,
            )

        return args, kwargs


class Inspector(Generic[JobType]):
    @staticmethod
    def get_param_info(param: Parameter) -> Input | Depends | Context | JobObject:
        origin = get_origin(param.annotation)
        if origin is not Annotated:
            return Input()

        arguments = get_args(param.annotation)
        ergate_annotations = [
            argument
            for argument in arguments
            if isinstance(argument, (Input, Depends, Context, JobObject))
        ]

        if not ergate_annotations:
            return Input()

        if len(ergate_annotations) > 1:
            raise ValueError(
                "Parameter annotations must contain no more than one dependency "
                f"or one context marker ({param.name=})"
            )

        return ergate_annotations[0]

    @classmethod
    def build_function_arg_info(
        cls,
        function: Callable[..., Any],
    ) -> FunctionArgumentInfo[JobType]:
        signature = get_signature(function)
        function_wrapper: FunctionArgumentInfo[JobType] = FunctionArgumentInfo()

        for param in signature.parameters.values():
            param_info = cls.get_param_info(param)

            if isinstance(param_info, Depends):
                depends_copy = copy.copy(param_info)
                dependency_arg_info = cls.build_function_arg_info(
                    depends_copy.dependency
                )
                depends_copy.initialize(dependency_arg_info)
                param_info = depends_copy

            function_wrapper.add_param(param, param_info)

        return function_wrapper
