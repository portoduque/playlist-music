"""Behavioral tests for safe output names and request deduplication."""

from playlist_music.models import TrackRequest
from playlist_music.output import allocate_output_path, deduplicate_requests, safe_filename


def test_sanitizes_windows_reserved_names_and_unsafe_characters() -> None:
    assert safe_filename('  ../CON<>:"/\\|?*. ') == "CON_"
    assert safe_filename("Title. ") == "Title"
    assert safe_filename("   ") == "track"


def test_output_paths_cannot_escape_the_selected_directory(tmp_path) -> None:
    path = allocate_output_path(tmp_path, "../outside.mp3")

    assert path.parent == tmp_path.resolve()
    assert path.name == "outside.mp3"


def test_output_paths_reject_absolute_components_and_keep_unicode(tmp_path) -> None:
    path = allocate_output_path(tmp_path, "C:\\outside\\Beyonc\u00e9.mp3")

    assert path.parent == tmp_path.resolve()
    assert "Beyonc\u00e9" in path.name


def test_output_path_collisions_receive_deterministic_suffixes(tmp_path) -> None:
    (tmp_path / "song.mp3").touch()
    (tmp_path / "song (2).mp3").touch()

    assert allocate_output_path(tmp_path, "song.mp3").name == "song (3).mp3"


def test_deduplicates_requests_while_preserving_the_first_occurrence() -> None:
    result = deduplicate_requests(
        [
            TrackRequest(1, "Song One"),
            TrackRequest(2, " song one "),
            TrackRequest(3, "Song Two", "https://example.com/two"),
            TrackRequest(4, "Other title", "https://example.com/two"),
        ]
    )

    assert [item.line_number for item in result.unique_requests] == [1, 3]
    assert [item.line_number for item in result.duplicate_requests] == [2, 4]
