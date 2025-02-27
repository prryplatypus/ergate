import argparse
import re

_APP_LOCATION_FORMAT = re.compile(r"^[a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)*:[a-zA-Z0-9_]+$")


def _parse_app_location(arg: str) -> str:
    if not _APP_LOCATION_FORMAT.match(arg):
        raise argparse.ArgumentTypeError(f"Invalid app location: {arg}")
    return arg


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ergate run
    run_parser = subparsers.add_parser("run", help="Run an application")

    # ergate run worker|publisher [location]
    run_subparsers = run_parser.add_subparsers(dest="app", required=True)
    for parser_name in ("worker", "publisher"):
        run_subparsers.add_parser(
            parser_name,
            help=f"Run a {parser_name}",
        ).add_argument(
            "app_location",
            type=_parse_app_location,
            help=f"Location of the {parser_name} (e.g. 'my.module:app')",
        )

    return parser
