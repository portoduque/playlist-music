"""Headless composition of import, acquisition, metadata, and artifacts."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from playlist_music.artifacts import ArtifactPaths, write_artifacts
from playlist_music.downloader import PreflightResult, preflight_tools, run_single_download
from playlist_music.metadata import MetadataResult, write_metadata
from playlist_music.models import (
    AcquisitionResult,
    ImportResult,
    QueueProgress,
    QueueResult,
    TrackRequest,
)
from playlist_music.queue import process_queue


@dataclass(frozen=True, slots=True)
class ServiceResult:
    """A blocked start or the final result of a headless playlist run."""

    started: bool
    message: str | None
    queue: QueueResult | None
    artifacts: ArtifactPaths | None


MetadataWriter = Callable[[Path, str | None, str | None, str | None], MetadataResult]


def create_playlist(
    playlist_name: str,
    output_root: Path,
    imported: ImportResult,
    *,
    quality: str = "recommended",
    preflight: Callable[[], PreflightResult] = preflight_tools,
    acquire: Callable[[TrackRequest], AcquisitionResult] | None = None,
    write_tags: MetadataWriter = write_metadata,
    on_progress: Callable[[QueueProgress], None] | None = None,
) -> ServiceResult:
    """Create one playlist folder from normalized input without knowing about Tkinter."""
    if not playlist_name.strip():
        return ServiceResult(False, "Playlist name is required.", None, None)
    if not imported.requests or imported.issues:
        return ServiceResult(False, "Input must contain valid tracks without errors.", None, None)
    tools = preflight()
    if not tools.ready or not tools.ffmpeg_path:
        return ServiceResult(False, tools.message or "Required tools are unavailable.", None, None)

    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if acquire is None:
        def acquire(request: TrackRequest) -> AcquisitionResult:
            return run_single_download(
                request,
                output_root,
                f"{request.line_number:03d} - {request.query}.mp3",
                tools.ffmpeg_path,
                quality=quality,
            )
    queue = process_queue(imported.requests, acquire, on_progress)
    for item in queue.items:
        if item.status == "succeeded" and item.acquisition and item.acquisition.output_path:
            write_tags(item.acquisition.output_path, item.request.query, None, None)
    artifacts = write_artifacts(output_root, playlist_name, queue)
    return ServiceResult(True, None, queue, artifacts)
