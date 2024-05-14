from typing import ClassVar, Generator, Generic, Type, TypeVar


FACTORY_MODEL = TypeVar("FACTORY_MODEL")


class Factory(Generic[FACTORY_MODEL]):
    __model__: ClassVar[Type[FACTORY_MODEL]]

    def create(cls) -> Generator[FACTORY_MODEL, None, None]: ...
