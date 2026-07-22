from __future__ import annotations

import json
from pathlib import Path
from statistics import NormalDist
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from .config import ARTIFACT_DIR, DATA_DIR, ROOT, load_config


def _query_sql(connection: duckdb.DuckDBPyConnection, name: str) -> pd.DataFrame:
    path = ROOT / "sql" / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. The analysis expects the full repository layout (sql/, config/) "
            "and an editable install from the repository root: pip install -e ."
        )
    return connection.execute(path.read_text(encoding="utf-8")).fetch_df()


def _experiment_sample_size(base_rate: float, lift_pp: float, alpha: float, power: float) -> int:
    if not 0 < base_rate < 1:
        raise ValueError(f"base rate must be in (0, 1), got {base_rate}")
    if lift_pp <= 0:
        raise ValueError(f"minimum detectable lift must be positive, got {lift_pp}")
    if not 0 < alpha < 1:
        raise ValueError(f"alpha must be in (0, 1), got {alpha}")
    if not 0 < power < 1:
        raise ValueError(f"power must be in (0, 1), got {power}")
    p1 = base_rate
    p2 = base_rate + lift_pp / 100
    if p2 >= 1:
        raise ValueError(f"base rate plus minimum detectable lift must be below 1, got {p2}")
    p_bar = (p1 + p2) / 2
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_power = NormalDist().inv_cdf(power)
    numerator = (
        z_alpha * np.sqrt(2 * p_bar * (1 - p_bar))
        + z_power * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    ) ** 2
    return int(np.ceil(numerator / ((p2 - p1) ** 2)))


