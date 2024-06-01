from typing import Protocol, TypeVar

from .job import Job

T = TypeVar("T", bound=Job, contravariant=True)
U = TypeVar("U", bound=Job)


class QueueWriteProtocol(Protocol[T]):
    def put(self, job: T) -> None: ...


class QueueProtocol(QueueWriteProtocol[U], Protocol[U]):
    def put(self, job: U) -> None: ...
    def get_one(self) -> U: ...
