"""Preflight checks and safe command construction for yt-dlp."""

import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from playlist_music.models import AcquisitionResult, TrackRequest
from playlist_music.output import allocate_output_path


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
        "--no-overwrites",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        audio_quality,
        "--embed-metadata",
        "--embed-thumbnail",
        "--ffmpeg-location",
        str(ffmpeg_path),
        "--output",
        str(output_template),
        "--print",
        "after_move:%(webpage_url)s",
        "--",
        source,
    ]


def run_single_download(
    request: TrackRequest,
    output_root: Path,
    filename: str,
    ffmpeg_path: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    quality: str = "recommended",
) -> AcquisitionResult:
    """Run one download and report success only for a confined final MP3."""
    output_root = output_root.resolve()
    final_path = allocate_output_path(output_root, filename)
    template = final_path.with_suffix(".%(ext)s")
    command = build_download_command(request, template, ffmpeg_path, quality=quality)
    try:
        result = runner(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return AcquisitionResult(request, False, None, None, "Download timed out.")
    except OSError:
        return AcquisitionResult(request, False, None, None, "Download command could not start.")

    has_final_file = final_path.is_file() and final_path.resolve().parent == output_root
    if result.returncode and has_final_file:
        detail = result.stderr.strip()[-900:]
        return AcquisitionResult(
            request,
            True,
            final_path,
            _resolved_source(result.stdout, request.url or request.query),
            f"Post-processing warning: {detail or 'metadata or cover could not be embedded.'}",
        )
    if result.returncode:
        detail = result.stderr.strip()[-900:]
        error = f"Download command failed: {detail}" if detail else "Download command failed."
        return AcquisitionResult(request, False, None, None, error)
    if not has_final_file:
        return AcquisitionResult(request, False, None, None, "Expected MP3 file was not created.")

    fallback = request.url or request.query
    return AcquisitionResult(
        request,
        True,
        final_path,
        _resolved_source(result.stdout, fallback),
        None,
    )


def _resolved_source(stdout: str, fallback: str) -> str:
    for line in reversed(stdout.splitlines()):
        parsed = urlsplit(line.strip())
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            return line.strip()
    return fallback
