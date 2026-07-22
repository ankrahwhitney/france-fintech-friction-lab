from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from friction_lab.config import ARTIFACT_DIR

APP_PATH = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


@pytest.fixture(scope="module")
def app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=60).run()


def test_dashboard_renders_without_exceptions(app: AppTest) -> None:
    assert not app.exception


def test_dashboard_shows_recommendation_from_artifacts(app: AppTest) -> None:
    scorecard = pd.read_csv(ARTIFACT_DIR / "intervention_scorecard.csv")
    top = scorecard.sort_values("decision_score", ascending=False).iloc[0]
    rendered = " ".join(block.value for block in app.markdown)
    assert str(top["intervention"]) in rendered
    assert "Portfolio simulation" in rendered


@pytest.mark.parametrize(
    ("view", "expected_text"),
    [
        ("Executive decision", "What would change the decision?"),
        ("Funnel diagnosis", "Verification latency by operating path"),
        ("Segment drill-down", "Segments are diagnostic, not causal"),
        ("Test design", "Validity checks before reading the result"),
    ],
)
def test_every_dashboard_view_renders(view: str, expected_text: str) -> None:
    app = AppTest.from_file(str(APP_PATH), default_timeout=60).run()
    app.radio[0].set_value(view).run()
    assert not app.exception
    rendered = " ".join(block.value for block in [*app.markdown, *app.subheader, *app.caption])
    assert expected_text in rendered
