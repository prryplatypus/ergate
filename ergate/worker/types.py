from collections.abc import Callable
from typing import TypeVar

from .annotations import Context, Depends, Input

AppType = TypeVar("AppType")
Annotation = Input | Depends | Context

JobType = TypeVar("JobType")
ExceptionHook = Callable[[JobType, Exception], None]
