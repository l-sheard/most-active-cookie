"""Tests for reading and validating cookie log files."""

from datetime import datetime, timezone

import pytest

from most_active_cookie.cookie_log_reader import (
    CookieLogError,
    parse_log_row,
    read_cookie_log,
)
from most_active_cookie.models import CookieRecord

# Test parse_log_row


@pytest.mark.parametrize(
    "log_row, expected_timestamp",
    [
        (
            ["cookie-a", "2018-12-09T14:19:00+00:00"],
            datetime(2018, 12, 9, 14, 19, tzinfo=timezone.utc),
        ),
        (
            ["cookie-a", "2018-12-09T14:19:00+01:00"],
            datetime(2018, 12, 9, 13, 19, tzinfo=timezone.utc),
        ),
        (
            ["cookie-a", "2018-12-09T23:19:00-03:00"],
            datetime(2018, 12, 10, 2, 19, tzinfo=timezone.utc),
        ),
        (
            ["cookie-a", "2018-12-09T14:19:00Z"],
            datetime(2018, 12, 9, 14, 19, tzinfo=timezone.utc),
        ),
    ],
    ids=[
        "utc-timestamp",
        "positive-timezone-offset",
        "negative-offset-crosses-utc-date",
        "utc-z-suffix",
    ],
)
def test_parse_log_row_valid(log_row, expected_timestamp):
    result = parse_log_row(log_row, 2)

    assert result == CookieRecord(
        cookie="cookie-a",
        timestamp=expected_timestamp,
    )


@pytest.mark.parametrize(
    "log_row",
    [
        ["", "2018-12-09T14:19:00+00:00"],
        ["cookie-a", ""],
        ["cookie-a", "2018-12-09T14:19:00+00:00", "hello"],
        ["cookie-a"],
        ["cookie-a", "hello"],
        ["cookie-a", "2018-12-09T14:19:00"],
    ],
    ids=[
        "missing-cookie",
        "missing-timestamp",
        "extra-fields",
        "missing-fields",
        "invalid-timestamp",
        "missing-timezone-offset",
    ],
)
def test_parse_log_row_invalid(log_row):
    with pytest.raises(CookieLogError):
        parse_log_row(log_row, 2)


# Test read_cookie_log


def test_read_cookie_log(tmp_path):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,timestamp\n"
        "cookie-a,2018-12-09T14:19:00+00:00\n"
        "cookie-b,2018-12-09T13:19:00+00:00\n",
        encoding="utf-8",
    )

    result = list(read_cookie_log(filepath))

    assert result == [
        CookieRecord(
            cookie="cookie-a", timestamp=datetime(2018, 12, 9, 14, 19, tzinfo=timezone.utc)
        ),
        CookieRecord(
            cookie="cookie-b", timestamp=datetime(2018, 12, 9, 13, 19, tzinfo=timezone.utc)
        ),
    ]


def test_read_cookie_log_with_empty_file(tmp_path):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text("", encoding="utf-8")

    with pytest.raises(CookieLogError):
        list(read_cookie_log(filepath))


def test_read_cookie_log_with_invalid_header(tmp_path):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,hello\ncookie-a,2018-12-09T14:19:00+00:00\ncookie-b,2018-12-09T13:19:00+00:00\n",
        encoding="utf-8",
    )

    with pytest.raises(CookieLogError):
        list(read_cookie_log(filepath))


def test_read_cookie_log_with_header_no_records(tmp_path):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,timestamp\n",
        encoding="utf-8",
    )

    result = list(read_cookie_log(filepath))

    assert result == []


def test_read_cookie_log_with_blank_lines(tmp_path):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,timestamp\n"
        "\n"
        "cookie-a,2018-12-09T14:00:00+00:00\n"
        "\n"
        "cookie-b,2018-12-09T12:00:00+00:00\n"
        "\n",
        encoding="utf-8",
    )

    records = list(read_cookie_log(filepath))

    assert len(records) == 2
    assert [record.cookie for record in records] == ["cookie-a", "cookie-b"]


def test_read_cookie_log_with_whitespace(tmp_path):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        " cookie , timestamp \n cookie-a , 2018-12-09T14:00:00+00:00 \n",
        encoding="utf-8",
    )

    records = list(read_cookie_log(filepath))

    assert len(records) == 1
    assert records[0].cookie == "cookie-a"
    assert records[0].timestamp == datetime(2018, 12, 9, 14, 0, tzinfo=timezone.utc)
