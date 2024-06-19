from collections.abc import Callable
from typing import ContextManager, TypeVar

from .annotations import Context, Depends, Input

AppType = TypeVar("AppType")
JobType = TypeVar("JobType")

Lifespan = Callable[[AppType], ContextManager[None]] | None

ExceptionHook = Callable[[JobType, Exception], None]

Annotation = Input | Depends | Context
