"""Optional ID3 metadata writes that never delete the audio file."""

from dataclasses import dataclass
from pathlib import Path

from mutagen import MutagenError
from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TALB, TIT2, TPE1, TRCK


@dataclass(frozen=True, slots=True)
class MetadataResult:
    """Recoverable issues from writing optional metadata."""

    issues: list[str]


def write_metadata(
    audio_path: Path,
    title: str | None,
    artist: str | None,
    album: str | None,
    cover_path: Path | None = None,
    *,
    fallback_title: str | None = None,
    track_number: str | None = None,
) -> MetadataResult:
    """Write available ID3 fields and a JPEG/PNG cover without deleting audio."""
    try:
        tags = ID3(audio_path)
    except ID3NoHeaderError:
        tags = ID3()
    except (OSError, MutagenError):
        return MetadataResult(["Could not read audio tags."])

    fallback_needed = bool(fallback_title and not tags.get("TIT2"))
    if title or fallback_needed:
        tags.add(TIT2(encoding=3, text=title or fallback_title))
    if artist:
        tags.add(TPE1(encoding=3, text=artist))
    if album:
        tags.add(TALB(encoding=3, text=album))
    if track_number:
        tags.add(TRCK(encoding=3, text=track_number))
    if title or artist or album or track_number or fallback_needed:
        try:
            tags.save(audio_path)
        except (OSError, MutagenError):
            return MetadataResult(["Could not write audio tags."])

    if not cover_path:
        return MetadataResult([])
    try:
        cover_data = cover_path.read_bytes()
    except OSError:
        return MetadataResult(["Could not read cover image."])
    mime = _cover_mime(cover_data)
    if not mime:
        return MetadataResult(["Cover must be a JPEG or PNG file."])

    tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=cover_data))
    try:
        tags.save(audio_path)
    except (OSError, MutagenError):
        return MetadataResult(["Could not write cover image."])
    return MetadataResult([])


def _cover_mime(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    return None
