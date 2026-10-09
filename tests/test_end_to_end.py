"""End-to-end tests for the most active cookie command-line program."""

import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
TEST_CSV = Path(__file__).resolve().parent / "resources" / "test_cookie_log.csv"


def test_script_end_to_end():
    result = subprocess.run(
        [
            sys.executable,
            "most_active_cookie",
            "-f",
            str(TEST_CSV),
            "-d",
            "2018-12-09",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == "AtY0laUfhglK3lC7\n"
    assert result.stderr == ""


def test_script_end_to_end_with_three_way_tie():
    result = subprocess.run(
        [
            sys.executable,
            "most_active_cookie",
            "-f",
            str(TEST_CSV),
            "-d",
            "2018-12-08",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "SAZuXPGUrfbcn5UA",
        "4sMM2LxV07bPJzwf",
        "fbcn5UAVanZf6UtG",
    ]
    assert result.stderr == ""
