"""Preflight checks and safe command construction for yt-dlp."""

import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from playlist_music.models import TrackRequest


AUDIO_QUALITY = {"recommended": "0", "balanced": "5", "compact": "8"}


@dataclass(frozen=True, slots=True)
class PreflightResult:
    """Whether the required local tools are ready for a download."""

    ready: bool
    ffmpeg_path: Path | None
    message: str | None


def preflight_tools(
    ffmpeg_finder: Callable[[str], str | None] = shutil.which,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> PreflightResult:
    """Confirm FFmpeg exists and the installed yt-dlp module reports a version."""
    ffmpeg = ffmpeg_finder("ffmpeg")
    if not ffmpeg:
        return PreflightResult(False, None, "FFmpeg was not found on PATH.")
    try:
        result = runner(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return PreflightResult(False, Path(ffmpeg), "yt-dlp version check failed.")
    if result.returncode or not result.stdout.strip():
        return PreflightResult(False, Path(ffmpeg), "yt-dlp version check failed.")
    return PreflightResult(True, Path(ffmpeg), None)


def build_download_command(
    request: TrackRequest,
    output_template: Path,
    ffmpeg_path: Path,
    *,
    quality: str = "recommended",
) -> list[str]:
    """Build, but do not execute, an MP3 extraction command."""
    try:
        audio_quality = AUDIO_QUALITY[quality]
    except KeyError as error:
        raise ValueError(f"Unsupported quality: {quality}") from error

    source = request.url or f"ytsearch1:{request.query}"
    return [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        audio_quality,
        "--ffmpeg-location",
        str(ffmpeg_path),
        "--output",
        str(output_template),
        "--",
        source,
    ]
