"""Thread worker events without a Tkinter window or network access."""

from threading import Event

from playlist_music.models import QueueItemResult, QueueProgress, QueueResult, TrackRequest
from playlist_music.service import ServiceResult
from playlist_music.worker import PlaylistWorker


def _progress(completed: int, total: int) -> QueueProgress:
    request = TrackRequest(completed, f"Song {completed}")
    item = QueueItemResult(request, "duplicate", None)
    return QueueProgress(completed, total, item)


def test_delivers_progress_before_the_final_result() -> None:
    worker = PlaylistWorker()

    def run(on_progress) -> ServiceResult:
        on_progress(_progress(1, 2))
        on_progress(_progress(2, 2))
        return ServiceResult(True, None, QueueResult([]), None)

    assert worker.start(run) is True
    worker.join()

    events = worker.drain_events()
    assert [event.kind for event in events] == ["progress", "progress", "completed"]
    assert [event.progress.completed for event in events[:2]] == [1, 2]


def test_converts_an_unexpected_exception_to_a_recoverable_event() -> None:
    worker = PlaylistWorker()

    assert worker.start(lambda _on_progress: (_ for _ in ()).throw(RuntimeError("Unexpected failure")))
    worker.join()

    event = worker.drain_events()[0]
    assert event.kind == "error"
    assert event.message == "Unexpected failure"


def test_rejects_a_second_start_while_work_is_running() -> None:
    worker = PlaylistWorker()
    entered = Event()
    release = Event()

    def run(_on_progress) -> ServiceResult:
        entered.set()
        release.wait(timeout=1)
        return ServiceResult(True, None, QueueResult([]), None)

    assert worker.start(run) is True
    assert entered.wait(timeout=1) is True
    assert worker.start(run) is False
    release.set()
    worker.join()
