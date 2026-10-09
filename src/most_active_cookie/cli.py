"""Command-line interface for the most active cookie program."""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from .cookie_log_analysis import find_most_active_cookies, get_cookie_counts_on_date
from .cookie_log_reader import CookieLogError, read_cookie_log

DATE_FORMAT = "%Y-%m-%d"
DATE_PRESENTATION_FORMAT = "YYYY-MM-DD"


def _parse_command_date(date_string: str) -> date:
    """Parse the date parameter from a string to a date object."""
    try:
        parsed_date = datetime.strptime(date_string, DATE_FORMAT).date()

        if parsed_date.strftime(DATE_FORMAT) != date_string:
            raise ValueError("Date does not match required format")

        return parsed_date

    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date provided. Expected date format: "
            f"{DATE_PRESENTATION_FORMAT}, received: {date_string!r}"
        ) from None


def parse_command_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Initialise the parser and return the parsed arguments."""
    parser = argparse.ArgumentParser(description="Find the most active cookie for a specified day")

    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        required=True,
        help="Filepath for cookie log",
    )

    parser.add_argument(
        "-d",
        "--date",
        type=_parse_command_date,
        required=True,
        help=f"UTC date as {DATE_PRESENTATION_FORMAT}",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the most active cookie command."""
    args = parse_command_args(argv)

    try:
        cookie_records = read_cookie_log(args.file)
        cookie_counts = get_cookie_counts_on_date(cookie_records, args.date)
        most_active_cookies = find_most_active_cookies(cookie_counts)

    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    except IsADirectoryError:
        print(
            f"Error: expected a file, got a directory: {args.file}",
            file=sys.stderr,
        )
        return 1

    except PermissionError:
        if args.file.is_dir():
            print(
                f"Error: expected a file, got a directory: {args.file}",
                file=sys.stderr,
            )
        else:
            print(
                f"Error: permission denied when reading: {args.file}",
                file=sys.stderr,
            )
        return 1

    except OSError as exc:
        print(f"Error: unable to read {args.file}: {exc}", file=sys.stderr)
        return 1

    except UnicodeDecodeError:
        print(
            f"Error: {args.file} is not valid UTF-8 text",
            file=sys.stderr,
        )
        return 1

    except CookieLogError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for cookie in most_active_cookies:
        print(cookie)

    return 0
