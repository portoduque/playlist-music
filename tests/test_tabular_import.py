"""Behavioral tests for TXT and CSV imports."""

from playlist_music.imports import parse_csv_file, parse_txt_file, preview_csv_file
from playlist_music.models import CsvColumnMapping


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


def test_previews_csv_rows_and_suggests_portuguese_and_english_headers(tmp_path) -> None:
    source = tmp_path / "songs.csv"
    source.write_text(
        " Música ,Banda,Link,Ignored\nSong 1,Artist 1,https://example.com/1,x\n"
        "Song 2,Artist 2,https://example.com/2,y\n"
        "Song 3,Artist 3,https://example.com/3,z\n"
        "Song 4,Artist 4,https://example.com/4,w\n"
        "Song 5,Artist 5,https://example.com/5,v\n"
        "Song 6,Artist 6,https://example.com/6,u\n",
        encoding="utf-8-sig",
    )

    preview = preview_csv_file(source)

    assert preview.error is None
    assert preview.headers == ("Música", "Banda", "Link", "Ignored")
    assert preview.rows == (
        ("Song 1", "Artist 1", "https://example.com/1", "x"),
        ("Song 2", "Artist 2", "https://example.com/2", "y"),
        ("Song 3", "Artist 3", "https://example.com/3", "z"),
        ("Song 4", "Artist 4", "https://example.com/4", "w"),
        ("Song 5", "Artist 5", "https://example.com/5", "v"),
    )
    assert preview.title_column == "Música"
    assert preview.artist_column == "Banda"
    assert preview.url_column == "Link"


def test_rejects_empty_or_duplicate_csv_headers_in_preview(tmp_path) -> None:
    empty_header = tmp_path / "empty-header.csv"
    empty_header.write_text("title,,url\nSong,Artist,https://example.com\n", encoding="utf-8")
    duplicate_header = tmp_path / "duplicate-header.csv"
    duplicate_header.write_text("title, Title ,url\nSong,Again,https://example.com\n", encoding="utf-8")

    empty_preview = preview_csv_file(empty_header)
    duplicate_preview = preview_csv_file(duplicate_header)

    assert empty_preview.error == "CSV headers cannot be empty."
    assert duplicate_preview.error == "CSV headers must be unique."
    assert empty_preview.headers == ()
    assert duplicate_preview.rows == ()


def test_reports_an_unreadable_csv_preview(tmp_path) -> None:
    preview = preview_csv_file(tmp_path / "missing.csv")

    assert preview.error == "Could not read CSV file."
    assert preview.headers == ()


def test_normalizes_header_separators_and_leaves_unknown_fields_unmapped(tmp_path) -> None:
    source = tmp_path / "aliases.csv"
    source.write_text(
        "t_i_t_l_e,a-r-t-i-s-t,u r l,other\nSong,Artist,https://example.com,x\n",
        encoding="utf-8",
    )

    preview = preview_csv_file(source)

    assert (preview.title_column, preview.artist_column, preview.url_column) == (
        "t_i_t_l_e",
        "a-r-t-i-s-t",
        "u r l",
    )


def test_leaves_missing_or_ambiguous_header_suggestions_unmapped(tmp_path) -> None:
    missing = tmp_path / "missing.csv"
    missing.write_text("one,two\nA,B\n", encoding="utf-8")
    ambiguous = tmp_path / "ambiguous.csv"
    ambiguous.write_text("title,song,artist,url\nA,B,C,https://example.com\n", encoding="utf-8")

    missing_preview = preview_csv_file(missing)
    ambiguous_preview = preview_csv_file(ambiguous)

    assert (missing_preview.title_column, missing_preview.artist_column, missing_preview.url_column) == (
        None,
        None,
        None,
    )
    assert ambiguous_preview.title_column is None
    assert ambiguous_preview.artist_column == "artist"
    assert ambiguous_preview.url_column == "url"


def test_parses_nonstandard_csv_columns_with_a_confirmed_mapping(tmp_path) -> None:
    source = tmp_path / "songs.csv"
    source.write_text(
        "Music name,Performer,Watch link\n\"Song, One\",Artist One,https://example.com/a\n",
        encoding="utf-8",
    )

    result = parse_csv_file(
        source,
        CsvColumnMapping(title_column="Music name", artist_column="Performer", url_column="Watch link"),
    )

    assert [
        (item.line_number, item.query, item.url, item.title, item.artist)
        for item in result.requests
    ] == [
        (2, "Artist One - Song, One", "https://example.com/a", "Song, One", "Artist One")
    ]
    assert result.issues == []


def test_parses_title_only_or_url_only_confirmed_mappings(tmp_path) -> None:
    title_source = tmp_path / "titles.csv"
    title_source.write_text("Track,Performer\nSong One,Artist One\n", encoding="utf-8")
    url_source = tmp_path / "urls.csv"
    url_source.write_text("Watch link\nhttps://example.com/a\n", encoding="utf-8")

    title_result = parse_csv_file(
        title_source,
        CsvColumnMapping(title_column="Track", artist_column="Performer"),
    )
    url_result = parse_csv_file(url_source, CsvColumnMapping(url_column="Watch link"))

    assert [(item.query, item.url, item.title, item.artist) for item in title_result.requests] == [
        ("Artist One - Song One", None, "Song One", "Artist One")
    ]
    assert [(item.query, item.url, item.title) for item in url_result.requests] == [
        ("https://example.com/a", "https://example.com/a", None)
    ]


def test_rejects_invalid_confirmed_csv_mappings(tmp_path) -> None:
    source = tmp_path / "songs.csv"
    source.write_text("Title,Artist,Link\nSong,Artist,https://example.com/a\n", encoding="utf-8")

    missing_result = parse_csv_file(source, CsvColumnMapping())
    duplicate_result = parse_csv_file(
        source,
        CsvColumnMapping(title_column="Title", artist_column="Title"),
    )
    unknown_result = parse_csv_file(source, CsvColumnMapping(title_column="Missing"))

    assert [(issue.line_number, issue.message) for issue in missing_result.issues] == [
        (1, "CSV mapping needs title or url.")
    ]
    assert [(issue.line_number, issue.message) for issue in duplicate_result.issues] == [
        (1, "CSV mapping cannot use one column for multiple fields.")
    ]
    assert [(issue.line_number, issue.message) for issue in unknown_result.issues] == [
        (1, "CSV mapping references an unknown column.")
    ]


def test_nonstandard_mapping_matches_the_canonical_csv_result(tmp_path) -> None:
    mapped_source = tmp_path / "mapped.csv"
    mapped_source.write_text(
        "Musica,Banda,Link\nSong One,Artist One,https://example.com/a\n",
        encoding="utf-8",
    )
    canonical_source = tmp_path / "canonical.csv"
    canonical_source.write_text(
        "title,artist,url\nSong One,Artist One,https://example.com/a\n",
        encoding="utf-8",
    )

    mapped = parse_csv_file(
        mapped_source,
        CsvColumnMapping(title_column="Musica", artist_column="Banda", url_column="Link"),
    )
    canonical = parse_csv_file(canonical_source)

    assert mapped == canonical
