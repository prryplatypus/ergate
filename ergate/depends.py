import inspect
from collections.abc import Callable, Generator
from contextlib import ExitStack, contextmanager
from typing import Any, TypeVar

from .depends_cache import DependsCache
from .inspect import (
    validate_and_get_kwargs_defaults,
    validate_and_get_pos_args,
    validate_pos_or_kwrd_args,
)

T = TypeVar("T")


class DependsArgument:
    def __init__(self, dependency: Callable[..., Generator[T, None, None]]) -> None:
        self.dependency = dependency

        signature = inspect.signature(dependency)
        validate_pos_or_kwrd_args(signature)
        validate_and_get_pos_args(signature)
        self._kwarg_depends = validate_and_get_kwargs_defaults(
            signature,
            self.__class__,
        )

    @contextmanager
    def create(self, stack: ExitStack, cache: DependsCache) -> Generator[T, None, None]:
        cached_dependency = cache.get(self.dependency)
        if cached_dependency is not None:
            yield cached_dependency
            return

        kwargs: dict[str, Any] = {
            name: stack.enter_context(depends.create(stack, cache))
            for name, depends in self._kwarg_depends.items()
        }

        dependency = stack.enter_context(contextmanager(self.dependency)(**kwargs))
        cache.set(self.dependency, dependency)
        yield dependency
        cache.delete(self.dependency)


def Depends(dependency: Callable[..., Generator[Any, None, None]]) -> Any:  # noqa: N802
    return DependsArgument(dependency)
