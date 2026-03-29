"""Team compatibility computation — pure functions, no DB or LLM access.

Pairwise compatibility scoring and team balance analysis based on
leadership genome profiles and interaction rules.
"""

import statistics


def compute_pairwise_compatibility(
    genome_a: dict[str, float],
    genome_b: dict[str, float],
    relationship_type: str,
    rules: list[dict],
) -> dict:
    """Compute compatibility between two leaders based on interaction rules.

    Applies rules: complementary -> positive synergy, clash -> negative,
    high overlap -> groupthink risk. Normalizes to [-1, 1].

    Args:
        genome_a: Dict of dimension -> score (0-10) for leader A.
        genome_b: Dict of dimension -> score (0-10) for leader B.
        relationship_type: E.g. "cross_functional", "direct_report", "peer".
        rules: List of interaction rule dicts with keys:
            dimension_a, dimension_b, relationship_type,
            interaction_effect, effect_magnitude.

    Returns:
        Dict with synergy_score (-1 to 1), friction_dimensions,
        synergy_dimensions, groupthink_risk.
    """
    synergy_total = 0.0
    rule_count = 0
    friction_dims: list[str] = []
    synergy_dims: list[str] = []
    overlap_dims: list[str] = []

    # Apply interaction rules — magnitude is neutral (0.5) for all rules.
    # The LLM reasons about actual interaction strength from context.
    for rule in rules:
        if rule.get("relationship_type") and rule["relationship_type"] != relationship_type:
            continue

        dim_a = rule["dimension_a"]
        dim_b = rule["dimension_b"]
        effect = rule["interaction_effect"]
        magnitude = 0.5  # neutral — no hardcoded bias

        score_a = genome_a.get(dim_a, 5.0)
        score_b = genome_b.get(dim_b, 5.0)

        # Normalize scores to 0-1 for computation
        norm_a = score_a / 10.0
        norm_b = score_b / 10.0

        if effect == "complementary_positive":
            # Both strong in different areas = good synergy
            contribution = min(norm_a, norm_b) * magnitude
            synergy_total += contribution
            if contribution > 0.1:
                synergy_dims.append(f"{dim_a}+{dim_b}")
        elif effect == "clash_negative":
            # Both high = friction
            both_high = min(norm_a, norm_b)
            contribution = -both_high * magnitude
            synergy_total += contribution
            if abs(contribution) > 0.1:
                friction_dims.append(f"{dim_a}x{dim_b}")
        elif effect == "amplifying":
            # Both high = amplified positive
            contribution = norm_a * norm_b * magnitude
            synergy_total += contribution
            if contribution > 0.1:
                synergy_dims.append(f"{dim_a}*{dim_b}")

        rule_count += 1

    # Groupthink detection: high overlap in many dimensions
    shared_dims = set(genome_a.keys()) & set(genome_b.keys())
    for dim in shared_dims:
        if abs(genome_a[dim] - genome_b[dim]) < 1.0 and genome_a[dim] > 7.0:
            overlap_dims.append(dim)

    groupthink_risk = min(len(overlap_dims) / max(len(shared_dims), 1), 1.0)

    # Normalize synergy score to [-1, 1]
    if rule_count > 0:
        synergy_score = max(-1.0, min(1.0, synergy_total / rule_count))
    else:
        synergy_score = 0.0

    return {
        "mechanical_synergy_score": round(synergy_score, 4),
        "friction_dimensions": friction_dims,
        "synergy_dimensions": synergy_dims,
        "groupthink_risk": round(groupthink_risk, 4),
    }


def compute_team_balance(
    team_genomes: list[dict[str, float]],
    candidate_genome: dict[str, float],
) -> dict:
    """Compute team balance metrics with and without a candidate.

    Args:
        team_genomes: List of genome dicts for existing team members.
        candidate_genome: Genome dict for the candidate being evaluated.

    Returns:
        TeamBalanceCard-compatible dict with cognitive_diversity,
        gap_dimensions, overlap_dimensions, diversity_delta,
        gaps_filled, new_overlaps.
    """
    if not team_genomes:
        return {
            "cognitive_diversity": 0.0,
            "gap_dimensions": [],
            "overlap_dimensions": [],
            "diversity_delta": 0.0,
            "gaps_filled": [],
            "new_overlaps": [],
        }

    # Get all dimensions from team
    all_dims = set()
    for g in team_genomes:
        all_dims.update(g.keys())
    all_dims.update(candidate_genome.keys())

    # Compute current team stats per dimension
    current_gaps: list[str] = []
    current_overlaps: list[str] = []
    current_stdevs: list[float] = []

    for dim in sorted(all_dims):
        scores = [g.get(dim, 0.0) / 10.0 for g in team_genomes]
        if scores:
            dim_max = max(scores)
            dim_min = min(scores)
            if dim_max < 0.6:
                current_gaps.append(dim)
            if len(scores) > 1 and dim_min > 0.7:
                current_overlaps.append(dim)
            if len(scores) > 1:
                current_stdevs.append(statistics.stdev(scores))

    current_diversity = statistics.mean(current_stdevs) if current_stdevs else 0.0

    # Compute stats with candidate added
    augmented = team_genomes + [candidate_genome]
    new_gaps: list[str] = []
    new_overlaps: list[str] = []
    new_stdevs: list[float] = []

    for dim in sorted(all_dims):
        scores = [g.get(dim, 0.0) / 10.0 for g in augmented]
        dim_max = max(scores)
        dim_min = min(scores)
        if dim_max < 0.6:
            new_gaps.append(dim)
        if dim_min > 0.7:
            new_overlaps.append(dim)
        if len(scores) > 1:
            new_stdevs.append(statistics.stdev(scores))

    new_diversity = statistics.mean(new_stdevs) if new_stdevs else 0.0

    gaps_filled = [d for d in current_gaps if d not in new_gaps]
    added_overlaps = [d for d in new_overlaps if d not in current_overlaps]

    return {
        "cognitive_diversity": round(new_diversity, 4),
        "gap_dimensions": new_gaps,
        "overlap_dimensions": new_overlaps,
        "diversity_delta": round(new_diversity - current_diversity, 4),
        "gaps_filled": gaps_filled,
        "new_overlaps": added_overlaps,
    }