def _simulate_interventions(
    funnel: pd.DataFrame, applications: pd.DataFrame, config: dict[str, Any]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    counts = dict(zip(funnel["stage"], funnel["applications"], strict=True))
    expected_stages = [
        "Application started",
        "Profile completed",
        "Document submitted",
        "Verification completed",
        "Funded within 7 days",
    ]
    missing_stages = [stage for stage in expected_stages if stage not in counts]
    if missing_stages:
        raise KeyError(
            f"Funnel is missing stages {missing_stages}; these labels must match sql/01_funnel.sql."
        )
    stage_rates = {
        "profile_completed": counts["Profile completed"] / counts["Application started"],
        "document_submitted": counts["Document submitted"] / counts["Profile completed"],
        "verification_completed": counts["Verification completed"] / counts["Document submitted"],
        "account_funded": counts["Funded within 7 days"] / counts["Verification completed"],
    }
    baseline_funded_rate = float(applications["funded_7d"].mean())
    baseline_support_rate = float(applications["support_contact"].mean())
    baseline_manual_rate = float(applications["manual_review"].mean())
    # Share of started applications that incur an intervention's variable cost.
    cost_population_shares = {
        "application_started": 1.0,
        "profile_completed": float(applications["profile_completed"].mean()),
        "failed_verification": float(
            (applications["document_submitted"] & ~applications["verified"]).mean()
        ),
    }
    economics = config["unit_economics"]
    monthly_apps = int(economics["monthly_applications"])
    rng = np.random.default_rng(int(config["project"]["seed"]) + 41)

    outputs: list[dict[str, Any]] = []
    distributions: list[pd.DataFrame] = []
    for intervention in config["interventions"]:
        lift = intervention["stage_lift_pp"]
        lift_samples = (
            rng.triangular(lift["low"], lift["most_likely"], lift["high"], size=10_000) / 100
        )
        simulated_rates = stage_rates.copy()
        target = intervention["target_stage"]
        simulated_target = np.clip(simulated_rates[target] + lift_samples, 0, 1)
        other_product = np.prod(
            [rate for stage, rate in simulated_rates.items() if stage != target]
        )
        funded_rate_samples = simulated_target * other_product
        funded_rate_delta = funded_rate_samples - baseline_funded_rate
        incremental_funded_per_10k = 10_000 * funded_rate_delta
        monthly_incremental_funded = monthly_apps * funded_rate_delta

        support_rate = np.clip(baseline_support_rate + intervention["support_delta_pp"] / 100, 0, 1)
        manual_rate = np.clip(
            baseline_manual_rate + intervention["manual_review_delta_pp"] / 100, 0, 1
        )
        monthly_guardrail_cost_delta = monthly_apps * (
            (support_rate - baseline_support_rate) * economics["support_contact_cost_eur"]
            + (manual_rate - baseline_manual_rate) * economics["manual_review_cost_eur"]
        )
        cost_share = cost_population_shares[intervention["cost_population"]]
        annual_net_value = (
            12
            * (
                monthly_incremental_funded * economics["funded_account_12m_contribution_eur"]
                - monthly_guardrail_cost_delta
                - monthly_apps * cost_share * intervention["variable_cost_eur_per_application"]
            )
            - intervention["fixed_cost_eur"]
        )

        outputs.append(
            {
                "intervention_key": intervention["key"],
                "intervention": intervention["name"],
                "target_stage": target,
                "expected_funded_lift_pp": round(
                    100 * (float(np.mean(funded_rate_samples)) - baseline_funded_rate), 2
                ),
                "incremental_funded_per_10k_mean": round(
                    float(np.mean(incremental_funded_per_10k)), 1
                ),
                "incremental_funded_per_10k_p10": round(
                    float(np.quantile(incremental_funded_per_10k, 0.10)), 1
                ),
                "incremental_funded_per_10k_p90": round(
                    float(np.quantile(incremental_funded_per_10k, 0.90)), 1
                ),
                "annual_net_value_mean_eur": round(float(np.mean(annual_net_value)), 0),
                "annual_net_value_p10_eur": round(float(np.quantile(annual_net_value, 0.10)), 0),
                "annual_net_value_p90_eur": round(float(np.quantile(annual_net_value, 0.90)), 0),
                "support_delta_pp": intervention["support_delta_pp"],
                "manual_review_delta_pp": intervention["manual_review_delta_pp"],
                "delivery_weeks": intervention["delivery_weeks"],
                "evidence_confidence": intervention["evidence_confidence"],
            }
        )
        distributions.append(
            pd.DataFrame(
                {
                    "intervention": intervention["name"],
                    "incremental_funded_per_10k": incremental_funded_per_10k,
                    "annual_net_value_eur": annual_net_value,
                }
            )
        )

    scorecard = pd.DataFrame(outputs)
    anchors = config["decision_score_anchors"]
    impact = scorecard["expected_funded_lift_pp"]
    # Absolute anchors make scores stable when the option set changes. Values beyond
    # the cap saturate instead of giving every other candidate a different score.
    impact_score = (impact / anchors["conversion_impact_pp_cap"]).clip(0, 1)
    guardrail_penalty = scorecard["support_delta_pp"].clip(lower=0) + scorecard[
        "manual_review_delta_pp"
    ].clip(lower=0)
    guardrail_score = (1 - guardrail_penalty / anchors["guardrail_penalty_pp_cap"]).clip(0, 1)
    fastest = float(anchors["fastest_delivery_weeks"])
    slowest = float(anchors["slowest_delivery_weeks"])
    speed_score = (1 - (scorecard["delivery_weeks"] - fastest) / (slowest - fastest)).clip(0, 1)
    scorecard["impact_score"] = (100 * impact_score).round(1)
    scorecard["guardrail_score"] = (100 * guardrail_score).round(1)
    scorecard["speed_score"] = (100 * speed_score).round(1)
    scorecard["confidence_score"] = (100 * scorecard["evidence_confidence"]).round(1)
    weights = config["decision_weights"]
    scorecard["decision_score"] = (
        100
        * (
            weights["conversion_impact"] * impact_score
            + weights["guardrails"] * guardrail_score
            + weights["speed_to_learn"] * speed_score
            + weights["evidence_confidence"] * scorecard["evidence_confidence"]
        )
    ).round(1)

    weight_profiles = {
        "Balanced": (
            weights["conversion_impact"],
            weights["guardrails"],
            weights["speed_to_learn"],
            weights["evidence_confidence"],
        ),
        "Growth first": (0.65, 0.15, 0.10, 0.10),
        "Operations first": (0.25, 0.50, 0.10, 0.15),
        "Speed first": (0.25, 0.20, 0.45, 0.10),
        "Evidence first": (0.25, 0.20, 0.10, 0.45),
    }
    sensitivity_records: list[dict[str, Any]] = []
    for profile, profile_weights in weight_profiles.items():
        profile_score = 100 * (
            profile_weights[0] * impact_score
            + profile_weights[1] * guardrail_score
            + profile_weights[2] * speed_score
            + profile_weights[3] * scorecard["evidence_confidence"]
        )
        winner_index = int(profile_score.idxmax())
        for index, value in profile_score.items():
            sensitivity_records.append(
                {
                    "weight_profile": profile,
                    "intervention": scorecard.loc[index, "intervention"],
                    "decision_score": round(float(value), 1),
                    "winner": index == winner_index,
                }
            )

    scorecard = scorecard.sort_values("decision_score", ascending=False).reset_index(drop=True)
    distribution = pd.concat(distributions, ignore_index=True)
    sensitivity = pd.DataFrame(sensitivity_records)
    return scorecard, distribution, sensitivity


def build_analysis_artifacts(
    data_dir: Path = DATA_DIR, output_dir: Path = ARTIFACT_DIR
) -> dict[str, Any]:
    config = load_config()
    applications = pd.read_parquet(data_dir / "applications.parquet")
    events = pd.read_parquet(data_dir / "events.parquet")

    with duckdb.connect() as connection:
        connection.register("applications", applications)
        connection.register("events", events)
        funnel = _query_sql(connection, "01_funnel.sql")
        segments = _query_sql(connection, "02_segment_friction.sql")
        weekly = _query_sql(connection, "03_weekly_kpis.sql")
        durations = _query_sql(connection, "04_stage_durations.sql")
        review_latency = _query_sql(connection, "05_review_latency.sql")

    funnel["drop_from_previous"] = funnel["applications"].shift(1) - funnel["applications"]
    funnel.loc[0, "drop_from_previous"] = 0
    funnel["drop_from_previous"] = funnel["drop_from_previous"].astype(int)

    scorecard, distribution, sensitivity = _simulate_interventions(funnel, applications, config)
    experiment = config["experiment"]
    primary_base_rate = float(applications[experiment["primary_metric"]].mean())
    sample_per_arm = _experiment_sample_size(
        primary_base_rate,
        experiment["minimum_detectable_lift_pp"],
        experiment["alpha"],
        experiment["power"],
    )
    monthly_apps = int(config["unit_economics"]["monthly_applications"])
    allocation = float(experiment["traffic_allocation"])
    experiment_days_full_traffic = int(
        np.ceil(2 * sample_per_arm / (monthly_apps * allocation / 30))
    )

    recommended_funded_lift = float(scorecard.iloc[0]["expected_funded_lift_pp"])
    funded_sample_per_arm = _experiment_sample_size(
        float(applications["funded_7d"].mean()),
        recommended_funded_lift,
        experiment["alpha"],
        experiment["power"],
    )
    funded_experiment_days = int(
        np.ceil(2 * funded_sample_per_arm / (monthly_apps * allocation / 30))
    )

    top_friction = funnel.iloc[1:].sort_values("drop_from_previous", ascending=False).iloc[0]
    summary = {
        "applications": int(len(applications)),
        "events": int(len(events)),
        "funded_7d_pct": round(100 * float(applications["funded_7d"].mean()), 2),
        "manual_review_pct": round(100 * float(applications["manual_review"].mean()), 2),
        "support_contact_pct": round(100 * float(applications["support_contact"].mean()), 2),
        "largest_absolute_drop_before_stage": str(top_friction["stage"]),
        "largest_absolute_drop_applications": int(top_friction["drop_from_previous"]),
        "recommended_intervention": str(scorecard.iloc[0]["intervention"]),
        "recommended_decision_score": float(scorecard.iloc[0]["decision_score"]),
        "experiment_primary_metric": experiment["primary_metric_label"],
        "experiment_secondary_metric": experiment["secondary_metric_label"],
        "experiment_primary_base_rate_pct": round(100 * primary_base_rate, 2),
        "experiment_sample_per_arm": sample_per_arm,
        "experiment_total_sample": 2 * sample_per_arm,
        "experiment_days_full_traffic": experiment_days_full_traffic,
        "funded_secondary_sample_per_arm": funded_sample_per_arm,
        "funded_secondary_total_sample": 2 * funded_sample_per_arm,
        "funded_secondary_days_full_traffic": funded_experiment_days,
        "minimum_detectable_lift_pp": experiment["minimum_detectable_lift_pp"],
        "minimum_practical_lift_pp": experiment["minimum_practical_lift_pp"],
        "traffic_allocation_pct": round(100 * allocation, 1),
        "monthly_applications": monthly_apps,
        "data_status": "Fully synthetic; no customer or company data",
    }

    prohibited = {"name", "email", "phone", "address", "date_of_birth", "account_number"}
    sorted_events = events.sort_values(["application_id", "event_at"]).reset_index(drop=True)
    data_quality = {
        "applications_rows": int(len(applications)),
        "events_rows": int(len(events)),
        "duplicate_application_ids": int(applications["application_id"].duplicated().sum()),
        "events_with_unknown_application_id": int(
            (~events["application_id"].isin(applications["application_id"])).sum()
        ),
        "events_with_missing_timestamp": int(events["event_at"].isna().sum()),
        "event_stream_ordered": bool(events.reset_index(drop=True).equals(sorted_events)),
        "profile_dependency_violations": int(
            (applications["document_submitted"] & ~applications["profile_completed"]).sum()
        ),
        "verification_dependency_violations": int(
            (applications["verified"] & ~applications["document_submitted"]).sum()
        ),
        "funding_dependency_violations": int(
            (applications["funded"] & ~applications["verified"]).sum()
        ),
        "funded_7d_window_violations": int(
            (
                applications["funded_7d"]
                & (
                    applications["first_funded_at"]
                    > applications["started_at"] + np.timedelta64(7, "D")
                )
            ).sum()
        ),
        "prohibited_pii_columns_present": sorted(
            prohibited & {column.lower() for column in applications.columns}
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    funnel.to_csv(output_dir / "funnel.csv", index=False)
    segments.to_csv(output_dir / "segment_friction.csv", index=False)
    weekly.to_csv(output_dir / "weekly_kpis.csv", index=False)
    durations.to_csv(output_dir / "stage_durations.csv", index=False)
    review_latency.to_csv(output_dir / "review_latency.csv", index=False)
    scorecard.to_csv(output_dir / "intervention_scorecard.csv", index=False)
    sensitivity.to_csv(output_dir / "weight_sensitivity.csv", index=False)
    distribution.to_parquet(output_dir / "intervention_simulations.parquet", index=False)
    (output_dir / "data_quality.json").write_text(
        json.dumps(data_quality, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary
