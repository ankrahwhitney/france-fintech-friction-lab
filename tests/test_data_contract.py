from __future__ import annotations

import pandas as pd

from friction_lab.config import DATA_DIR


def test_application_dataset_contract() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet")
    assert len(applications) == 50_000
    assert applications["application_id"].is_unique
    assert applications["application_id"].notna().all()

    prohibited = {"name", "email", "phone", "address", "date_of_birth", "account_number"}
    assert prohibited.isdisjoint(applications.columns)


def test_funnel_dependencies_are_monotonic() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet")
    assert (~applications["document_submitted"] | applications["profile_completed"]).all()
    assert (~applications["verified"] | applications["document_submitted"]).all()
    assert (~applications["funded_7d"] | applications["verified"]).all()


def test_event_history_references_known_applications_and_is_ordered() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet", columns=["application_id"])
    events = pd.read_parquet(DATA_DIR / "events.parquet")
    assert len(events) >= 140_000
    assert set(events["application_id"]).issubset(set(applications["application_id"]))
    ordered = events.sort_values(["application_id", "event_at"])
    assert ordered.index.equals(events.index)
