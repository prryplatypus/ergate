from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any, TypeVar

from .annotations import Context, Depends, Input, JobObject

AppType = TypeVar("AppType")
JobType = TypeVar("JobType")

Lifespan = Callable[[AppType], AbstractContextManager[None]] | None

SignalHandler = Callable[[JobType], Any]

Annotation = Input | Depends | Context | JobObject
