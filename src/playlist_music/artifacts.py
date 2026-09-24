"""Portable playlists and a safe text report from queue results."""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from playlist_music.models import QueueItemResult, QueueResult
from playlist_music.output import safe_filename


URL_PATTERN = re.compile(r"https?://[^\s]+")


@dataclass(frozen=True, slots=True)
class ArtifactPaths:
    """Files generated for one portable playlist folder."""

    m3u8: Path
    m3u: Path
    report: Path


def write_artifacts(root: Path, playlist_name: str, queue: QueueResult) -> ArtifactPaths:
    """Write playlists for valid final MP3s and a report for every queue item."""
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    name = Path(safe_filename(playlist_name)).stem or "playlist"
    paths = ArtifactPaths(root / f"{name}.m3u8", root / f"{name}.m3u", root / "resultado.txt")
    relative_paths = [_relative_output_path(root, item) for item in queue.items]
    entries = [path.as_posix() for path in relative_paths if path]
    content = "#EXTM3U\n" + "".join(f"{entry}\n" for entry in entries)
    paths.m3u8.write_text(content, encoding="utf-8", newline="\n")
    paths.m3u.write_text(content, encoding="utf-8-sig", newline="\n")
    report_lines = ["query\tstatus\tsource\tfile\terror"]
    for item, relative_path in zip(queue.items, relative_paths, strict=True):
        acquisition = item.acquisition
        source = acquisition.source if acquisition else ""
        error = acquisition.error if acquisition else "Duplicate request."
        values = (
            _redact_urls(item.request.query),
            item.status,
            _redact_urls(source or ""),
            relative_path.as_posix() if relative_path else "",
            _redact_urls(error or ""),
        )
        report_lines.append("\t".join(values))
    paths.report.write_text("\n".join(report_lines) + "\n", encoding="utf-8", newline="\n")
    return paths


def _relative_output_path(root: Path, item: QueueItemResult) -> Path | None:
    if item.status != "succeeded" or not item.acquisition or not item.acquisition.output_path:
        return None
    output_path = item.acquisition.output_path
    if not output_path.is_file():
        return None
    try:
        return output_path.resolve().relative_to(root)
    except ValueError:
        return None


def _redact_urls(value: str) -> str:
    return URL_PATTERN.sub(_redact_url, value)


def _redact_url(match: re.Match[str]) -> str:
    parsed = urlsplit(match.group())
    hostname = parsed.hostname or ""
    try:
        port = f":{parsed.port}" if parsed.port else ""
    except ValueError:
        port = ""
    return urlunsplit((parsed.scheme, f"{hostname}{port}", parsed.path, "", ""))
