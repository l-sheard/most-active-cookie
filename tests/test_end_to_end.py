"""End-to-end tests for the most active cookie command-line program."""

import subprocess
import sys
from pathlib import Path


def test_script_end_to_end():
    project_dir = Path(__file__).resolve().parent.parent

    result = subprocess.run(
        [
            sys.executable,
            "most_active_cookie",
            "-f",
            "cookie_log.csv",
            "-d",
            "2018-12-09",
        ],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == "AtY0laUfhglK3lC7\n"
    assert result.stderr == ""


def test_script_end_to_end_with_three_way_tie():
    project_dir = Path(__file__).resolve().parent.parent

    result = subprocess.run(
        [
            sys.executable,
            "most_active_cookie",
            "-f",
            "cookie_log.csv",
            "-d",
            "2018-12-08",
        ],
        cwd=project_dir,
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
