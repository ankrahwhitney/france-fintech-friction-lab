from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


def test_dashboard_renders_without_exceptions() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
    assert not app.exception


def test_dashboard_shows_recommendation_from_artifacts() -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
    rendered = " ".join(block.value for block in app.markdown)
    assert "Portfolio simulation" in rendered
