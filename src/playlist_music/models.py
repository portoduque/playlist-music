"""Normalized data used throughout playlist creation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True, slots=True)
class TrackRequest:
    """One requested track, tied to its original input line."""

    line_number: int
    query: str
    url: str | None = None
    title: str | None = None
    artist: str | None = None


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
class CsvPreview:
    """A small, validated CSV sample for confirming column choices."""

    headers: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    title_column: str | None = None
    artist_column: str | None = None
    url_column: str | None = None
    error: str | None = None


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
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class QueueItemResult:
    """One final queue state: successful, failed, or skipped as duplicate."""

    request: TrackRequest
    status: Literal["succeeded", "failed", "duplicate"]
    acquisition: AcquisitionResult | None


@dataclass(frozen=True, slots=True)
class QueueProgress:
    """Progress emitted after one input request reaches its final state."""

    completed: int
    total: int
    item: QueueItemResult


@dataclass(frozen=True, slots=True)
class QueueResult:
    """Ordered final states for a complete acquisition queue."""

    items: list[QueueItemResult]
