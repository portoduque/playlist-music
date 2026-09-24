"""Behavioral tests for M3U and JSON imports."""

from playlist_music.imports import parse_json_file, parse_m3u_file


def test_parses_bom_m3u_and_ignores_comments(tmp_path) -> None:
    source = tmp_path / "songs.m3u8"
    source.write_text(
        "#EXTM3U\nhttps://example.com/song\n#EXTINF:123,Artist - Song\nmusic/song.mp3\n",
        encoding="utf-8-sig",
    )

    result = parse_m3u_file(source)

    assert [(item.line_number, item.query, item.url) for item in result.requests] == [
        (2, "https://example.com/song", "https://example.com/song"),
        (4, "music/song.mp3", None),
    ]
    assert result.issues == []


def test_parses_json_strings_and_track_objects(tmp_path) -> None:
    source = tmp_path / "songs.json"
    source.write_text(
        '["Song One", {"title": "Song Two", "artist": "Artist Two", '
        '"url": "https://example.com/two"}]',
        encoding="utf-8",
    )

    result = parse_json_file(source)

    assert [(item.line_number, item.query, item.url) for item in result.requests] == [
        (1, "Song One", None),
        (2, "Artist Two - Song Two", "https://example.com/two"),
    ]
    assert result.issues == []


def test_keeps_valid_json_items_and_reports_invalid_items(tmp_path) -> None:
    source = tmp_path / "songs.json"
    source.write_text(
        '["Song One", {"artist": "Artist only"}, 7, {"title": "Song Two"}]',
        encoding="utf-8",
    )

    result = parse_json_file(source)

    assert [item.query for item in result.requests] == ["Song One", "Song Two"]
    assert [(issue.line_number, issue.message) for issue in result.issues] == [
        (2, "JSON item needs title or url."),
        (3, "JSON item must be a string or object."),
    ]


def test_reports_malformed_and_non_list_json(tmp_path) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text("[", encoding="utf-8")
    object_root = tmp_path / "object.json"
    object_root.write_text('{"title": "Song"}', encoding="utf-8")

    assert parse_json_file(malformed).issues[0].message == "Could not read JSON file."
    assert parse_json_file(object_root).issues[0].message == "JSON root must be a list."
