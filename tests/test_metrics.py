from __future__ import annotations

import pytest

from friction_lab.metrics import _experiment_sample_size


def test_experiment_sample_size_matches_published_primary_design() -> None:
    assert _experiment_sample_size(base_rate=0.571, lift_pp=2.5, alpha=0.05, power=0.80) == 6103


@pytest.mark.parametrize("base_rate", [0, 1, -0.1, 1.1])
def test_experiment_sample_size_rejects_invalid_base_rate(base_rate: float) -> None:
    with pytest.raises(ValueError, match="base rate must be in"):
        _experiment_sample_size(base_rate, lift_pp=2.5, alpha=0.05, power=0.80)


@pytest.mark.parametrize("lift_pp", [0, -1])
def test_experiment_sample_size_rejects_non_positive_lift(lift_pp: float) -> None:
    with pytest.raises(ValueError, match="minimum detectable lift must be positive"):
        _experiment_sample_size(0.571, lift_pp=lift_pp, alpha=0.05, power=0.80)


def test_experiment_sample_size_rejects_lift_above_probability_ceiling() -> None:
    with pytest.raises(ValueError, match="must be below 1"):
        _experiment_sample_size(0.99, lift_pp=2.5, alpha=0.05, power=0.80)


@pytest.mark.parametrize(("alpha", "power", "message"), [(0, 0.8, "alpha"), (0.05, 1, "power")])
def test_experiment_sample_size_rejects_invalid_test_parameters(
    alpha: float, power: float, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        _experiment_sample_size(0.571, lift_pp=2.5, alpha=alpha, power=power)
