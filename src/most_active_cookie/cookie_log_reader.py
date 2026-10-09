"""Read and validate cookie log CSV files."""

import csv
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

from .models import CookieRecord

EXPECTED_HEADER = ["cookie", "timestamp"]
NUM_COOKIE_LOG_FIELDS = len(EXPECTED_HEADER)


class CookieLogError(Exception):
    """Raised when the cookie log contains invalid data."""


def parse_log_row(row: list[str], row_num: int) -> CookieRecord:
    """Parse and validate a cookie log row."""
    if len(row) != NUM_COOKIE_LOG_FIELDS:
        raise CookieLogError(
            f"Expected {NUM_COOKIE_LOG_FIELDS} fields in cookie log. "
            f"Line {row_num} contains {len(row)} fields."
        )

    cookie, timestamp_value = row
    cookie = cookie.strip()
    timestamp_value = timestamp_value.strip()

    if not cookie:
        raise CookieLogError(f"Line {row_num}: missing cookie.")

    if not timestamp_value:
        raise CookieLogError(f"Line {row_num}: missing timestamp.")

    try:
        timestamp = datetime.fromisoformat(timestamp_value)
    except ValueError:
        raise CookieLogError(f"Line {row_num}: invalid timestamp {timestamp_value!r}") from None

    if timestamp.tzinfo is None:
        raise CookieLogError(f"Line {row_num}: timestamp must specify the timezone offset.")

    return CookieRecord(
        cookie=cookie,
        timestamp=timestamp.astimezone(timezone.utc),
    )


def read_cookie_log(filepath: Path) -> Iterator[CookieRecord]:
    """Lazily read and parse cookie records from a CSV file."""
    with filepath.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)

        header = next(reader, None)

        if header is None:
            raise CookieLogError("Cookie log file is empty.")

        header = [column.strip() for column in header]

        if header != EXPECTED_HEADER:
            raise CookieLogError(
                f"Cookie log header is invalid. Expected header {EXPECTED_HEADER!r}, "
                f"received {header!r}."
            )

        for row in reader:
            line_num = reader.line_num

            if not row:
                continue

            yield parse_log_row(row, line_num)
