from collections.abc import Callable
from typing import ContextManager, TypeVar

AppType = TypeVar("AppType")
JobType = TypeVar("JobType")

Lifespan = Callable[[AppType], ContextManager[None]] | None

ExceptionHook = Callable[[JobType, Exception], None]
