"""Normalized data used throughout playlist creation."""

from dataclasses import dataclass
from pathlib import Path


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


@dataclass(frozen=True, slots=True)
class DeduplicationResult:
    """Requests retained for processing and requests skipped as duplicates."""

    unique_requests: list[TrackRequest]
    duplicate_requests: list[TrackRequest]


@dataclass(frozen=True, slots=True)
class AcquisitionResult:
    """The final state of one requested track acquisition."""

    request: TrackRequest
    succeeded: bool
    output_path: Path | None
    source: str | None
    error: str | None
