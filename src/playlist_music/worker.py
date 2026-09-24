"""Threaded service execution that communicates only through queue events."""

from collections.abc import Callable
from dataclasses import dataclass
from queue import Empty, Queue
from threading import Lock, Thread
from typing import Literal

from playlist_music.models import QueueProgress
from playlist_music.service import ServiceResult


@dataclass(frozen=True, slots=True)
class WorkerEvent:
    """One message sent from the worker thread to the UI thread."""

    kind: Literal["progress", "completed", "error"]
    progress: QueueProgress | None = None
    result: ServiceResult | None = None
    message: str | None = None


WorkerRun = Callable[[Callable[[QueueProgress], None]], ServiceResult]


class PlaylistWorker:
    """Run one service call at a time without allowing Tkinter access in the thread."""

    def __init__(self) -> None:
        self._events: Queue[WorkerEvent] = Queue()
        self._lock = Lock()
        self._thread: Thread | None = None

    def start(self, run: WorkerRun) -> bool:
        """Start *run* once, returning False while a previous run is still active."""
        with self._lock:
            if self._thread and self._thread.is_alive():
                return False
            self._thread = Thread(target=self._run, args=(run,), daemon=True)
            self._thread.start()
            return True

    def join(self, timeout: float | None = None) -> None:
        """Wait for the active thread; used by non-UI tests."""
        if self._thread:
            self._thread.join(timeout)

    @property
    def is_running(self) -> bool:
        """Whether a service call is currently active."""
        with self._lock:
            return bool(self._thread and self._thread.is_alive())

    def drain_events(self) -> list[WorkerEvent]:
        """Return all messages currently available to the UI thread."""
        events: list[WorkerEvent] = []
        while True:
            try:
                events.append(self._events.get_nowait())
            except Empty:
                return events

    def _run(self, run: WorkerRun) -> None:
        try:
            result = run(lambda progress: self._events.put(WorkerEvent("progress", progress=progress)))
        except Exception as error:
            self._events.put(WorkerEvent("error", message=str(error)))
        else:
            self._events.put(WorkerEvent("completed", result=result))
