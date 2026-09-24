"""Import supported playlist inputs into normalized requests."""

import re
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

        if URL_PREFIX.match(value):
            parsed = urlsplit(value)
            if parsed.scheme not in {"http", "https"}:
                issues.append(ImportIssue(line_number, "URL must use HTTP or HTTPS."))
                continue
            if not parsed.netloc:
                issues.append(ImportIssue(line_number, "URL must include a host."))
                continue
            requests.append(TrackRequest(line_number, value, value))
            continue

        requests.append(TrackRequest(line_number, value))

    if not requests and not issues:
        issues.append(ImportIssue(None, "Add at least one song query or URL."))

    return ImportResult(requests, issues)
