"""Behavioral tests for one safe acquisition without network access."""

import subprocess
from pathlib import Path

from playlist_music.downloader import run_single_download
from playlist_music.models import TrackRequest


def test_returns_a_confined_final_file_and_resolved_source(tmp_path) -> None:
    def runner(command, **_kwargs):
        (tmp_path / "song.mp3").write_bytes(b"audio")
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="https://example.com/resolved\n",
            stderr="",
        )

    result = run_single_download(
        TrackRequest(1, "Song", "https://example.com/input"),
        tmp_path,
        "song.mp3",
        Path("ffmpeg"),
        runner=runner,
    )

    assert result.succeeded is True
    assert result.output_path == tmp_path / "song.mp3"
    assert result.source == "https://example.com/resolved"
    assert result.error is None


def test_reports_command_failure_with_limited_error_output(tmp_path) -> None:
    result = run_single_download(
        TrackRequest(1, "Song"),
        tmp_path,
        "song.mp3",
        Path("ffmpeg"),
        runner=lambda command, **_kwargs: subprocess.CompletedProcess(
            command, 1, stdout="", stderr="x" * 2_000
        ),
    )

    assert result.succeeded is False
    assert result.output_path is None
    assert len(result.error or "") <= 1_000


def test_keeps_a_final_mp3_when_post_processing_returns_an_error(tmp_path) -> None:
    def runner(command, **_kwargs):
        (tmp_path / "song.mp3").write_bytes(b"audio")
        return subprocess.CompletedProcess(command, 1, stdout="https://example.com/song\n", stderr="cover failed")

    result = run_single_download(
        TrackRequest(1, "Song"), tmp_path, "song.mp3", Path("ffmpeg"), runner=runner
    )

    assert result.succeeded is True
    assert result.output_path == tmp_path / "song.mp3"
    assert result.source == "https://example.com/song"
    assert result.error == "Post-processing warning: cover failed"


def test_reports_timeout_without_a_final_file(tmp_path) -> None:
    def runner(command, **_kwargs):
        raise subprocess.TimeoutExpired(command, 30)

    result = run_single_download(
        TrackRequest(1, "Song"), tmp_path, "song.mp3", Path("ffmpeg"), runner=runner
    )

    assert result.succeeded is False
    assert result.error == "Download timed out."


def test_does_not_treat_a_partial_file_as_success(tmp_path) -> None:
    def runner(command, **_kwargs):
        (tmp_path / "song.mp3.part").write_bytes(b"partial")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    result = run_single_download(
        TrackRequest(1, "Song"), tmp_path, "song.mp3", Path("ffmpeg"), runner=runner
    )

    assert result.succeeded is False
    assert result.error == "Expected MP3 file was not created."


def test_uses_a_new_name_without_overwriting_an_existing_file(tmp_path) -> None:
    existing = tmp_path / "song.mp3"
    existing.write_bytes(b"keep")

    def runner(command, **_kwargs):
        (tmp_path / "song (2).mp3").write_bytes(b"new")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    result = run_single_download(
        TrackRequest(1, "Song"), tmp_path, "song.mp3", Path("ffmpeg"), runner=runner
    )

    assert existing.read_bytes() == b"keep"
    assert result.output_path == tmp_path / "song (2).mp3"
