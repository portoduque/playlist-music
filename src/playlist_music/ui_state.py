"""Testable state for the small Tkinter input screen."""

from dataclasses import dataclass, field
from pathlib import Path

from playlist_music.downloader import AUDIO_QUALITY
from playlist_music.imports import parse_pasted_text
from playlist_music.models import ImportResult


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
