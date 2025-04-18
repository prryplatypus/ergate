from collections.abc import Callable
from typing import Any, ContextManager, TypeVar

from .annotations import Context, Depends, Input

AppType = TypeVar("AppType")
JobType = TypeVar("JobType")

Lifespan = Callable[[AppType], ContextManager[None]] | None

SignalHandler = Callable[[JobType], Any]

Annotation = Input | Depends | Context
