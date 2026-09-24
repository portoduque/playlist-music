"""Behavioral tests for pasted playlist text."""

from playlist_music.imports import parse_pasted_text


def test_parses_queries_and_https_urls_in_source_order() -> None:
    result = parse_pasted_text(
        "  Caetano Veloso - Sozinho  \n\nhttps://example.com/song\nBeyonc\u00e9 - Halo\n"
    )

    assert [(item.line_number, item.query, item.url) for item in result.requests] == [
        (1, "Caetano Veloso - Sozinho", None),
        (3, "https://example.com/song", "https://example.com/song"),
        (4, "Beyonc\u00e9 - Halo", None),
    ]
    assert result.issues == []


def test_reports_invalid_url_without_discarding_valid_lines() -> None:
    result = parse_pasted_text("Song One\nhttps://\nSong Two")

    assert [item.query for item in result.requests] == ["Song One", "Song Two"]
    assert [(issue.line_number, issue.message) for issue in result.issues] == [
        (2, "URL must include a host.")
    ]


def test_reports_when_input_has_no_useful_lines() -> None:
    result = parse_pasted_text(" \n\t\n")

    assert result.requests == []
    assert [(issue.line_number, issue.message) for issue in result.issues] == [
        (None, "Add at least one song query or URL.")
    ]
