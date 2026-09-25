"""Testable state for the small Tkinter input screen."""

from dataclasses import dataclass, field
from pathlib import Path

from playlist_music.artifacts import ArtifactPaths
from playlist_music.downloader import AUDIO_QUALITY
from playlist_music.imports import parse_pasted_text
from playlist_music.models import ImportResult, QueueResult
from playlist_music.service import ServiceResult


@dataclass(slots=True)
class InputState:
    """User choices and the current normalized pasted-text result."""

    output_folder: Path | None = None
    quality: str = "recommended"
    advanced_open: bool = False
    imported: ImportResult = field(default_factory=lambda: parse_pasted_text(""))

    @property
    def import_summary(self) -> str:
        valid = len(self.imported.requests)
        invalid = len(self.imported.issues)
        if not valid and invalid == 1 and self.imported.issues[0].line_number is None:
            return "Add music queries or URLs to begin."
        return f"{valid} valid, {invalid} invalid."

    def set_pasted_text(self, text: str) -> None:
        self.imported = parse_pasted_text(text)

    def set_imported(self, imported: ImportResult) -> None:
        self.imported = imported

    def set_output_folder(self, folder: Path) -> None:
        self.output_folder = folder

    def set_quality(self, quality: str) -> None:
        if quality not in AUDIO_QUALITY:
            raise ValueError(f"Unsupported quality: {quality}")
        self.quality = quality

    def toggle_advanced(self) -> None:
        self.advanced_open = not self.advanced_open


@dataclass(frozen=True, slots=True)
class CompletionActions:
    """Clear final feedback and optional, safe native-open targets."""

    message: str
    folder: Path | None
    playlist: Path | None


def completion_actions(result: ServiceResult, output_folder: Path | None) -> CompletionActions:
    """Summarize a completed run without exposing paths outside its output folder."""
    folder = safe_output_path(output_folder, result.output_folder or output_folder, directory=True)
    playlist = _safe_playlist_path(result.artifacts, folder)
    return CompletionActions(_completion_message(result), folder, playlist)


def safe_output_path(
    output_folder: Path | None, candidate: Path | None, *, directory: bool
) -> Path | None:
    """Return an existing output path only when it resolves inside the chosen folder."""
    if not output_folder or not candidate:
        return None
    try:
        root = output_folder.resolve(strict=True)
        path = candidate.resolve(strict=True)
        path.relative_to(root)
    except (OSError, ValueError):
        return None
    if directory and path.is_dir():
        return path
    if not directory and path.is_file():
        return path
    return None


def _completion_message(result: ServiceResult) -> str:
    if not result.started:
        return result.message or "Playlist creation could not start."
    queue = result.queue or QueueResult([])
    succeeded = sum(item.status == "succeeded" for item in queue.items)
    failed = sum(item.status == "failed" for item in queue.items)
    duplicates = sum(item.status == "duplicate" for item in queue.items)
    warnings = sum(len(item.acquisition.warnings) for item in queue.items if item.acquisition)
    duplicate_label = "duplicate" if duplicates == 1 else "duplicates"
    if not succeeded:
        return f"Finished: no tracks downloaded; {failed} failed, {duplicates} {duplicate_label} skipped."
    message = f"Finished: {succeeded} downloaded, {failed} failed, {duplicates} {duplicate_label} skipped."
    if warnings:
        warning_label = "warning" if warnings == 1 else "warnings"
        return f"{message[:-1]}; {warnings} metadata {warning_label}."
    return message


def _safe_playlist_path(artifacts: ArtifactPaths | None, output_folder: Path | None) -> Path | None:
    if not artifacts:
        return None
    return safe_output_path(output_folder, artifacts.m3u8, directory=False)
