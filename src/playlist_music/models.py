"""Normalized data used throughout playlist creation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrackRequest:
    """One requested track, tied to its original input line."""

    line_number: int
    query: str
    url: str | None = None


@dataclass(frozen=True, slots=True)
class ImportIssue:
    """A readable problem found while importing a list."""

    line_number: int | None
    message: str


@dataclass(frozen=True, slots=True)
class ImportResult:
    """Normalized requests and recoverable input issues."""

    requests: list[TrackRequest]
    issues: list[ImportIssue]
