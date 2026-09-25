"""Behavioral tests for downloader preflight and command construction."""

import subprocess
import sys
from pathlib import Path

import pytest

from playlist_music.downloader import build_download_command, preflight_tools
from playlist_music.models import TrackRequest


def test_preflight_uses_the_current_python_and_detects_ffmpeg() -> None:
    calls: list[list[str]] = []

    def runner(args, **_kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="2026.01.01\n", stderr="")

    result = preflight_tools(ffmpeg_finder=lambda _name: "C:/ffmpeg/ffmpeg.exe", runner=runner)

    assert result.ready is True
    assert result.ffmpeg_path == Path("C:/ffmpeg/ffmpeg.exe")
    assert calls == [[sys.executable, "-m", "yt_dlp", "--version"]]


def test_preflight_reports_missing_ffmpeg_without_running_yt_dlp() -> None:
    result = preflight_tools(
        ffmpeg_finder=lambda _name: None,
        runner=lambda *_args, **_kwargs: pytest.fail("yt-dlp should not run"),
    )

    assert result.ready is False
    assert result.message == "FFmpeg was not found on PATH."


def test_preflight_reports_an_invalid_yt_dlp_version() -> None:
    result = preflight_tools(
        ffmpeg_finder=lambda _name: "ffmpeg",
        runner=lambda args, **_kwargs: subprocess.CompletedProcess(args, 1, stdout="", stderr="bad"),
    )

    assert result.ready is False
    assert result.message == "yt-dlp version check failed."


def test_builds_literal_arguments_for_queries_with_shell_characters(tmp_path) -> None:
    request = TrackRequest(1, "song; & echo unsafe")

    command = build_download_command(
        request,
        tmp_path / "song.%(ext)s",
        Path("C:/ffmpeg/ffmpeg.exe"),
        quality="recommended",
    )

    assert command[:3] == [sys.executable, "-m", "yt_dlp"]
    assert command[-1] == "ytsearch1:song; & echo unsafe"
    assert command[command.index("--audio-format") + 1] == "mp3"
    assert command[command.index("--audio-quality") + 1] == "0"
    assert command[command.index("--ffmpeg-location") + 1] == "C:\\ffmpeg\\ffmpeg.exe"
    assert "--embed-metadata" in command
    assert "--embed-thumbnail" in command


def test_can_omit_metadata_and_cover_flags(tmp_path) -> None:
    command = build_download_command(
        TrackRequest(1, "Song"),
        tmp_path / "song.%(ext)s",
        Path("ffmpeg"),
        embed_metadata=False,
        embed_thumbnail=False,
    )

    assert "--embed-metadata" not in command
    assert "--embed-thumbnail" not in command


@pytest.mark.parametrize("quality, expected", [("balanced", "5"), ("compact", "8")])
def test_maps_supported_qualities_to_ffmpeg_values(tmp_path, quality, expected) -> None:
    command = build_download_command(
        TrackRequest(1, "Song"),
        tmp_path / "song.%(ext)s",
        Path("ffmpeg"),
        quality=quality,
    )

    assert command[command.index("--audio-quality") + 1] == expected
