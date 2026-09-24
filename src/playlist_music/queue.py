"""Sequential, failure-tolerant processing of normalized requests."""

from collections.abc import Callable, Iterable

from playlist_music.models import (
    AcquisitionResult,
    QueueItemResult,
    QueueProgress,
    QueueResult,
    TrackRequest,
)


def process_queue(
    requests: Iterable[TrackRequest],
    acquire: Callable[[TrackRequest], AcquisitionResult],
    on_progress: Callable[[QueueProgress], None] | None = None,
) -> QueueResult:
    """Acquire requests in order, continuing after failures and duplicates."""
    ordered_requests = list(requests)
    items: list[QueueItemResult] = []
    seen: set[str] = set()
    total = len(ordered_requests)

    for request in ordered_requests:
        key = (request.url or request.query).strip().casefold()
        if key in seen:
            item = QueueItemResult(request, "duplicate", None)
        else:
            seen.add(key)
            item = _acquire_item(request, acquire)
        items.append(item)
        if on_progress:
            on_progress(QueueProgress(len(items), total, item))

    return QueueResult(items)


def _acquire_item(
    request: TrackRequest, acquire: Callable[[TrackRequest], AcquisitionResult]
) -> QueueItemResult:
    try:
        acquisition = acquire(request)
    except Exception as error:
        acquisition = AcquisitionResult(request, False, None, None, str(error))
    status = "succeeded" if acquisition.succeeded else "failed"
    return QueueItemResult(request, status, acquisition)
