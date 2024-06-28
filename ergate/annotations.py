from __future__ import annotations

from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING, Any, Callable, Generator, Generic, TypeVar

from .depends_cache import DependsCache

if TYPE_CHECKING:
    from .inspect import FunctionArgumentInfo

DependencyReturn = TypeVar("DependencyReturn")


class Depends(Generic[DependencyReturn]):
    def __init__(
        self,
        dependency: Callable[..., Generator[DependencyReturn, None, None]],
    ) -> None:
        self.dependency = dependency
        self.argument_info: FunctionArgumentInfo | None = None

    def initialize(self, argument_info: FunctionArgumentInfo) -> None:
        self.argument_info = argument_info

    @contextmanager
    def create(
        self,
        stack: ExitStack,
        depends_cache: DependsCache,
        user_context: Any,
        input_value: Any,
    ) -> Generator[DependencyReturn, None, None]:
        assert self.argument_info is not None, "Depends not initialized"

        if self.dependency in depends_cache:
            yield depends_cache[self.dependency]
            return

        args, kwargs = self.argument_info.build_args(
            stack,
            depends_cache,
            user_context,
            input_value,
        )

        dependency_callable = contextmanager(self.dependency)
        dependency = stack.enter_context(dependency_callable(*args, **kwargs))
        depends_cache.set(self.dependency, dependency)

        yield dependency


class Input:
    pass


class Context:
    pass
