from __future__ import annotations

import math
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

REQUIRED_DECISION_WEIGHTS = {
    "conversion_impact",
    "guardrails",
    "speed_to_learn",
    "evidence_confidence",
}


def _required_mapping(parent: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{path}: {key} must be a non-empty mapping")
    return value


def _required_text(parent: dict[str, Any], key: str, path: Path, context: str) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}: {context}.{key} must be non-empty text")
    return value.strip()


def _number(value: Any, path: Path, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{path}: {label} must be a finite number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{path}: {label} must be a finite number") from error
    if not math.isfinite(parsed):
        raise ValueError(f"{path}: {label} must be a finite number")
    return parsed


def _integer(value: Any, path: Path, label: str, minimum: int = 0) -> int:
    parsed = _number(value, path, label)
    if not parsed.is_integer() or parsed < minimum:
        raise ValueError(f"{path}: {label} must be an integer >= {minimum}")
    return int(parsed)


def _validate_config(config: dict[str, Any], path: Path) -> None:
    """Fail early when an assumption file would produce a misleading model."""
    project = _required_mapping(config, "project", path)
    _required_text(project, "name", path, "project")
    _required_text(project, "geography", path, "project")
    _integer(project.get("generated_applications"), path, "project.generated_applications", 1)
    _integer(project.get("seed"), path, "project.seed")

    economics = _required_mapping(config, "unit_economics", path)
    required_economics = {
        "funded_account_12m_contribution_eur",
        "support_contact_cost_eur",
        "manual_review_cost_eur",
        "monthly_applications",
    }
    missing_economics = required_economics - set(economics)
    if missing_economics:
        raise ValueError(
            f"{path}: missing unit_economics fields: {', '.join(sorted(missing_economics))}"
        )
    if (
        _number(
            economics["funded_account_12m_contribution_eur"],
            path,
            "unit_economics.funded_account_12m_contribution_eur",
        )
        <= 0
    ):
        raise ValueError(f"{path}: funded-account contribution must be positive")
    for key in ("support_contact_cost_eur", "manual_review_cost_eur"):
        if _number(economics[key], path, f"unit_economics.{key}") < 0:
            raise ValueError(f"{path}: unit_economics.{key} cannot be negative")
    _integer(economics["monthly_applications"], path, "unit_economics.monthly_applications", 1)

    weights = _required_mapping(config, "decision_weights", path)
    missing_weights = REQUIRED_DECISION_WEIGHTS - set(weights)
    unexpected_weights = set(weights) - REQUIRED_DECISION_WEIGHTS
    if missing_weights:
        raise ValueError(f"{path}: missing decision_weights: {', '.join(sorted(missing_weights))}")
    if unexpected_weights:
        raise ValueError(
            f"{path}: unsupported decision_weights: {', '.join(sorted(unexpected_weights))}"
        )
    numeric_weights = {
        key: _number(value, path, f"decision_weights.{key}") for key, value in weights.items()
    }
    if abs(sum(numeric_weights.values()) - 1.0) > 1e-9:
        raise ValueError(f"{path}: decision_weights must sum to 1.0")
    if any(value < 0 for value in numeric_weights.values()):
        raise ValueError(f"{path}: decision_weights cannot be negative")

    anchors = _required_mapping(config, "decision_score_anchors", path)
    positive_anchors = {
        "conversion_impact_pp_cap",
        "guardrail_penalty_pp_cap",
        "fastest_delivery_weeks",
        "slowest_delivery_weeks",
    }
    missing_anchors = positive_anchors - set(anchors)
    if missing_anchors:
        raise ValueError(f"{path}: missing score anchors: {', '.join(sorted(missing_anchors))}")
    numeric_anchors = {
        key: _number(anchors[key], path, f"decision_score_anchors.{key}")
        for key in positive_anchors
    }
    if any(value <= 0 for value in numeric_anchors.values()):
        raise ValueError(f"{path}: decision score anchors must be positive")
    if numeric_anchors["fastest_delivery_weeks"] >= numeric_anchors["slowest_delivery_weeks"]:
        raise ValueError(f"{path}: fastest delivery anchor must be below slowest")

    interventions = config["interventions"]
    if not isinstance(interventions, list) or not interventions:
        raise ValueError(f"{path}: interventions must be a non-empty list")
    if not all(isinstance(intervention, dict) for intervention in interventions):
        raise ValueError(f"{path}: every intervention must be a mapping")
    keys = [intervention.get("key") for intervention in interventions]
    if any(not isinstance(key, str) or not key.strip() for key in keys):
        raise ValueError(f"{path}: interventions need unique non-empty keys")
    normalised_keys = [key.strip() for key in keys]
    if len(normalised_keys) != len(set(normalised_keys)):
        raise ValueError(f"{path}: interventions need unique non-empty keys")
    for intervention in interventions:
        label = _required_text(intervention, "key", path, "intervention")
        _required_text(intervention, "name", path, label)
        _required_text(intervention, "hypothesis", path, label)
        if intervention.get("target_stage") not in ALLOWED_TARGET_STAGES:
            raise ValueError(f"{path}: {label} has an unsupported target_stage")
        if intervention.get("cost_population") not in ALLOWED_COST_POPULATIONS:
            raise ValueError(f"{path}: {label} has an unsupported cost_population")
        lift = _required_mapping(intervention, "stage_lift_pp", path)
        missing_lift_values = {"low", "most_likely", "high"} - set(lift)
        if missing_lift_values:
            raise ValueError(f"{path}: {label} needs low/most_likely/high lift values")
        low, likely, high = (
            _number(lift[key], path, f"{label}.stage_lift_pp.{key}")
            for key in ("low", "most_likely", "high")
        )
        if not 0 <= low <= likely <= high:
            raise ValueError(f"{path}: {label} lift values must satisfy 0 <= low <= likely <= high")
        confidence = _number(
            intervention.get("evidence_confidence"), path, f"{label}.evidence_confidence"
        )
        if not 0 <= confidence <= 1:
            raise ValueError(f"{path}: {label} evidence_confidence must be in [0, 1]")
        if _number(intervention.get("fixed_cost_eur"), path, f"{label}.fixed_cost_eur") < 0:
            raise ValueError(f"{path}: {label} fixed_cost_eur cannot be negative")
        if (
            _number(
                intervention.get("variable_cost_eur_per_application"),
                path,
                f"{label}.variable_cost_eur_per_application",
            )
            < 0
        ):
            raise ValueError(f"{path}: {label} variable cost cannot be negative")
        if _number(intervention.get("delivery_weeks"), path, f"{label}.delivery_weeks") <= 0:
            raise ValueError(f"{path}: {label} delivery_weeks must be positive")
        _number(intervention.get("support_delta_pp"), path, f"{label}.support_delta_pp")
        _number(intervention.get("manual_review_delta_pp"), path, f"{label}.manual_review_delta_pp")

    experiment = _required_mapping(config, "experiment", path)
    _required_text(experiment, "primary_metric_label", path, "experiment")
    _required_text(experiment, "secondary_metric_label", path, "experiment")
    if experiment.get("primary_metric") not in ALLOWED_TARGET_STAGES:
        raise ValueError(f"{path}: unsupported experiment primary_metric")
    if not 0 < _number(experiment.get("alpha"), path, "experiment.alpha") < 1:
        raise ValueError(f"{path}: experiment alpha must be in (0, 1)")
    if not 0 < _number(experiment.get("power"), path, "experiment.power") < 1:
        raise ValueError(f"{path}: experiment power must be in (0, 1)")
    if (
        not 0
        < _number(experiment.get("traffic_allocation"), path, "experiment.traffic_allocation")
        <= 1
    ):
        raise ValueError(f"{path}: traffic_allocation must be in (0, 1]")
    if (
        _number(
            experiment.get("minimum_detectable_lift_pp"),
            path,
            "experiment.minimum_detectable_lift_pp",
        )
        <= 0
    ):
        raise ValueError(f"{path}: minimum_detectable_lift_pp must be positive")
    if (
        _number(
            experiment.get("minimum_practical_lift_pp"),
            path,
            "experiment.minimum_practical_lift_pp",
        )
        <= 0
    ):
        raise ValueError(f"{path}: minimum_practical_lift_pp must be positive")


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict):
        raise ValueError(f"{path}: configuration root must be a mapping")
    missing = sorted(REQUIRED_CONFIG_KEYS - set(config))
    if missing:
        raise ValueError(f"{path} is missing required keys: {', '.join(missing)}")
    _validate_config(config, path)
    return config
