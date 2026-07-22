from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from friction_lab.config import load_config


def _write_config(path: Path, config: dict) -> None:
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")


def test_config_rejects_weights_that_do_not_sum_to_one(tmp_path: Path) -> None:
    config = deepcopy(load_config())
    config["decision_weights"]["conversion_impact"] = 0.60
    path = tmp_path / "invalid.yml"
    _write_config(path, config)

    with pytest.raises(ValueError, match="must sum to 1.0"):
        load_config(path)


def test_config_rejects_reversed_lift_range(tmp_path: Path) -> None:
    config = deepcopy(load_config())
    config["interventions"][0]["stage_lift_pp"] = {
        "low": 6.0,
        "most_likely": 4.0,
        "high": 2.0,
    }
    path = tmp_path / "invalid.yml"
    _write_config(path, config)

    with pytest.raises(ValueError, match="lift values"):
        load_config(path)
