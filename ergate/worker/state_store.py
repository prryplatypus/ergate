from typing import Protocol, TypeVar

from ..job import Job

JobType_contra = TypeVar("JobType_contra", bound=Job, contravariant=True)


class StateStoreProtocol(Protocol[JobType_contra]):
    def update(self, job: JobType_contra) -> None: ...
