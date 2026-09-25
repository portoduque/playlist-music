"""Behavioral tests for TXT and CSV imports."""

from playlist_music.imports import parse_csv_file, parse_txt_file


def test_parses_utf8_sig_txt_with_the_pasted_text_rules(tmp_path) -> None:
    source = tmp_path / "songs.txt"
    source.write_text("  Song One  \n\nhttps://example.com/song\n", encoding="utf-8-sig")

    result = parse_txt_file(source)

    assert [(item.line_number, item.query, item.url) for item in result.requests] == [
        (1, "Song One", None),
        (3, "https://example.com/song", "https://example.com/song"),
    ]
    assert result.issues == []


def test_parses_reordered_csv_headers_and_quoted_values(tmp_path) -> None:
    source = tmp_path / "songs.csv"
    source.write_text(
        "url,artist,title\nhttps://example.com/a,Artist One,\"Song, One\"\n",
        encoding="utf-8",
    )

    result = parse_csv_file(source)

    assert [
        (item.line_number, item.query, item.url, item.title, item.artist)
        for item in result.requests
    ] == [
        (2, "Artist One - Song, One", "https://example.com/a", "Song, One", "Artist One")
    ]
    assert result.issues == []


def test_reports_invalid_csv_rows_without_discarding_valid_rows(tmp_path) -> None:
    source = tmp_path / "songs.csv"
    source.write_text(
        "title,artist,url\nSong One,,\nSong Two,,https://\n,,\n",
        encoding="utf-8",
    )

    result = parse_csv_file(source)

    assert [
        (item.line_number, item.query, item.url, item.title, item.artist)
        for item in result.requests
    ] == [
        (2, "Song One", None, "Song One", None)
    ]
    assert [(issue.line_number, issue.message) for issue in result.issues] == [
        (3, "URL must include a host.")
    ]


def test_reports_a_csv_without_title_or_url_headers(tmp_path) -> None:
    source = tmp_path / "songs.csv"
    source.write_text("artist\nArtist One\n", encoding="utf-8")

    result = parse_csv_file(source)

    assert result.requests == []
    assert [(issue.line_number, issue.message) for issue in result.issues] == [
        (1, "CSV header needs title or url.")
    ]
