"""Tests for portfolio math services."""

from src.services.portfolio_math import (
    compute_efficient_frontier,
    compute_roi_estimate,
    compute_scenario_sensitivity,
)


def test_frontier_monotonically_increasing():
    """Higher budget => equal or higher resilience improvement."""
    roles = [
        {"id": "r1", "title": "Role A"},
        {"id": "r2", "title": "Role B"},
    ]
    candidates = {
        "r1": [{"name": "C1", "fit_score": 0.8, "cost_eur": 50_000}],
        "r2": [{"name": "C2", "fit_score": 0.6, "cost_eur": 40_000}],
    }
    frontier = compute_efficient_frontier(
        roles, candidates, [30_000, 50_000, 100_000]
    )
    resiliences = [p["resilience_improvement"] for p in frontier]
    assert all(a <= b for a, b in zip(resiliences, resiliences[1:]))


def test_scenario_sensitivity():
    """Candidate with varying ranks has higher sensitivity."""
    rankings = {
        "scenario_1": {"cand_a": 1, "cand_b": 3},
        "scenario_2": {"cand_a": 3, "cand_b": 2},
        "scenario_3": {"cand_a": 2, "cand_b": 1},
    }
    sensitivity = compute_scenario_sensitivity(rankings)
    assert sensitivity["cand_a"] == sensitivity["cand_b"]  # both vary by 1
    assert sensitivity["cand_a"] > 0


def test_roi_positive_when_risk_exceeds_cost():
    """ROI is positive when avoided risk exceeds hiring cost."""
    plan = {"total_cost_eur": 100_000, "items": []}
    impacts = [
        {"estimated_cost_eur": 200_000},
        {"estimated_cost_eur": 150_000},
    ]
    result = compute_roi_estimate(plan, impacts)
    assert result["roi"] > 0
    assert result["total_risk_avoided"] == 350_000
