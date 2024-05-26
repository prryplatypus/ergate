from typing import Any


class DependsCache:
    def __init__(self) -> None:
        self._cache: dict[Any, Any] = {}

    def get(self, key: Any) -> Any:
        return self._cache.get(key)

    def set(self, key: Any, value: Any) -> None:
        self._cache[key] = value

    def delete(self, key: Any) -> None:
        self._cache.pop(key)
