from pydantic import ValidationError

__all__ = (
    "ErgateError",
    "ValidationError",
)


class ErgateError(Exception):
    """Base class for ergate exceptions."""
