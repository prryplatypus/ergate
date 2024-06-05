import inspect
from typing import Type, TypeVar

from .exceptions import InvalidDefinitionError

T = TypeVar("T")


def validate_and_get_pos_or_kwrd_args(
    signature: inspect.Signature,
    allow_one: bool = False,
) -> inspect.Parameter | None:
    positional_or_keyword = [
        param
        for param in signature.parameters.values()
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]

    if not positional_or_keyword:
        return None

    if not allow_one:
        raise InvalidDefinitionError(
            "Arguments that are both positional and keyword are not "
            "allowed. All arguments must be explicitly defined as "
            "positional-only or keyword-only."
        )

    if len(positional_or_keyword) > 1:
        raise InvalidDefinitionError(
            "Only one argument that can be both positional or keyword is allowed."
        )

    return positional_or_keyword[0]


def validate_and_get_pos_args(
    signature: inspect.Signature,
    allow_one: bool = False,
) -> inspect.Parameter | None:
    args = [
        param
        for param in signature.parameters.values()
        if param.kind == inspect.Parameter.POSITIONAL_ONLY
    ]

    if not args:
        return None

    if not allow_one:
        raise InvalidDefinitionError("Positional arguments are not allowed.")

    if len(args) > 1:
        raise InvalidDefinitionError("Only one positional argument is allowed.")

    return args[0]


def validate_and_get_kwargs_defaults(
    signature: inspect.Signature,
    dependency_type: Type[T],
) -> dict[str, T]:
    kwargs_depends: dict[str, T] = {}

    kwargs = (
        (param_name, param)
        for param_name, param in signature.parameters.items()
        if param.kind == inspect.Parameter.KEYWORD_ONLY
    )

    for param_name, param in kwargs:
        if param.annotation == inspect.Parameter.empty:
            raise InvalidDefinitionError(
                f'Keyword argument "{param_name}" is missing a type annotation'
            )

        if not isinstance(param.default, dependency_type):
            raise InvalidDefinitionError(
                f'Keyword argument "{param_name}" is missing a dependency'
            )

        kwargs_depends[param_name] = param.default

    return kwargs_depends
