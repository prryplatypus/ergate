from abc import ABC, abstractmethod
from typing import Generator, Generic, Type, TypeVar

FACTORY_MODEL = TypeVar("FACTORY_MODEL")


class Factory(ABC, Generic[FACTORY_MODEL]):
    __model__: Type[FACTORY_MODEL]

    @abstractmethod
    def create(self) -> Generator[FACTORY_MODEL, None, None]: ...
