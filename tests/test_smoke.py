"""Smoke coverage for the executable package."""

from playlist_music import __main__


def test_module_starts_the_local_app(monkeypatch) -> None:
    started = []
    monkeypatch.setattr(__main__, "run_app", lambda: started.append(True))

    __main__.main()

    assert started == [True]
