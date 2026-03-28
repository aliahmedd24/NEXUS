"""Scenario engine — pure functions, no DB or LLM access.

Adapts JD weightings based on scenario demand vectors and combines
compound scenarios.
"""


def adapt_jd_weightings(
    base_weightings: dict[str, float],
    demand_vector: dict[str, float],
) -> tuple[dict[str, float], list[str]]:
    """Adapt job description weightings based on scenario demand.

    adapted[dim] = base[dim] * (0.5 + 0.5 * demand[dim]).
    Renormalize to sum to 1.0. Track significant changes.

    Args:
        base_weightings: Dict of dimension -> weight (should sum to ~1.0).
        demand_vector: Dict of dimension -> demand intensity (0-1).

    Returns:
        Tuple of (adapted_weightings dict summing to 1.0,
        list of change description strings).
    """
    if not base_weightings:
        return {}, []

    adapted: dict[str, float] = {}
    for dim, base_weight in base_weightings.items():
        demand = demand_vector.get(dim, 0.5)
        adapted[dim] = base_weight * (0.5 + 0.5 * demand)

    # Renormalize to sum to 1.0
    total = sum(adapted.values())
    if total > 0:
        adapted = {dim: round(w / total, 4) for dim, w in adapted.items()}

    # Track significant changes
    changes: list[str] = []
    for dim in base_weightings:
        old = base_weightings[dim]
        new = adapted.get(dim, 0.0)
        delta = new - old
        if abs(delta) > 0.03:
            direction = "increased" if delta > 0 else "decreased"
            changes.append(
                f"{dim}: {old:.2f} -> {new:.2f} ({direction} by {abs(delta):.2f})"
            )

    return adapted, changes


def combine_scenarios(
    scenario_a: dict[str, float],
    scenario_b: dict[str, float],
) -> dict[str, float]:
    """Combine two scenario demand vectors into a compound scenario.

    Demand = element-wise max. Interaction boost for dimensions that
    are critical (>0.7) in both scenarios.

    Args:
        scenario_a: Dict of dimension -> demand (0-1).
        scenario_b: Dict of dimension -> demand (0-1).

    Returns:
        Combined demand vector dict.
    """
    all_dims = set(scenario_a.keys()) | set(scenario_b.keys())
    combined: dict[str, float] = {}

    for dim in all_dims:
        val_a = scenario_a.get(dim, 0.0)
        val_b = scenario_b.get(dim, 0.0)

        # Element-wise max
        base = max(val_a, val_b)

        # Interaction boost: if both scenarios stress this dimension
        if val_a > 0.7 and val_b > 0.7:
            boost = 0.1 * min(val_a, val_b)
            base = min(base + boost, 1.0)

        combined[dim] = round(base, 4)

    return combined
