"""Define shared data models for cookie log processing."""

from datetime import datetime
from typing import NamedTuple


class CookieRecord(NamedTuple):
    """A parsed cookie log record."""

    cookie: str
    timestamp: datetime
