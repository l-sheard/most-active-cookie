"""Tests for command-line argument parsing and most active cookie program execution."""

import argparse
from datetime import date
from pathlib import Path

import pytest

import most_active_cookie.cli as cli
from most_active_cookie.cli import (
    _parse_command_date,
    main,
    parse_command_args,
)

# Test _parse_command_date


def test_parse_command_date():
    date_string = "2018-12-09"
    result = _parse_command_date(date_string)

    assert result == date(2018, 12, 9)


@pytest.mark.parametrize(
    "date_string",
    [
        "2018-13-09",  # Invalid month
        "2018-12-9",  # Day not zero-padded
        "09-12-2018",  # Incorrect date format
        "not-a-date",  # Not a date
    ],
)
def test_parse_command_date_with_invalid_date(date_string):
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_command_date(date_string)


# Test parse_command_args


def test_parse_command_args():
    test_args = [
        "-f",
        "cookie_log.csv",
        "-d",
        "2018-12-09",
    ]

    args = parse_command_args(test_args)

    assert args.file == Path("cookie_log.csv")
    assert args.date == date(2018, 12, 9)


def test_parse_command_args_with_missing_file():
    test_args = [
        "-d",
        "2018-12-09",
    ]

    with pytest.raises(SystemExit):
        parse_command_args(test_args)


def test_parse_command_args_with_missing_date():
    test_args = [
        "-f",
        "cookie_log.csv",
    ]

    with pytest.raises(SystemExit):
        parse_command_args(test_args)


def test_parse_command_args_with_invalid_date():
    test_args = [
        "-f",
        "cookie_log.csv",
        "-d",
        "2018-13-09",
    ]

    with pytest.raises(SystemExit) as exc_info:
        parse_command_args(test_args)

    assert exc_info.value.code == 2


# Test Main


def test_main_success(tmp_path, capsys):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,timestamp\n"
        "AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00\n"
        "SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00\n"
        "5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00\n"
        "AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00\n"
        "SAZuXPGUrfbcn5UA,2018-12-08T22:03:00+00:00\n"
        "4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00\n"
        "fbcn5UAVanZf6UtG,2018-12-08T09:30:00+00:00\n"
        "4sMM2LxV07bPJzwf,2018-12-07T23:30:00+00:00\n",
        encoding="utf-8",
    )

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-09",
        ]
    )
    captured = capsys.readouterr()

    assert result == 0
    assert captured.out == "AtY0laUfhglK3lC7\n"
    assert captured.err == ""


def test_main_with_tied_cookie_counts(tmp_path, capsys):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,timestamp\n"
        "cookie-c,2018-12-09T18:23:00+00:00\n"
        "cookie-c,2018-12-09T16:37:00+00:00\n"
        "cookie-a,2018-12-09T15:24:00+00:00\n"
        "cookie-b,2018-12-09T11:13:00+00:00\n"
        "cookie-a,2018-12-09T10:19:00+00:00\n",
        encoding="utf-8",
    )

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-09",
        ]
    )
    captured = capsys.readouterr()

    assert result == 0
    # Check tied cookies are printed on separate lines, regardless of order.
    assert sorted(captured.out.splitlines()) == ["cookie-a", "cookie-c"]
    assert captured.err == ""


def test_main_with_no_cookies_on_specified_date(tmp_path, capsys):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,timestamp\n"
        "cookie-c,2018-12-09T18:23:00+00:00\n"
        "cookie-c,2018-12-09T16:37:00+00:00\n"
        "cookie-a,2018-12-09T15:24:00+00:00\n"
        "cookie-b,2018-12-09T11:13:00+00:00\n"
        "cookie-a,2018-12-09T10:19:00+00:00\n",
        encoding="utf-8",
    )

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-08",
        ]
    )
    captured = capsys.readouterr()

    assert result == 0
    assert captured.out == ""
    assert captured.err == ""


def test_main_with_file_not_found(tmp_path, capsys):
    filepath = tmp_path / "does_not_exist.csv"

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-08",
        ]
    )
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err == f"Error: file not found: {filepath}\n"


def test_main_with_directory_instead_of_file(tmp_path, capsys):
    result = main(
        [
            "-f",
            str(tmp_path),
            "-d",
            "2018-12-09",
        ]
    )
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err == f"Error: expected a file, got a directory: {tmp_path}\n"


def test_main_with_invalid_cookie_log(tmp_path, capsys):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_text(
        "cookie,hello\n",
        encoding="utf-8",
    )

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-08",
        ]
    )
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert "Cookie log header is invalid" in captured.err


def test_main_with_permission_error(tmp_path, monkeypatch, capsys):
    filepath = tmp_path / "cookie_log.csv"

    def raise_permission_error(_filepath):
        raise PermissionError

    monkeypatch.setattr(
        cli,
        "read_cookie_log",
        raise_permission_error,
    )

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-09",
        ]
    )
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err == f"Error: permission denied when reading: {filepath}\n"


def test_main_with_non_utf8_file(tmp_path, capsys):
    filepath = tmp_path / "cookie_log.csv"

    filepath.write_bytes(b"\xff\xfe\x00\x00")

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-09",
        ]
    )
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err == f"Error: {filepath} is not valid UTF-8 text\n"


def test_main_with_os_error(tmp_path, monkeypatch, capsys):
    filepath = tmp_path / "cookie_log.csv"

    def raise_os_error(_filepath):
        raise OSError("unable to read file")

    monkeypatch.setattr(
        cli,
        "read_cookie_log",
        raise_os_error,
    )

    result = main(
        [
            "-f",
            str(filepath),
            "-d",
            "2018-12-09",
        ]
    )
    captured = capsys.readouterr()

    assert result == 1
    assert captured.out == ""
    assert captured.err == (f"Error: unable to read {filepath}: unable to read file\n")
