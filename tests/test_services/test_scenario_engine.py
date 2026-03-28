"""Tests for scenario engine services."""

from src.services.scenario_engine import adapt_jd_weightings, combine_scenarios


def test_adapt_weightings_sum_to_one():
    """Adapted weightings must sum to 1.0."""
    base = {"strategic_thinking": 0.3, "operational_execution": 0.4, "innovation": 0.3}
    demand = {"strategic_thinking": 0.9, "operational_execution": 0.3, "innovation": 0.5}
    adapted, _ = adapt_jd_weightings(base, demand)
    assert abs(sum(adapted.values()) - 1.0) < 0.01


def test_high_demand_increases_weight():
    """Dimension with high demand gets relatively higher weight."""
    base = {"dim_a": 0.5, "dim_b": 0.5}
    demand = {"dim_a": 1.0, "dim_b": 0.0}
    adapted, _ = adapt_jd_weightings(base, demand)
    assert adapted["dim_a"] > adapted["dim_b"]


def test_combine_scenarios_takes_max():
    """Combined demand uses element-wise max."""
    a = {"dim_a": 0.3, "dim_b": 0.9}
    b = {"dim_a": 0.8, "dim_b": 0.4}
    combined = combine_scenarios(a, b)
    assert combined["dim_a"] == 0.8
    assert combined["dim_b"] == 0.9


def test_combine_scenarios_interaction_boost():
    """Co-critical dimensions (both >0.7) get a boost."""
    a = {"dim_a": 0.8, "dim_b": 0.2}
    b = {"dim_a": 0.9, "dim_b": 0.1}
    combined = combine_scenarios(a, b)
    # max is 0.9, boost = 0.1 * min(0.8, 0.9) = 0.08 -> 0.98
    assert combined["dim_a"] > 0.9
