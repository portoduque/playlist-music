"""Safe output names and paths for generated playlist files."""

import re
from collections.abc import Iterable
from pathlib import Path

from playlist_music.models import DeduplicationResult, TrackRequest


INVALID_FILENAME_CHARACTERS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


def safe_filename(value: str) -> str:
    """Return a non-empty Windows-safe filename without path components."""
    name = INVALID_FILENAME_CHARACTERS.sub("", value).strip(". ") or "track"
    stem = name.split(".", maxsplit=1)[0].rstrip(" ").upper()
    return f"{name}_" if stem in WINDOWS_RESERVED_NAMES else name


def allocate_output_path(root: Path, name: str) -> Path:
    """Choose a non-existing output path confined to *root*."""
    root = root.resolve()
    cleaned_name = safe_filename(name)
    candidate = _confined_path(root, cleaned_name)
    stem = Path(cleaned_name).stem
    suffix = Path(cleaned_name).suffix
    number = 2
    while candidate.exists():
        candidate = _confined_path(root, f"{stem} ({number}){suffix}")
        number += 1
    return candidate


def deduplicate_requests(requests: Iterable[TrackRequest]) -> DeduplicationResult:
    """Keep the first request for each case-insensitive query or URL."""
    unique_requests: list[TrackRequest] = []
    duplicate_requests: list[TrackRequest] = []
    seen: set[str] = set()
    for request in requests:
        key = (request.url or request.query).strip().casefold()
        if key in seen:
            duplicate_requests.append(request)
        else:
            seen.add(key)
            unique_requests.append(request)
    return DeduplicationResult(unique_requests, duplicate_requests)


def _confined_path(root: Path, name: str) -> Path:
    candidate = (root / name).resolve()
    if candidate.parent != root:
        raise ValueError("Output path must stay inside the selected directory.")
    return candidate
