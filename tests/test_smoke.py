"""Smoke coverage for the executable package."""

from __future__ import annotations

import subprocess
import sys


def test_module_runs_and_explains_that_the_app_is_not_ready() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "playlist_music"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "not ready" in result.stdout.lower()
