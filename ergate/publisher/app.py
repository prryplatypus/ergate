from __future__ import annotations

from collections.abc import Generator
from contextlib import ExitStack
from typing import Generic, TypeVar

from ..job import Job
from ..types import Lifespan
from .protocols import PublisherDriverProtocol, PublisherQueueProtocol

JobType = TypeVar("JobType", bound=Job)


class ErgatePublisher(Generic[JobType]):
    """
    Publisher for jobs in the Ergate system.

    This class is responsible for fetching jobs that need publishing
    from the state store and publishing them to the queue.
    """

    def __init__(
        self,
        driver: PublisherDriverProtocol[JobType],
        queue: PublisherQueueProtocol[JobType],
        lifespan: Lifespan[ErgatePublisher[JobType]] | None = None,
    ) -> None:
        self.driver = driver
        self.queue = queue
        self.lifespan = lifespan

    def run(self) -> None:
        """
        Runs the publisher, fetching jobs from the state store and
        publishing them to the queue.

        This method will continue to fetch and publish jobs until
        there are no more jobs to process (`StopIteration` is raised
        from the state store), at which point it will exit gracefully.
        """

        with ExitStack() as stack:
            if self.lifespan:
                stack.enter_context(self.lifespan(self))

            generator = self.driver.generate_jobs()
            while True:
                try:
                    self._get_and_publish_next_job(generator)
                except StopIteration:
                    break

    def _get_and_publish_next_job(
        self,
        generator: Generator[JobType, None, None],
    ) -> None:
        """
        Fetches the next job from the generator and publishes it to the queue.
        If an exception occurs while publishing, it will be thrown back
        to the generator, allowing it to handle the exception appropriately.

        This method is intended to be called repeatedly until the generator
        raises `StopIteration`, indicating that there are no more jobs to process.
        """

        job = next(generator)

        try:
            self.queue.publish_job(job)
        except Exception as exc:
            generator.throw(exc)
