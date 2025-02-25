from __future__ import annotations

from contextlib import ExitStack
from time import sleep
from typing import Generic, TypeVar

from ..interrupt import DelayedKeyboardInterrupt
from ..job import Job
from ..types import Lifespan
from .queue import PublisherQueueProtocol
from .state_store import PublisherStateStore

JobType = TypeVar("JobType", bound=Job)


class Publisher(Generic[JobType]):
    def __init__(
        self,
        queue: PublisherQueueProtocol[JobType],
        state_store: PublisherStateStore[JobType],
        lifespan: Lifespan[Publisher[JobType]] | None = None,
        poll_delay_seconds: float = 5.0,
    ) -> None:
        self.queue = queue
        self.state_store = state_store
        self.lifespan = lifespan
        self.poll_delay_seconds = poll_delay_seconds

    def _fetch_and_queue(self) -> None:
        jobs = self.state_store.fetch_many_and_transition_to_queued()
        if not jobs:
            return
        self.queue.put_many(jobs)

    def _run_loop(self) -> None:
        while True:
            with DelayedKeyboardInterrupt():
                self._fetch_and_queue()
            sleep(self.poll_delay_seconds)

    def run(self) -> None:
        with ExitStack() as stack:
            if self.lifespan:
                stack.enter_context(self.lifespan(self))
            self._run_loop()
