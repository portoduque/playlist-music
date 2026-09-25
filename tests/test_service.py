"""Headless playlist creation with fake local dependencies only."""

from pathlib import Path

from playlist_music.downloader import PreflightResult
from playlist_music.metadata import MetadataResult
from playlist_music.models import AcquisitionResult, ImportIssue, ImportResult, TrackRequest
from playlist_music.service import create_playlist


def test_creates_a_complete_folder_with_fake_dependencies(tmp_path) -> None:
    root = tmp_path / "library"
    playlist_folder = root / "Minha Playlist"
    requests = [TrackRequest(1, "One"), TrackRequest(2, "Two")]
    metadata_calls = []
    events = []

    def acquire(request: TrackRequest) -> AcquisitionResult:
        output = playlist_folder / f"{request.line_number:03d} - {request.query}.mp3"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"audio")
        return AcquisitionResult(request, True, output, "https://example.com/song", None)

    def write_tags(*args) -> MetadataResult:
        metadata_calls.append(args)
        return MetadataResult([])

    result = create_playlist(
        "Minha Playlist",
        root,
        ImportResult(requests, []),
        preflight=lambda: PreflightResult(True, Path("ffmpeg"), None),
        acquire=acquire,
        write_tags=write_tags,
        on_progress=events.append,
    )

    assert result.started is True
    assert [item.status for item in result.queue.items] == ["succeeded", "succeeded"]
    assert [event.completed for event in events] == [1, 2]
    assert len(metadata_calls) == 2
    assert result.output_folder == playlist_folder
    assert result.artifacts.m3u8.parent == playlist_folder
    assert result.artifacts.m3u8.read_text(encoding="utf-8") == "#EXTM3U\n001 - One.mp3\n002 - Two.mp3\n"
    assert result.artifacts.m3u.is_file()
    assert result.artifacts.report.is_file()


def test_rejects_invalid_input_before_preflight(tmp_path) -> None:
    called = False

    def preflight() -> PreflightResult:
        nonlocal called
        called = True
        return PreflightResult(True, Path("ffmpeg"), None)

    result = create_playlist(
        "playlist",
        tmp_path / "output",
        ImportResult([], [ImportIssue(1, "Invalid input")]),
        preflight=preflight,
    )

    assert result.started is False
    assert result.message == "Input must contain valid tracks without errors."
    assert called is False


def test_rejects_missing_preflight_without_running_the_queue(tmp_path) -> None:
    called = False

    def acquire(request: TrackRequest) -> AcquisitionResult:
        nonlocal called
        called = True
        return AcquisitionResult(request, False, None, None, "Should not run")

    result = create_playlist(
        "playlist",
        tmp_path / "output",
        ImportResult([TrackRequest(1, "One")], []),
        preflight=lambda: PreflightResult(False, None, "FFmpeg was not found on PATH."),
        acquire=acquire,
    )

    assert result.started is False
    assert result.message == "FFmpeg was not found on PATH."
    assert called is False


def test_keeps_processing_after_one_acquisition_failure(tmp_path) -> None:
    root = tmp_path / "library"
    playlist_folder = root / "playlist"
    requests = [TrackRequest(1, "Broken"), TrackRequest(2, "Working")]

    def acquire(request: TrackRequest) -> AcquisitionResult:
        if request.query == "Broken":
            return AcquisitionResult(request, False, None, None, "Source failed.")
        output = playlist_folder / "002 - Working.mp3"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"audio")
        return AcquisitionResult(request, True, output, "https://example.com/working", None)

    result = create_playlist(
        "playlist",
        root,
        ImportResult(requests, []),
        preflight=lambda: PreflightResult(True, Path("ffmpeg"), None),
        acquire=acquire,
    )

    assert result.started is True
    assert [item.status for item in result.queue.items] == ["failed", "succeeded"]
    assert result.artifacts.m3u8.read_text(encoding="utf-8") == "#EXTM3U\n002 - Working.mp3\n"
