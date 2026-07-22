from __future__ import annotations

import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_pipeline_outputs() -> None:
    """Always rebuild so stale, truncated or cloud-placeholder outputs cannot pass tests."""
    from friction_lab.generate import generate_datasets
    from friction_lab.metrics import build_analysis_artifacts

    generate_datasets()
    build_analysis_artifacts()
