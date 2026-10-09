"""Count cookie occurrences and identify the most active cookies."""

from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import date

from .models import CookieRecord


def get_cookie_counts_on_date(
    cookie_records: Iterable[CookieRecord],
    query_date: date,
) -> Counter[str]:
    """Return cookie occurrence counts for the requested UTC date."""
    cookie_counts: Counter[str] = Counter()

    for record in cookie_records:
        record_date = record.timestamp.date()

        if record_date == query_date:
            cookie_counts[record.cookie] += 1

        elif record_date < query_date:
            # Early stopping condition due to timestamp ordered log file.
            break

    return cookie_counts


def find_most_active_cookies(
    cookie_counts: Mapping[str, int],
) -> list[str]:
    """Return all cookies tied for the highest occurrence count."""
    if not cookie_counts:
        return []

    max_count = max(cookie_counts.values())

    return [cookie for cookie, count in cookie_counts.items() if count == max_count]
