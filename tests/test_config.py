from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from friction_lab.config import load_config


def _write_config(path: Path, config: dict) -> None:
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")


def _assert_invalid_config(
    tmp_path: Path, config: dict, message: str, filename: str = "invalid.yml"
) -> None:
    path = tmp_path / filename
    _write_config(path, config)
    with pytest.raises(ValueError, match=message):
        load_config(path)


def test_config_rejects_weights_that_do_not_sum_to_one(tmp_path: Path) -> None:
    config = deepcopy(load_config())
    config["decision_weights"]["conversion_impact"] = 0.60
    _assert_invalid_config(tmp_path, config, "must sum to 1.0")


def test_config_rejects_reversed_lift_range(tmp_path: Path) -> None:
    config = deepcopy(load_config())
    config["interventions"][0]["stage_lift_pp"] = {
        "low": 6.0,
        "most_likely": 4.0,
        "high": 2.0,
    }
    _assert_invalid_config(tmp_path, config, "lift values")


@pytest.mark.parametrize("invalid_key", [None, "", "   "])
def test_config_rejects_empty_intervention_key(tmp_path: Path, invalid_key: object) -> None:
    config = deepcopy(load_config())
    config["interventions"] = [deepcopy(config["interventions"][0])]
    config["interventions"][0]["key"] = invalid_key

    _assert_invalid_config(tmp_path, config, "unique non-empty keys")


def test_config_rejects_incomplete_decision_weights(tmp_path: Path) -> None:
    config = deepcopy(load_config())
    config["decision_weights"].pop("guardrails")

    _assert_invalid_config(tmp_path, config, "missing decision_weights: guardrails")


def test_config_rejects_negative_unit_economics(tmp_path: Path) -> None:
    config = deepcopy(load_config())
    config["unit_economics"]["manual_review_cost_eur"] = -0.01

    _assert_invalid_config(tmp_path, config, "manual_review_cost_eur cannot be negative")


@pytest.mark.parametrize("invalid_mde", [0, -1, None, "unknown"])
def test_config_rejects_invalid_minimum_detectable_effect(
    tmp_path: Path, invalid_mde: object
) -> None:
    config = deepcopy(load_config())
    config["experiment"]["minimum_detectable_lift_pp"] = invalid_mde

    _assert_invalid_config(tmp_path, config, "minimum_detectable_lift_pp")


def test_config_rejects_non_positive_delivery_window(tmp_path: Path) -> None:
    config = deepcopy(load_config())
    config["interventions"][0]["delivery_weeks"] = 0

    _assert_invalid_config(tmp_path, config, "delivery_weeks must be positive")


@pytest.mark.parametrize(
    ("section", "field", "message"),
    [
        ("project", "seed", "project.seed"),
        ("unit_economics", "monthly_applications", "missing unit_economics fields"),
        ("experiment", "primary_metric_label", "primary_metric_label"),
    ],
)
def test_config_rejects_missing_nested_fields(
    tmp_path: Path, section: str, field: str, message: str
) -> None:
    config = deepcopy(load_config())
    config[section].pop(field)

    _assert_invalid_config(tmp_path, config, message)
