from collections.abc import Callable
from contextlib import ExitStack, contextmanager
from typing import Any


class DependsCache:
    def __init__(self, exit_stack: ExitStack):
        self.exit_stack = exit_stack
        self._cache: dict = {}

    @contextmanager
    def get_or_create(self, callable_: Callable[..., Any]):
        if callable_ in self._cache:
            yield self._cache[callable_]
            return

        item = self.exit_stack.enter_context(
            contextmanager(callable_)(self.exit_stack, self)
        )
        self._cache[callable_] = item

        try:
            yield item
        finally:
            self._cache.pop(callable_)
