"""Import supported playlist inputs into normalized requests."""

import csv
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from playlist_music.models import ImportIssue, ImportResult, TrackRequest


URL_PREFIX = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")


def parse_pasted_text(text: str) -> ImportResult:
    """Parse one search query or HTTP(S) URL per non-empty line."""
    requests: list[TrackRequest] = []
    issues: list[ImportIssue] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        value = raw_line.strip()
        if not value:
            continue

        _append_request(value, line_number, value, requests, issues)

    if not requests and not issues:
        issues.append(ImportIssue(None, "Add at least one song query or URL."))

    return ImportResult(requests, issues)


def parse_txt_file(path: Path) -> ImportResult:
    """Read a UTF-8 TXT file using the pasted-text rules."""
    try:
        return parse_pasted_text(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError):
        return ImportResult([], [ImportIssue(None, "Could not read TXT file.")])


def parse_csv_file(path: Path) -> ImportResult:
    """Read CSV rows containing title, artist, and optional URL columns."""
    requests: list[TrackRequest] = []
    issues: list[ImportIssue] = []
    try:
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            headers = {name.strip().lower(): name for name in reader.fieldnames or []}
            if not {"title", "url"} & headers.keys():
                return ImportResult([], [ImportIssue(1, "CSV header needs title or url.")])

            for row in reader:
                line_number = reader.line_num
                title = _csv_value(row, headers, "title")
                artist = _csv_value(row, headers, "artist")
                url = _csv_value(row, headers, "url")
                if not title and not artist and not url:
                    continue
                if not title and not url:
                    issues.append(ImportIssue(line_number, "CSV row needs title or url."))
                    continue
                query = f"{artist} - {title}" if artist and title else title or url
                _append_request(
                    url or query,
                    line_number,
                    query,
                    requests,
                    issues,
                    title=title or None,
                    artist=artist or None,
                )
    except (csv.Error, OSError, UnicodeError):
        return ImportResult([], [ImportIssue(None, "Could not read CSV file.")])

    return ImportResult(requests, issues)


def parse_m3u_file(path: Path) -> ImportResult:
    """Read an M3U/M3U8 file, ignoring comment lines."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return ImportResult([], [ImportIssue(None, "Could not read M3U file.")])

    lines = ("" if line.lstrip().startswith("#") else line for line in text.splitlines())
    return parse_pasted_text("\n".join(lines))


def parse_json_file(path: Path) -> ImportResult:
    """Read a list of strings or simple track objects from JSON."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ImportResult([], [ImportIssue(None, "Could not read JSON file.")])

    if not isinstance(payload, list):
        return ImportResult([], [ImportIssue(None, "JSON root must be a list.")])

    requests: list[TrackRequest] = []
    issues: list[ImportIssue] = []
    for item_number, item in enumerate(payload, start=1):
        if isinstance(item, str):
            value = item.strip()
            if value:
                _append_request(value, item_number, value, requests, issues)
            else:
                issues.append(ImportIssue(item_number, "JSON item needs title or url."))
            continue
        if not isinstance(item, dict):
            issues.append(ImportIssue(item_number, "JSON item must be a string or object."))
            continue

        values = [item.get(name) for name in ("title", "artist", "url")]
        if any(value is not None and not isinstance(value, str) for value in values):
            issues.append(ImportIssue(item_number, "JSON title, artist, and url must be strings."))
            continue
        title, artist, url = ((value or "").strip() for value in values)
        if not title and not url:
            issues.append(ImportIssue(item_number, "JSON item needs title or url."))
            continue
        query = f"{artist} - {title}" if artist and title else title or url
        _append_request(
            url or query,
            item_number,
            query,
            requests,
            issues,
            title=title or None,
            artist=artist or None,
        )

    return ImportResult(requests, issues)


def _append_request(
    value: str,
    line_number: int,
    query: str,
    requests: list[TrackRequest],
    issues: list[ImportIssue],
    *,
    title: str | None = None,
    artist: str | None = None,
) -> None:
    if URL_PREFIX.match(value):
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"}:
            issues.append(ImportIssue(line_number, "URL must use HTTP or HTTPS."))
            return
        if not parsed.netloc:
            issues.append(ImportIssue(line_number, "URL must include a host."))
            return
        requests.append(TrackRequest(line_number, query, value, title, artist))
        return
    requests.append(TrackRequest(line_number, query, title=title, artist=artist))


def _csv_value(row: dict[str, str | None], headers: dict[str, str], name: str) -> str:
    return (row.get(headers.get(name, "")) or "").strip()
