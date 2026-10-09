# Most Active Cookie

A Python command-line tool that finds the most active cookie(s) in a CSV log file for a specified UTC date.

## Requirements

- Python 3.11 or later
- No third-party runtime dependencies

## Usage

The program can be run directly without installation or installed as a command-line tool.

### Direct Execution

Run the program from the project root without installation.

**macOS / Linux:**

```bash
./most_active_cookie -f cookie_log.csv -d 2018-12-09
```

**Windows (PowerShell / Command Prompt):**

```powershell
python most_active_cookie -f cookie_log.csv -d 2018-12-09
```

### Installation (Optional)

It is recommended to use a virtual environment when installing the package or development dependencies.

Create and activate a virtual environment from the project root:

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the package:

```bash
python -m pip install .
```
*Note: On some Linux/macOS systems, you may need to use `python3` instead of `python` when running commands outside the virtual environment.*

Once installed, run the command:

```bash
most_active_cookie -f cookie_log.csv -d 2018-12-09
```

### Arguments

| Argument | Description |
|---|---|
| `-f`, `--file` | Path to the input CSV file |
| `-d`, `--date` | Target date in `YYYY-MM-DD` format |

## Input Format

The input file must be a CSV containing a `cookie` column and a `timestamp` column.

Example:

```csv
cookie,timestamp
AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
```

## Output

The program prints the most active cookie(s) for the specified date to standard output.

If multiple cookies share the highest frequency, each is printed on a separate line.

## Running Tests
It is recommended to activate a virtual environment (see Installation above) before installing the test dependencies.

Install the optional test dependencies:

```bash
python -m pip install -e ".[test]"
```

Run the test suite:

```bash
python -m pytest -v
```

## Development Tools

I used Ruff for linting and formatting the Python code.

To use Ruff, install the optional development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Check for linting and formatting issues:

```bash
ruff check .
ruff format --check .
```

To automatically fix linting issues and format the code:

```bash
ruff check . --fix
ruff format .
```

## Assumptions

- Input files must be in CSV format.
- If there are no active cookies on the specified date, nothing is printed to stdout, and the program exits successfully.
- We assume that the statement *"Cookies in the log file are sorted by timestamp (most recent occurrence is the first line of the file)"* takes timezone offsets into account. This allows us to use an early stopping condition when reading the log file; once a record with a date earlier than the target date is encountered, we break and don't read any more of the file.
- All timestamps are converted to UTC before any date comparisons are made.
- Blank lines in the input file are skipped, and the program continues reading the file.
- The input `-d` parameter must be in the format `YYYY-MM-DD`.
- Whitespace surrounding the cookie and timestamp fields in the log file is stripped before processing.
- Tied cookie occurrences are printed in the order they first appeared in the log file (most recently active first).
- Exit codes: `0` means success (including no matches), `1` means a file or data error, and `2` means a CLI usage error (argparse).
- The CSV file header `cookie,timestamp` is required, and whitespace is stripped from the header fields before validation.

## Design Decisions

- The repo is split into `src/` and `tests/` directories for a clean structure. This, along with the packaging and installation configuration in `pyproject.toml`, allows the project to be installed using `pip`, exposing `most_active_cookie` as a command-line command.
- The `most_active_cookie` file at the project root is an executable wrapper allowing the application to also be run directly without installation.
- The application is split into modules for the different functional components required for the task. This makes it easier to add additional functionality to the CLI at a later date. Each module has a corresponding test file which tests the core functionality and edge cases.
