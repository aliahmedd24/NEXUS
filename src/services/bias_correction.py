"""Bias detection and calibration — pure functions, no DB or LLM access.

Analyzes historical hiring decisions to detect systematic biases and
compute calibration coefficients for future decision-making.
"""

import statistics


def detect_historical_biases(
    decisions: list[dict],
    outcomes: list[dict],
) -> dict[str, float]:
    """Detect systematic biases in historical hiring decisions.

    Correlates criteria weights with outcome quality. A dimension is
    overweighted if it had high weight in decisions but low correlation
    with positive outcomes.

    Args:
        decisions: List of decision dicts with decision_criteria_used
            (dict of dimension -> weight) and id.
        outcomes: List of outcome dicts with decision_id,
            performance_rating, goal_completion_pct.

    Returns:
        Dict of dimension -> overweight factor. Positive = overweighted,
        negative = underweighted. Zero = well-calibrated.
    """
    if not decisions or not outcomes:
        return {}

    # Build outcome quality index: decision_id -> avg quality
    outcome_quality: dict[str, float] = {}
    for decision_id in {d["id"] for d in decisions}:
        dec_outcomes = [o for o in outcomes if o["decision_id"] == decision_id]
        if dec_outcomes:
            # Normalize rating (0-10) and completion (0-100) to 0-1
            quality_scores = [
                (o.get("performance_rating", 5.0) / 10.0 * 0.5
                 + o.get("goal_completion_pct", 50) / 100.0 * 0.5)
                for o in dec_outcomes
            ]
            outcome_quality[decision_id] = statistics.mean(quality_scores)

    # For each dimension, correlate weight with outcome quality
    dim_weights: dict[str, list[float]] = {}
    dim_qualities: dict[str, list[float]] = {}

    for decision in decisions:
        dec_id = decision["id"]
        quality = outcome_quality.get(dec_id)
        if quality is None:
            continue

        criteria = decision.get("decision_criteria_used", {})
        for dim, weight in criteria.items():
            dim_weights.setdefault(dim, []).append(weight)
            dim_qualities.setdefault(dim, []).append(quality)

    # Compute overweight factor per dimension
    biases: dict[str, float] = {}
    for dim in dim_weights:
        weights = dim_weights[dim]
        qualities = dim_qualities[dim]

        if len(weights) < 2:
            continue

        avg_weight = statistics.mean(weights)

        # Weighted quality: how did high-weight uses of this dim perform?
        weighted_quality = sum(w * q for w, q in zip(weights, qualities)) / max(sum(weights), 0.01)
        overall_quality = statistics.mean(qualities)

        # Overweight = high avg weight but weighted quality below average
        if weighted_quality < overall_quality:
            overweight = avg_weight * (overall_quality - weighted_quality) / max(overall_quality, 0.01)
        else:
            overweight = -avg_weight * (weighted_quality - overall_quality) / max(overall_quality, 0.01)

        biases[dim] = round(overweight, 4)

    return biases


def compute_calibration_coefficients(
    biases: dict[str, float],
) -> dict[str, float]:
    """Convert detected biases into calibration correction factors.

    correction = 1.0 / (1.0 + overweight) for overweighted dimensions.
    Underweighted dimensions get a boost: 1.0 / (1.0 - abs(underweight)).

    Args:
        biases: Dict of dimension -> overweight factor from detect_historical_biases.

    Returns:
        Dict of dimension -> correction factor. Values < 1.0 reduce weight,
        values > 1.0 increase weight.
    """
    coefficients: dict[str, float] = {}

    for dim, overweight in biases.items():
        if overweight > 0:
            # Overweighted: reduce
            coefficients[dim] = round(1.0 / (1.0 + overweight), 4)
        elif overweight < 0:
            # Underweighted: boost
            coefficients[dim] = round(1.0 / (1.0 - abs(overweight)), 4)
        else:
            coefficients[dim] = 1.0

    return coefficients
