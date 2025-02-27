import importlib
from typing import Any

from ..publisher.app import Publisher
from ..worker.app import Worker
from .parser import create_parser


def _import_object(location: str) -> Any:
    modname, qualname = location.split(":", 1)

    try:
        obj = importlib.import_module(modname)
    except ImportError:
        raise ValueError(f"Module '{modname}' could not be imported") from None

    try:
        return getattr(obj, qualname)
    except AttributeError:
        raise ValueError(f"No object '{qualname}' found in '{modname}'") from None


def run() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "run":
        object = _import_object(args.app_location)

        expected_type = Worker if args.app == "worker" else Publisher
        if not isinstance(object, expected_type):
            raise ValueError(f"Given object is not of {expected_type.__name__} type")

        object.run()
