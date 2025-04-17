from collections import defaultdict
from logging import getLogger
from typing import Any, Callable, Generic

from ..types import JobType
from .enum import ErgateSignal

LOG = getLogger(__name__)
_HANDLER = Callable[[JobType], Any]


class SignalHandler(Generic[JobType]):
    def __init__(self) -> None:
        self._handlers: dict[ErgateSignal, list[_HANDLER]] = defaultdict(list)

    def register(self, signal: ErgateSignal, handler: _HANDLER) -> None:
        self._handlers[signal].append(handler)

    def trigger(self, signal: ErgateSignal, job: JobType) -> None:
        if signal not in self._handlers:
            return

        for handler in self._handlers[signal]:
            try:
                handler(job)
            except Exception:
                LOG.exception(
                    "Signal handler %s raised an exception - ignoring",
                    handler,
                )
