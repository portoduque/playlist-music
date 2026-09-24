"""Queue behavior without real downloads or subprocesses."""

from pathlib import Path

from playlist_music.models import AcquisitionResult, TrackRequest
from playlist_music.queue import process_queue


def _success(request: TrackRequest) -> AcquisitionResult:
    return AcquisitionResult(request, True, Path(f"{request.line_number}.mp3"), "source", None)


def _failure(request: TrackRequest) -> AcquisitionResult:
    return AcquisitionResult(request, False, None, None, "Download failed.")


def test_processes_requests_and_reports_progress_in_input_order() -> None:
    requests = [TrackRequest(1, "One"), TrackRequest(2, "Two"), TrackRequest(3, "Three")]
    events = []

    result = process_queue(requests, _success, events.append)

    assert [item.request for item in result.items] == requests
    assert [item.status for item in result.items] == ["succeeded", "succeeded", "succeeded"]
    assert [(event.completed, event.total) for event in events] == [(1, 3), (2, 3), (3, 3)]


def test_continues_after_an_individual_failure() -> None:
    requests = [TrackRequest(1, "One"), TrackRequest(2, "Two"), TrackRequest(3, "Three")]

    result = process_queue(requests, lambda request: _failure(request) if request.query == "Two" else _success(request))

    assert [item.status for item in result.items] == ["succeeded", "failed", "succeeded"]


def test_keeps_all_failures_as_final_results() -> None:
    requests = [TrackRequest(1, "One"), TrackRequest(2, "Two")]

    result = process_queue(requests, _failure)

    assert [item.status for item in result.items] == ["failed", "failed"]


def test_continues_when_an_acquirer_raises() -> None:
    requests = [TrackRequest(1, "One"), TrackRequest(2, "Two")]

    def acquire(request: TrackRequest) -> AcquisitionResult:
        if request.query == "One":
            raise RuntimeError("Unexpected failure")
        return _success(request)

    result = process_queue(requests, acquire)

    assert [item.status for item in result.items] == ["failed", "succeeded"]
    assert result.items[0].acquisition.error == "Unexpected failure"


def test_marks_duplicate_without_calling_acquirer() -> None:
    request = TrackRequest(1, "One")
    calls = []

    result = process_queue([request, TrackRequest(2, " one ")], lambda item: calls.append(item) or _success(item))

    assert [item.status for item in result.items] == ["succeeded", "duplicate"]
    assert calls == [request]
    assert result.items[1].acquisition is None


def test_handles_an_empty_queue() -> None:
    assert process_queue([], _success).items == []
