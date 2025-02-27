from typing import Any


class DependsCache:
    def __init__(self) -> None:
        self._cache: dict[Any, Any] = {}

    def __contains__(self, key: Any) -> bool:
        return key in self._cache

    def __getitem__(self, key: Any) -> Any:
        return self._cache[key]

    def set(self, key: Any, value: Any) -> None:
        self._cache[key] = value
