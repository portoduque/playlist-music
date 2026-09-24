"""State for the minimal input screen without creating a Tk window."""

from pathlib import Path
import tkinter as tk

from playlist_music.app import PlaylistMusicApp
from playlist_music.ui_state import InputState


def test_starts_with_only_the_safe_defaults() -> None:
    state = InputState()

    assert state.quality == "recommended"
    assert state.advanced_open is False
    assert state.import_summary == "Add music queries or URLs to begin."


def test_pasted_text_shows_valid_and_invalid_counts() -> None:
    state = InputState()

    state.set_pasted_text("Song\nftp://invalid\n\nhttps://example.com/song")

    assert len(state.imported.requests) == 2
    assert len(state.imported.issues) == 1
    assert state.import_summary == "2 valid, 1 invalid."


def test_can_select_output_folder_quality_and_advanced_options() -> None:
    state = InputState()

    state.set_output_folder(Path("C:/Music"))
    state.set_quality("compact")
    state.toggle_advanced()

    assert state.output_folder == Path("C:/Music")
    assert state.quality == "compact"
    assert state.advanced_open is True


def test_rejects_an_unknown_quality() -> None:
    state = InputState()

    try:
        state.set_quality("lossless")
    except ValueError as error:
        assert str(error) == "Unsupported quality: lossless"
    else:
        raise AssertionError("Unknown quality must be rejected.")


def test_builds_the_native_input_screen() -> None:
    root = tk.Tk()
    root.withdraw()
    app = PlaylistMusicApp(root)

    try:
        assert root.title() == "Playlist Music"
        assert app.text.winfo_exists() == 1
    finally:
        root.destroy()
