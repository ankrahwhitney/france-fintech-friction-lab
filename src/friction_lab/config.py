from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "model_assumptions.yml"
DATA_DIR = ROOT / "data" / "processed"
ARTIFACT_DIR = ROOT / "artifacts"

REQUIRED_CONFIG_KEYS = {
    "project",
    "interventions",
    "decision_weights",
    "decision_score_anchors",
    "unit_economics",
    "experiment",
}

ALLOWED_TARGET_STAGES = {
    "profile_completed",
    "document_submitted",
    "verification_completed",
    "account_funded",
}
ALLOWED_COST_POPULATIONS = {
    "application_started",
    "profile_completed",
    "failed_verification",
}


def _validate_config(config: dict[str, Any], path: Path) -> None:
    """Fail early when an assumption file would produce a misleading model."""
    weights = config["decision_weights"]
    if not weights or abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
        raise ValueError(f"{path}: decision_weights must sum to 1.0")
    if any(float(value) < 0 for value in weights.values()):
        raise ValueError(f"{path}: decision_weights cannot be negative")

    anchors = config["decision_score_anchors"]
    positive_anchors = {
        "conversion_impact_pp_cap",
        "guardrail_penalty_pp_cap",
        "fastest_delivery_weeks",
        "slowest_delivery_weeks",
    }
    missing_anchors = positive_anchors - set(anchors)
    if missing_anchors:
        raise ValueError(f"{path}: missing score anchors: {', '.join(sorted(missing_anchors))}")
    if any(float(anchors[key]) <= 0 for key in positive_anchors):
        raise ValueError(f"{path}: decision score anchors must be positive")
    if anchors["fastest_delivery_weeks"] >= anchors["slowest_delivery_weeks"]:
        raise ValueError(f"{path}: fastest delivery anchor must be below slowest")

    interventions = config["interventions"]
    keys = [intervention.get("key") for intervention in interventions]
    if not interventions or len(keys) != len(set(keys)):
        raise ValueError(f"{path}: interventions need unique non-empty keys")
    for intervention in interventions:
        label = intervention.get("key", "<missing key>")
        if intervention.get("target_stage") not in ALLOWED_TARGET_STAGES:
            raise ValueError(f"{path}: {label} has an unsupported target_stage")
        if intervention.get("cost_population") not in ALLOWED_COST_POPULATIONS:
            raise ValueError(f"{path}: {label} has an unsupported cost_population")
        lift = intervention.get("stage_lift_pp", {})
        try:
            low, likely, high = (float(lift[key]) for key in ("low", "most_likely", "high"))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"{path}: {label} needs low/most_likely/high lift values") from error
        if not 0 <= low <= likely <= high:
            raise ValueError(f"{path}: {label} lift values must satisfy 0 <= low <= likely <= high")
        confidence = float(intervention.get("evidence_confidence", -1))
        if not 0 <= confidence <= 1:
            raise ValueError(f"{path}: {label} evidence_confidence must be in [0, 1]")
        if float(intervention.get("fixed_cost_eur", -1)) < 0:
            raise ValueError(f"{path}: {label} fixed_cost_eur cannot be negative")
        if float(intervention.get("variable_cost_eur_per_application", -1)) < 0:
            raise ValueError(f"{path}: {label} variable cost cannot be negative")

    experiment = config["experiment"]
    if experiment.get("primary_metric") not in ALLOWED_TARGET_STAGES:
        raise ValueError(f"{path}: unsupported experiment primary_metric")
    if not 0 < float(experiment.get("alpha", 0)) < 1:
        raise ValueError(f"{path}: experiment alpha must be in (0, 1)")
    if not 0 < float(experiment.get("power", 0)) < 1:
        raise ValueError(f"{path}: experiment power must be in (0, 1)")
    if not 0 < float(experiment.get("traffic_allocation", 0)) <= 1:
        raise ValueError(f"{path}: traffic_allocation must be in (0, 1]")
    if float(experiment.get("minimum_practical_lift_pp", -1)) < 0:
        raise ValueError(f"{path}: minimum_practical_lift_pp cannot be negative")


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    missing = sorted(REQUIRED_CONFIG_KEYS - set(config))
    if missing:
        raise ValueError(f"{path} is missing required keys: {', '.join(missing)}")
    _validate_config(config, path)
    return config
