"""Tests for compatibility engine services."""

from src.services.compatibility_engine import (
    compute_pairwise_compatibility,
    compute_team_balance,
)


def test_complementary_pair_positive_synergy():
    """Complementary genomes produce positive synergy."""
    strategist = {"strategic_thinking": 9.0, "operational_execution": 3.0}
    executor = {"strategic_thinking": 3.0, "operational_execution": 9.0}
    rules = [
        {
            "dimension_a": "strategic_thinking",
            "dimension_b": "operational_execution",
            "relationship_type": "cross_functional",
            "interaction_effect": "complementary_positive",
            "effect_magnitude": 0.8,
        }
    ]
    result = compute_pairwise_compatibility(
        strategist, executor, "cross_functional", rules
    )
    assert result["mechanical_synergy_score"] > 0


def test_clash_pair_negative_synergy():
    """Clashing dimensions produce negative synergy."""
    leader_a = {"risk_calibration": 9.0}
    leader_b = {"risk_calibration": 9.0}
    rules = [
        {
            "dimension_a": "risk_calibration",
            "dimension_b": "risk_calibration",
            "relationship_type": "peer",
            "interaction_effect": "clash_negative",
            "effect_magnitude": 0.8,
        }
    ]
    result = compute_pairwise_compatibility(leader_a, leader_b, "peer", rules)
    assert result["mechanical_synergy_score"] < 0


def test_team_balance_fills_gap():
    """Adding a candidate with a strong dim fills a team gap."""
    team = [
        {"dim_a": 3.0, "dim_b": 8.0},
        {"dim_a": 4.0, "dim_b": 7.0},
    ]
    candidate = {"dim_a": 9.0, "dim_b": 5.0}
    result = compute_team_balance(team, candidate)
    assert "dim_a" in result["gaps_filled"]
