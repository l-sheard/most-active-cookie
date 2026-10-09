"""Tests for cookie log analysis, including occurrence counts and most active cookies."""

from collections import Counter
from datetime import date, datetime, timezone

from most_active_cookie.cookie_log_analysis import (
    find_most_active_cookies,
    get_cookie_counts_on_date,
)
from most_active_cookie.models import CookieRecord

# Test find_most_active_cookies


def test_find_most_active_cookie():
    cookie_counts = Counter(
        {
            "cookie-a": 3,
            "cookie-b": 1,
            "cookie-c": 2,
        }
    )

    result = find_most_active_cookies(cookie_counts)

    assert result == ["cookie-a"]


def test_find_most_active_cookies_with_tie():
    cookie_counts = Counter(
        {
            "cookie-a": 3,
            "cookie-b": 3,
            "cookie-c": 1,
        }
    )

    result = find_most_active_cookies(cookie_counts)

    assert result == ["cookie-a", "cookie-b"]


def test_find_most_active_cookies_with_no_counts():
    cookie_counts = Counter()

    result = find_most_active_cookies(cookie_counts)

    assert result == []


# Test get_cookie_counts_on_date


def test_get_cookie_counts_on_date():
    cookie_records = [
        CookieRecord("cookie-a", datetime(2025, 12, 9, tzinfo=timezone.utc)),
        CookieRecord("cookie-a", datetime(2025, 12, 9, tzinfo=timezone.utc)),
        CookieRecord("cookie-b", datetime(2025, 12, 9, tzinfo=timezone.utc)),
        CookieRecord("cookie-c", datetime(2025, 12, 8, tzinfo=timezone.utc)),
    ]

    query_date = date(2025, 12, 9)
    result = get_cookie_counts_on_date(cookie_records, query_date)

    assert result == Counter({"cookie-a": 2, "cookie-b": 1})


def test_get_cookie_counts_on_date_with_no_matches():
    cookie_records = [
        CookieRecord("cookie-a", datetime(2025, 12, 8, tzinfo=timezone.utc)),
        CookieRecord("cookie-c", datetime(2025, 12, 8, tzinfo=timezone.utc)),
    ]

    query_date = date(2025, 12, 9)
    result = get_cookie_counts_on_date(cookie_records, query_date)

    assert result == Counter()


def test_get_cookie_counts_on_date_with_no_records():
    cookie_records = []
    query_date = date(2025, 12, 9)

    result = get_cookie_counts_on_date(cookie_records, query_date)

    assert result == Counter()


def test_get_cookie_counts_on_date_at_utc_boundaries():
    cookie_records = [
        CookieRecord(
            "cookie-a",
            datetime(2018, 12, 10, 0, 0, 0, tzinfo=timezone.utc),
        ),
        CookieRecord(
            "cookie-b",
            datetime(2018, 12, 9, 23, 59, 59, tzinfo=timezone.utc),
        ),
        CookieRecord(
            "cookie-c",
            datetime(2018, 12, 9, 0, 0, 0, tzinfo=timezone.utc),
        ),
        CookieRecord(
            "cookie-d",
            datetime(2018, 12, 8, 23, 59, 59, tzinfo=timezone.utc),
        ),
    ]

    query_date = date(2018, 12, 9)

    result = get_cookie_counts_on_date(cookie_records, query_date)

    assert result == Counter(
        {
            "cookie-b": 1,
            "cookie-c": 1,
        }
    )


def test_get_cookie_counts_on_date_stops_at_earlier_date():
    cookie_records = [
        CookieRecord("cookie-a", datetime(2018, 12, 9, tzinfo=timezone.utc)),
        CookieRecord("cookie-b", datetime(2018, 12, 8, tzinfo=timezone.utc)),
        # Out of order on purpose: never reached if iteration stops early
        CookieRecord("cookie-c", datetime(2018, 12, 9, tzinfo=timezone.utc)),
    ]

    result = get_cookie_counts_on_date(cookie_records, date(2018, 12, 9))

    assert result == Counter({"cookie-a": 1})
