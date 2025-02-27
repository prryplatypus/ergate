from typing import Any, Generic, TypeVar

from ..common.job import Job
from ..common.log import LOG
from .types import ExceptionHook

JobType = TypeVar("JobType", bound=Job)


class ErrorHookHandler(Generic[JobType]):
    def __init__(self) -> None:
        self._hooks: dict[Any, ExceptionHook[JobType]] = {}

    def register(
        self,
        exception: type[Exception],
        hook: ExceptionHook[JobType],
    ) -> None:
        self._hooks[exception] = hook

    def get_hook(self, exception: Exception) -> ExceptionHook[JobType] | None:
        for cls in type(exception).__mro__:
            if cls in self._hooks:
                return self._hooks[cls]
        return None

    def notify(self, job: JobType, exception: Exception) -> None:
        hook = self.get_hook(exception)
        if not hook:
            return

        try:
            hook(job, exception)
        except Exception:
            LOG.warning("Error hook raised an exception", exc_info=True)
