from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import ExitStack, contextmanager
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from .depends_cache import DependsCache
from .job import Job

if TYPE_CHECKING:
    from .inspect import FunctionArgumentInfo

DependencyReturn = TypeVar("DependencyReturn")
JobType = TypeVar("JobType", bound=Job)


class Depends(Generic[DependencyReturn, JobType]):
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
        job: JobType,
        input_value: Any,
    ) -> Generator[DependencyReturn, None, None]:
        assert self.argument_info is not None, "Depends not initialized"

        if self.dependency in depends_cache:
            yield depends_cache[self.dependency]
            return

        args, kwargs = self.argument_info.build_args(
            stack,
            depends_cache,
            job,
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


class JobObject:
    pass
