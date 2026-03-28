"""Genome computation services — pure functions, no DB or LLM access.

Scoring algorithms for leadership genome analysis:
fit scoring, bias correction, confidence intervals, overall strength.
"""

import math
import statistics


def compute_weighted_fit_score(
    genome: dict[str, float],
    required: dict[str, float],
    calibration: dict[str, float] | None = None,
) -> float:
    """Compute how well a genome fits a required capability profile.

    Per-dimension fit = min(genome[dim] / max(required[dim], 0.01), 1.0).
    Apply optional calibration corrections, then take weighted average.

    Args:
        genome: Dict of dimension -> score (0-10 scale).
        required: Dict of dimension -> required score (0-10 scale).
        calibration: Optional dict of dimension -> correction factor.

    Returns:
        Weighted fit score between 0.0 and 1.0.
    """
    if not required:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0

    for dim, req_score in required.items():
        genome_score = genome.get(dim, 0.0)
        fit = min(genome_score / max(req_score, 0.01), 1.0)

        if calibration and dim in calibration:
            fit = fit * calibration[dim]
            fit = min(fit, 1.0)

        weight = req_score  # higher requirements = higher weight
        weighted_sum += fit * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(min(weighted_sum / total_weight, 1.0), 4)


def apply_bias_corrections(
    raw_scores: dict[str, float],
    ratings: list[float],
    sentiments: list[float],
) -> tuple[dict[str, float], dict[str, str]]:
    """Detect and correct common rating biases.

    Detects:
    - Central tendency: stdev of ratings < 0.5 (compressed range).
    - Halo effect: all dimensions within 0.5 of each other.
    - Rating-feedback divergence: average sentiment diverges from rating trend.

    Args:
        raw_scores: Dict of dimension -> raw score (0-10 scale).
        ratings: List of performance ratings for the leader.
        sentiments: List of sentiment scores (-1.0 to 1.0) from feedback.

    Returns:
        Tuple of (corrected_scores dict, corrections dict explaining what was applied).
    """
    corrected = dict(raw_scores)
    corrections: dict[str, str] = {}

    if not ratings or not raw_scores:
        return corrected, corrections

    # Central tendency detection: compressed rating range
    if len(ratings) >= 3:
        rating_stdev = statistics.stdev(ratings)
        if rating_stdev < 0.5:
            corrections["central_tendency"] = (
                f"Rating stdev={rating_stdev:.2f} < 0.5 — scores may be compressed. "
                "Expanding spread from mean."
            )
            mean_score = statistics.mean(corrected.values()) if corrected else 5.0
            for dim in corrected:
                deviation = corrected[dim] - mean_score
                corrected[dim] = mean_score + deviation * 1.3
                corrected[dim] = max(0.0, min(10.0, corrected[dim]))

    # Halo effect: all dimension scores suspiciously similar
    if len(raw_scores) >= 3:
        score_values = list(raw_scores.values())
        score_range = max(score_values) - min(score_values)
        if score_range < 0.5:
            corrections["halo_effect"] = (
                f"Dimension range={score_range:.2f} < 0.5 — possible halo effect. "
                "Scores may not reflect real differentiation."
            )

    # Rating-feedback divergence
    if sentiments:
        avg_sentiment = statistics.mean(sentiments)
        avg_rating = statistics.mean(ratings)
        normalized_rating = (avg_rating - 5.0) / 5.0  # map 0-10 to -1..1

        divergence = abs(avg_sentiment - normalized_rating)
        if divergence > 0.4:
            direction = "positive" if avg_sentiment > normalized_rating else "negative"
            corrections["rating_feedback_divergence"] = (
                f"Sentiment ({avg_sentiment:.2f}) diverges from ratings "
                f"({normalized_rating:.2f}) by {divergence:.2f}. "
                f"Feedback is more {direction} than scores suggest."
            )
            adjustment = avg_sentiment * 0.3
            for dim in corrected:
                corrected[dim] = max(0.0, min(10.0, corrected[dim] + adjustment))

    return corrected, corrections


def compute_confidence_interval(
    score: float,
    source_count: int,
    agreement: float = 1.0,
) -> tuple[float, float]:
    """Compute confidence interval for a score.

    Width = 0.20 / sqrt(sources) / agreement. More sources and higher
    agreement narrow the interval.

    Args:
        score: The point estimate (0-1 scale).
        source_count: Number of data sources.
        agreement: Inter-source agreement (0-1 scale, 1.0 = perfect agreement).

    Returns:
        Tuple of (lower_bound, upper_bound), clamped to [0, 1].
    """
    source_count = max(source_count, 1)
    agreement = max(agreement, 0.1)

    half_width = 0.20 / math.sqrt(source_count) / agreement
    low = max(0.0, score - half_width)
    high = min(1.0, score + half_width)
    return (round(low, 4), round(high, 4))


def compute_overall_strength(
    genome: dict[str, float],
    weights: dict[str, float] | None = None,
) -> float:
    """Compute overall leadership strength as weighted mean.

    Args:
        genome: Dict of dimension -> score (0-10 scale).
        weights: Optional dict of dimension -> weight. Default = uniform.

    Returns:
        Weighted mean score normalized to 0.0-1.0.
    """
    if not genome:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0

    for dim, score in genome.items():
        w = weights.get(dim, 1.0) if weights else 1.0
        weighted_sum += score * w
        total_weight += w

    if total_weight == 0:
        return 0.0

    # Normalize from 0-10 scale to 0-1
    return round(min(weighted_sum / total_weight / 10.0, 1.0), 4)
