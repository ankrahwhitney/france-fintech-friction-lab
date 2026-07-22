from __future__ import annotations

import numpy as np
import pandas as pd

from friction_lab.config import DATA_DIR, load_config


def test_application_dataset_contract() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet")
    expected_applications = int(load_config()["project"]["generated_applications"])
    assert len(applications) == expected_applications
    assert applications["application_id"].is_unique
    assert applications["application_id"].notna().all()

    prohibited = {"name", "email", "phone", "address", "date_of_birth", "account_number"}
    columns = {column.lower() for column in applications.columns}
    assert prohibited.isdisjoint(columns)


def test_funnel_dependencies_are_monotonic() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet")
    assert (~applications["document_submitted"] | applications["profile_completed"]).all()
    assert (~applications["verified"] | applications["document_submitted"]).all()
    assert (~applications["funded"] | applications["verified"]).all()
    assert (~applications["funded_7d"] | applications["verified"]).all()


def test_funded_within_seven_days_is_computed_from_timestamps() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet")
    expected = applications["funded"] & (
        applications["first_funded_at"] <= applications["started_at"] + np.timedelta64(7, "D")
    )
    pd.testing.assert_series_equal(applications["funded_7d"], expected, check_names=False)
    assert (applications.loc[applications["funded_7d"], "first_funded_at"].notna()).all()


def test_manual_review_creates_a_real_verification_delay() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet")
    verified = applications.loc[applications["verified"]].copy()
    duration_minutes = (
        verified["verification_completed_at"] - verified["document_submitted_at"]
    ).dt.total_seconds() / 60
    reviewed_median = duration_minutes.loc[verified["manual_review"]].median()
    straight_through_median = duration_minutes.loc[~verified["manual_review"]].median()
    assert reviewed_median > 5 * straight_through_median


def test_event_history_references_known_applications_and_is_ordered() -> None:
    applications = pd.read_parquet(DATA_DIR / "applications.parquet", columns=["application_id"])
    events = pd.read_parquet(DATA_DIR / "events.parquet")
    assert len(events) >= 140_000
    assert set(events["application_id"]).issubset(set(applications["application_id"]))
    ordered = events.sort_values(["application_id", "event_at"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(events.reset_index(drop=True), ordered)
