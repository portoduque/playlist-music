"""Completion feedback without real downloads or native file opening."""

from playlist_music.artifacts import ArtifactPaths
from playlist_music.app import PlaylistMusicApp
from playlist_music.models import AcquisitionResult, QueueItemResult, QueueResult, TrackRequest
from playlist_music.service import ServiceResult
from playlist_music.ui_state import InputState, completion_actions


class _Control:
    def __init__(self) -> None:
        self.state = "disabled"

    def configure(self, **options: str) -> None:
        self.state = options.get("state", self.state)

    def cget(self, option: str) -> str:
        assert option == "state"
        return self.state


class _ActionsFrame:
    def __init__(self) -> None:
        self.visible = False

    def grid(self) -> None:
        self.visible = True

    def grid_remove(self) -> None:
        self.visible = False


class _Status:
    def __init__(self) -> None:
        self.value = ""

    def set(self, value: str) -> None:
        self.value = value

    def get(self) -> str:
        return self.value


def _completion_app(output) -> PlaylistMusicApp:
    app = object.__new__(PlaylistMusicApp)
    app.status = _Status()
    app.state = InputState(output_folder=output)
    app._active_output_folder = None
    app._folder_to_open = None
    app._playlist_to_open = None
    app.create_button = _Control()
    app.open_folder_button = _Control()
    app.open_playlist_button = _Control()
    app.actions_frame = _ActionsFrame()
    return app


def _item(status: str, line_number: int) -> QueueItemResult:
    return QueueItemResult(TrackRequest(line_number, f"Song {line_number}"), status, None)


def test_summarizes_success_failure_and_duplicates() -> None:
    result = ServiceResult(
        True,
        None,
        QueueResult([_item("succeeded", 1), _item("failed", 2), _item("duplicate", 3)]),
        None,
    )

    actions = completion_actions(result, None)

    assert actions.message == (
        "Finished: 1 downloaded, 1 failed, 1 duplicate skipped. "
        "See resultado.txt for the reason for each failed track."
    )
    assert actions.folder is None
    assert actions.playlist is None


def test_summarizes_zero_successes() -> None:
    result = ServiceResult(
        True,
        None,
        QueueResult([_item("failed", 1), _item("duplicate", 2)]),
        None,
    )

    actions = completion_actions(result, None)

    assert actions.message == (
        "Finished: no tracks downloaded; 1 failed, 1 duplicate skipped. "
        "See resultado.txt for the reason for each failed track."
    )


def test_summarizes_metadata_warnings_without_counting_a_failure() -> None:
    request = TrackRequest(1, "Song")
    result = ServiceResult(
        True,
        None,
        QueueResult(
            [
                QueueItemResult(
                    request,
                    "succeeded",
                    AcquisitionResult(request, True, None, None, None, ("Tag warning",)),
                )
            ]
        ),
        None,
    )

    actions = completion_actions(result, None)

    assert actions.message == "Finished: 1 downloaded, 0 failed, 0 duplicates skipped; 1 metadata warning."


def test_only_offers_paths_confined_to_the_completed_output(tmp_path) -> None:
    output = tmp_path / "playlist"
    output.mkdir()
    playlist = output / "playlist.m3u8"
    playlist.write_text("#EXTM3U\n", encoding="utf-8")
    outside = tmp_path / "outside.m3u8"
    outside.write_text("#EXTM3U\n", encoding="utf-8")
    result = ServiceResult(True, None, QueueResult([]), ArtifactPaths(outside, outside, outside))

    actions = completion_actions(result, output)

    assert actions.folder == output.resolve()
    assert actions.playlist is None


def test_offers_the_generated_playlist_inside_the_output(tmp_path) -> None:
    output = tmp_path / "playlist"
    output.mkdir()
    playlist = output / "playlist.m3u8"
    playlist.write_text("#EXTM3U\n", encoding="utf-8")
    result = ServiceResult(True, None, QueueResult([]), ArtifactPaths(playlist, playlist, playlist))

    actions = completion_actions(result, output)

    assert actions.folder == output.resolve()
    assert actions.playlist == playlist.resolve()


def test_offers_the_created_playlist_subfolder(tmp_path) -> None:
    output = tmp_path / "library"
    playlist_folder = output / "playlist"
    playlist_folder.mkdir(parents=True)
    playlist = playlist_folder / "playlist.m3u8"
    playlist.write_text("#EXTM3U\n", encoding="utf-8")
    result = ServiceResult(
        True,
        None,
        QueueResult([]),
        ArtifactPaths(playlist, playlist, playlist),
        playlist_folder,
    )

    actions = completion_actions(result, output)

    assert actions.folder == playlist_folder.resolve()
    assert actions.playlist == playlist.resolve()


def test_completion_reenables_creation_and_shows_safe_actions(tmp_path) -> None:
    output = tmp_path / "playlist"
    output.mkdir()
    playlist = output / "playlist.m3u8"
    playlist.write_text("#EXTM3U\n", encoding="utf-8")
    result = ServiceResult(True, None, QueueResult([]), ArtifactPaths(playlist, playlist, playlist))
    app = _completion_app(output)
    app.create_button.configure(state="disabled")

    app._show_completion(result)

    assert app.status.get() == "Finished: no tracks downloaded; 0 failed, 0 duplicates skipped."
    assert app.create_button.cget("state") == "normal"
    assert app.open_folder_button.cget("state") == "normal"
    assert app.open_playlist_button.cget("state") == "normal"


def test_unexpected_error_reenables_creation(tmp_path) -> None:
    app = _completion_app(tmp_path)
    app.create_button.configure(state="disabled")

    app._show_error("Unexpected failure")

    assert app.status.get() == "Unexpected failure"
    assert app.create_button.cget("state") == "normal"
