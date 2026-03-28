"""Tests for genome computation services."""

from src.services.genome_computation import (
    apply_bias_corrections,
    compute_confidence_interval,
    compute_overall_strength,
    compute_weighted_fit_score,
)


def test_perfect_fit_returns_1():
    """Candidate exceeding all requirements scores 1.0."""
    genome = {"strategic_thinking": 0.9, "operational_execution": 0.8}
    required = {"strategic_thinking": 0.7, "operational_execution": 0.6}
    assert compute_weighted_fit_score(genome, required) == 1.0


def test_zero_genome_returns_0():
    """Zero scores against nonzero requirements."""
    genome = {"strategic_thinking": 0.0, "operational_execution": 0.0}
    required = {"strategic_thinking": 0.7, "operational_execution": 0.6}
    assert compute_weighted_fit_score(genome, required) == 0.0


def test_partial_fit():
    """Candidate meeting exactly half the requirements."""
    genome = {"dim_a": 0.5}
    required = {"dim_a": 1.0}
    score = compute_weighted_fit_score(genome, required)
    assert 0.49 <= score <= 0.51


def test_calibration_reduces_score():
    """Calibration factor < 1.0 reduces fit score."""
    genome = {"dim_a": 1.0}
    required = {"dim_a": 1.0}
    calibration = {"dim_a": 0.8}
    score = compute_weighted_fit_score(genome, required, calibration)
    assert score < 1.0


def test_bias_detection_finds_central_tendency():
    """Compressed rating range triggers central tendency detection."""
    ratings = [7.2, 7.5, 7.8, 7.3, 7.6, 7.4, 7.7, 7.1]
    sentiments = [-0.3, 0.1, -0.5, 0.2, -0.1, 0.4, -0.6, 0.0]
    corrected, corrections = apply_bias_corrections(
        {"dim_a": 7.5}, ratings, sentiments
    )
    assert "central_tendency" in corrections


def test_bias_detection_finds_halo_effect():
    """All dimensions within 0.5 triggers halo effect detection."""
    raw_scores = {"dim_a": 7.5, "dim_b": 7.6, "dim_c": 7.4}
    ratings = [7.0, 7.5, 8.0]
    sentiments = [0.1, 0.2, 0.3]
    _, corrections = apply_bias_corrections(raw_scores, ratings, sentiments)
    assert "halo_effect" in corrections


def test_confidence_interval_narrows_with_more_sources():
    """More sources produce a narrower interval."""
    low1, high1 = compute_confidence_interval(0.5, 1)
    low4, high4 = compute_confidence_interval(0.5, 4)
    assert (high1 - low1) > (high4 - low4)


def test_overall_strength_uniform():
    """Uniform weights with 7.0 scores => 0.7 strength."""
    genome = {"dim_a": 7.0, "dim_b": 7.0, "dim_c": 7.0}
    strength = compute_overall_strength(genome)
    assert strength == 0.7
