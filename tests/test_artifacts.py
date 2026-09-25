"""Portable playlist and report artifacts from final queue results."""

from pathlib import Path

from playlist_music.artifacts import write_artifacts
from playlist_music.models import AcquisitionResult, QueueItemResult, QueueResult, TrackRequest


def _success(request: TrackRequest, path: Path) -> QueueItemResult:
    return QueueItemResult(
        request,
        "succeeded",
        AcquisitionResult(request, True, path, "https://example.com/song?token=secret", None),
    )


def test_writes_portable_playlists_and_a_safe_report(tmp_path) -> None:
    root = tmp_path / "Minha Playlist"
    root.mkdir()
    first = root / "001 - Música.mp3"
    second = root / "002 - Canção.mp3"
    first.write_bytes(b"audio")
    second.write_bytes(b"audio")
    requests = [TrackRequest(1, "Artista - Música"), TrackRequest(2, "Canção")]
    queue = QueueResult([_success(requests[0], first), _success(requests[1], second)])

    artifacts = write_artifacts(root, "Minha Playlist", queue)

    assert artifacts.m3u8.read_text(encoding="utf-8") == "#EXTM3U\n001 - Música.mp3\n002 - Canção.mp3\n"
    assert artifacts.m3u.read_text(encoding="utf-8-sig") == "#EXTM3U\n001 - Música.mp3\n002 - Canção.mp3\n"
    report = artifacts.report.read_text(encoding="utf-8")
    assert "Artista - Música\tsucceeded\thttps://example.com/song\t001 - Música.mp3\t" in report
    assert "token=secret" not in report

    moved = tmp_path / "Movida"
    root.rename(moved)
    entries = (moved / "Minha Playlist.m3u8").read_text(encoding="utf-8").splitlines()[1:]
    assert all((moved / entry).is_file() for entry in entries)


def test_reports_failures_and_duplicates_without_adding_them_to_playlists(tmp_path) -> None:
    root = tmp_path / "playlist"
    root.mkdir()
    failed = TrackRequest(1, "Falhou")
    duplicate = TrackRequest(2, "Duplicada")
    queue = QueueResult(
        [
            QueueItemResult(
                failed,
                "failed",
                AcquisitionResult(failed, False, None, None, "Source failed: https://bad.example/?key=secret"),
            ),
            QueueItemResult(duplicate, "duplicate", None),
        ]
    )

    artifacts = write_artifacts(root, "playlist", queue)

    assert artifacts.m3u8.read_text(encoding="utf-8") == "#EXTM3U\n"
    report = artifacts.report.read_text(encoding="utf-8")
    assert "Falhou\tfailed" in report
    assert "Duplicada\tduplicate" in report
    assert "key=secret" not in report


def test_reports_metadata_warnings_without_excluding_successful_audio(tmp_path) -> None:
    root = tmp_path / "playlist"
    root.mkdir()
    audio = root / "001 - Song.mp3"
    audio.write_bytes(b"audio")
    request = TrackRequest(1, "Song")
    queue = QueueResult(
        [
            QueueItemResult(
                request,
                "succeeded",
                AcquisitionResult(
                    request,
                    True,
                    audio,
                    "https://example.com/song",
                    None,
                    ("Could not write audio tags.",),
                ),
            )
        ]
    )

    artifacts = write_artifacts(root, "playlist", queue)

    assert artifacts.m3u8.read_text(encoding="utf-8") == "#EXTM3U\n001 - Song.mp3\n"
    assert "warnings" in artifacts.report.read_text(encoding="utf-8").splitlines()[0]
    assert "Could not write audio tags." in artifacts.report.read_text(encoding="utf-8")


def test_ignores_a_success_path_outside_the_playlist_folder(tmp_path) -> None:
    root = tmp_path / "playlist"
    root.mkdir()
    outside = tmp_path / "outside.mp3"
    outside.write_bytes(b"audio")
    request = TrackRequest(1, "Outside")

    artifacts = write_artifacts(root, "playlist", QueueResult([_success(request, outside)]))

    assert artifacts.m3u8.read_text(encoding="utf-8") == "#EXTM3U\n"
    assert "outside.mp3" not in artifacts.report.read_text(encoding="utf-8")
