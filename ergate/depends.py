from collections.abc import Callable
from typing import Any


class DependsArgument:
    def __init__(self, callable: Callable[[], Any]) -> None:
        self.callable = callable


def Depends(callable: Callable[[], Any]) -> Any:  # noqa: N802
    return DependsArgument(callable)
