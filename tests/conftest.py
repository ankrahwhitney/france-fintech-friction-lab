from __future__ import annotations

import pytest

from friction_lab.config import ARTIFACT_DIR, DATA_DIR


@pytest.fixture(scope="session", autouse=True)
def ensure_pipeline_outputs() -> None:
    """Regenerate data and artifacts on a fresh clone so tests are self-sufficient."""
    required = [
        DATA_DIR / "applications.parquet",
        DATA_DIR / "events.parquet",
        ARTIFACT_DIR / "summary.json",
        ARTIFACT_DIR / "funnel.csv",
        ARTIFACT_DIR / "segment_friction.csv",
        ARTIFACT_DIR / "weekly_kpis.csv",
        ARTIFACT_DIR / "stage_durations.csv",
        ARTIFACT_DIR / "intervention_scorecard.csv",
        ARTIFACT_DIR / "weight_sensitivity.csv",
    ]
    if not all(path.exists() for path in required):
        from friction_lab.generate import generate_datasets
        from friction_lab.metrics import build_analysis_artifacts

        generate_datasets()
        build_analysis_artifacts()
