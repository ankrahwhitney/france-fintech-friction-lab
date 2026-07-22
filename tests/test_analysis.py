from __future__ import annotations

import json

import pandas as pd
import pytest

from friction_lab.config import ARTIFACT_DIR, load_config


def test_funnel_counts_only_decrease() -> None:
    funnel = pd.read_csv(ARTIFACT_DIR / "funnel.csv")
    assert funnel["applications"].is_monotonic_decreasing
    assert (funnel["applications"] >= 0).all()
    assert funnel.iloc[0]["start_conversion_pct"] == pytest.approx(100.0)


def test_stage_durations_come_from_event_stream() -> None:
    durations = pd.read_csv(ARTIFACT_DIR / "stage_durations.csv")
    assert list(durations["transition_order"]) == [1, 2, 3, 4]
    assert (durations["applications"] > 0).all()
    assert (durations["median_minutes"] > 0).all()
    assert (durations["p90_minutes"] >= durations["median_minutes"]).all()


def test_review_latency_exposes_operational_queue_effect() -> None:
    latency = pd.read_csv(ARTIFACT_DIR / "review_latency.csv").set_index("verification_path")
    assert {"Straight-through", "Manual review"}.issubset(latency.index)
    assert latency.loc["Manual review", "median_minutes"] > (
        5 * latency.loc["Straight-through", "median_minutes"]
    )


# The two assertions below pin the published recommendation. They are deliberate
# regression guards: if a config change flips the ranking, CI fails and the README,
# docs and dashboard narrative must be updated in the same change.
def test_decision_outputs_are_complete() -> None:
    scorecard = pd.read_csv(ARTIFACT_DIR / "intervention_scorecard.csv")
    required = {
        "intervention",
        "expected_funded_lift_pp",
        "incremental_funded_per_10k_mean",
        "impact_score",
        "guardrail_score",
        "speed_score",
        "confidence_score",
        "decision_score",
    }
    assert required.issubset(scorecard.columns)
    assert len(scorecard) == 3
    assert scorecard["decision_score"].between(0, 100).all()
    assert scorecard.iloc[0]["intervention"] == "Document-readiness checklist"


def test_weight_sensitivity_exposes_ranking_changes() -> None:
    sensitivity = pd.read_csv(ARTIFACT_DIR / "weight_sensitivity.csv")
    winners = sensitivity.loc[sensitivity["winner"], ["weight_profile", "intervention"]]

    assert len(winners) == 5
    assert winners["intervention"].nunique() == 2
    speed_winner = winners.loc[winners["weight_profile"] == "Speed first", "intervention"].item()
    assert speed_winner == "Contextual data-use explainer"


def test_summary_matches_generated_outputs() -> None:
    summary = json.loads((ARTIFACT_DIR / "summary.json").read_text(encoding="utf-8"))
    expected_applications = int(load_config()["project"]["generated_applications"])
    assert summary["applications"] == expected_applications
    assert summary["events"] >= 140_000
    assert summary["experiment_total_sample"] == 2 * summary["experiment_sample_per_arm"]
    assert summary["funded_secondary_total_sample"] == (
        2 * summary["funded_secondary_sample_per_arm"]
    )
    assert summary["funded_secondary_days_full_traffic"] > summary["experiment_days_full_traffic"]
    assert summary["data_status"] == "Fully synthetic; no customer or company data"


def test_data_quality_report_has_no_contract_failures() -> None:
    quality = json.loads((ARTIFACT_DIR / "data_quality.json").read_text(encoding="utf-8"))
    assert quality["duplicate_application_ids"] == 0
    assert quality["events_with_unknown_application_id"] == 0
    assert quality["events_with_missing_timestamp"] == 0
    assert quality["event_stream_ordered"] is True
    assert quality["profile_dependency_violations"] == 0
    assert quality["verification_dependency_violations"] == 0
    assert quality["funding_dependency_violations"] == 0
    assert quality["funded_7d_window_violations"] == 0
    assert quality["prohibited_pii_columns_present"] == []
