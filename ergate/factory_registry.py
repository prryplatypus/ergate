from typing import Any, Type

from .factory import FACTORY_MODEL, Factory


class FactoryRegistry:
    def __init__(self) -> None:
        self._factories: dict[Type[Any], Factory[Any]] = {}

    def __getitem__(self, model: Type[FACTORY_MODEL]) -> Factory[FACTORY_MODEL]:
        try:
            return self._factories[model]
        except KeyError:
            raise KeyError(f'No factory registered for "{model.__name__}"')

    def register(self, factory: Factory[FACTORY_MODEL]) -> None:
        if factory.__model__ in self._factories:
            err = f'A factory for "{factory.__model__.__name__}" is already registered'
            raise ValueError(err)
        self._factories[factory.__model__] = factory
