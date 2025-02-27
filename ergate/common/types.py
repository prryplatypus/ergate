from collections.abc import Callable
from typing import ContextManager, TypeVar

AppType = TypeVar("AppType")

Lifespan = Callable[[AppType], ContextManager[None]] | None
