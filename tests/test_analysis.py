from __future__ import annotations

import json

import pandas as pd

from friction_lab.config import ARTIFACT_DIR


def test_funnel_counts_only_decrease() -> None:
    funnel = pd.read_csv(ARTIFACT_DIR / "funnel.csv")
    assert funnel["applications"].is_monotonic_decreasing
    assert (funnel["applications"] >= 0).all()
    assert funnel.iloc[0]["start_conversion_pct"] == 100.0


def test_stage_durations_come_from_event_stream() -> None:
    durations = pd.read_csv(ARTIFACT_DIR / "stage_durations.csv")
    assert list(durations["transition_order"]) == [1, 2, 3, 4]
    assert (durations["applications"] > 0).all()
    assert (durations["median_minutes"] > 0).all()
    assert (durations["p90_minutes"] >= durations["median_minutes"]).all()


# The two assertions below pin the published recommendation. They are deliberate
# regression guards: if a config change flips the ranking, CI fails and the README,
# docs and dashboard narrative must be updated in the same change.
def test_decision_outputs_are_complete() -> None:
    scorecard = pd.read_csv(ARTIFACT_DIR / "intervention_scorecard.csv")
    required = {
        "intervention",
        "expected_funded_lift_pp",
        "incremental_funded_per_10k_mean",
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
    assert summary["applications"] == 50_000
    assert summary["events"] >= 140_000
    assert summary["experiment_total_sample"] == 2 * summary["experiment_sample_per_arm"]
    assert summary["data_status"] == "Fully synthetic; no customer or company data"
