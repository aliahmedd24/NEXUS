"""Tests for bias correction services."""

from src.services.bias_correction import (
    compute_calibration_coefficients,
    detect_historical_biases,
)


def test_detect_overweighted_dimension():
    """Dimension with high weight but poor outcome quality is flagged."""
    decisions = [
        {
            "id": "d1",
            "decision_criteria_used": {"industry_tenure": 0.4, "innovation": 0.1},
        },
        {
            "id": "d2",
            "decision_criteria_used": {"industry_tenure": 0.35, "innovation": 0.15},
        },
    ]
    outcomes = [
        {"decision_id": "d1", "performance_rating": 6.0, "goal_completion_pct": 60},
        {"decision_id": "d2", "performance_rating": 6.5, "goal_completion_pct": 65},
    ]
    biases = detect_historical_biases(decisions, outcomes)
    # industry_tenure had high weight — should show up in biases
    assert "industry_tenure" in biases


def test_calibration_reduces_overweighted():
    """Overweighted dimension gets correction < 1.0."""
    biases = {"industry_tenure": 0.35, "innovation": -0.1}
    coefficients = compute_calibration_coefficients(biases)
    assert coefficients["industry_tenure"] < 1.0
    assert coefficients["innovation"] > 1.0
