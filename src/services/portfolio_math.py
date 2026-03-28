"""Portfolio optimization math — pure functions, no DB or LLM access.

Efficient frontier computation, scenario sensitivity, and ROI estimation
for staffing plan optimization.
"""

import statistics


def compute_efficient_frontier(
    roles: list[dict],
    candidates_per_role: dict[str, list[dict]],
    budget_levels: list[float],
    constraints: list[str] | None = None,
) -> list[dict]:
    """Compute the efficient frontier of staffing plans across budget levels.

    Greedy algorithm: rank all (role, candidate) pairs by
    resilience_improvement/cost, then fill greedily at each budget level.

    Args:
        roles: List of role dicts with id, title.
        candidates_per_role: Dict of role_id -> list of candidate dicts,
            each with candidate_id, name, fit_score, cost_eur.
        budget_levels: List of budget amounts to compute frontier for.
        constraints: Optional list of constraint descriptions.

    Returns:
        List of frontier point dicts, one per budget level, with
        budget_eur, resilience_improvement, selected_hires, roi.
    """
    # Build ranked options: (role_title, candidate_name, cost, resilience, efficiency)
    options: list[tuple[str, str, float, float]] = []
    for role in roles:
        role_id = role["id"]
        role_title = role.get("title", role_id)
        for cand in candidates_per_role.get(role_id, []):
            cost = max(cand.get("cost_eur", 10_000), 1.0)
            resilience = cand.get("fit_score", 0.5)
            options.append((role_title, cand.get("name", "Unknown"), cost, resilience))

    # Sort by efficiency (resilience / cost) descending
    options.sort(key=lambda x: x[3] / x[2], reverse=True)

    frontier: list[dict] = []
    for budget in sorted(budget_levels):
        remaining = budget
        total_resilience = 0.0
        total_cost = 0.0
        selected: list[str] = []
        used_roles: set[str] = set()

        for role_title, cand_name, cost, resilience in options:
            if role_title in used_roles:
                continue
            if cost <= remaining:
                remaining -= cost
                total_cost += cost
                total_resilience += resilience
                selected.append(role_title)
                used_roles.add(role_title)

        roi = (total_resilience - total_cost / max(budget, 1)) / max(total_cost / max(budget, 1), 0.01) if total_cost > 0 else 0.0

        frontier.append({
            "budget_eur": budget,
            "resilience_improvement": round(total_resilience, 4),
            "selected_hires": selected,
            "roi": round(roi, 4),
        })

    return frontier


def compute_scenario_sensitivity(
    candidate_rankings: dict[str, dict[str, int]],
) -> dict[str, float]:
    """Compute how sensitive candidate rankings are to scenario changes.

    Args:
        candidate_rankings: Dict of scenario_name -> {candidate_id: rank_position}.

    Returns:
        Dict of candidate_id -> sensitivity score (stdev of rank positions).
        Higher = more scenario-dependent.
    """
    # Invert: candidate -> list of ranks across scenarios
    candidate_ranks: dict[str, list[int]] = {}
    for _scenario, rankings in candidate_rankings.items():
        for cand_id, rank in rankings.items():
            candidate_ranks.setdefault(cand_id, []).append(rank)

    sensitivity: dict[str, float] = {}
    for cand_id, ranks in candidate_ranks.items():
        if len(ranks) >= 2:
            sensitivity[cand_id] = round(statistics.stdev(ranks), 4)
        else:
            sensitivity[cand_id] = 0.0

    return sensitivity


def compute_roi_estimate(
    staffing_plan: dict,
    cascade_impacts: list[dict],
) -> dict:
    """Estimate ROI of a staffing plan based on avoided cascade damage.

    ROI = (risk_reduction - hiring_cost) / hiring_cost.

    Args:
        staffing_plan: Dict with items (list of hire dicts with estimated_cost_eur)
            and total_cost_eur.
        cascade_impacts: List of cascade impact dicts with estimated_cost_eur
            representing damage if roles remain unfilled.

    Returns:
        Dict with total_hiring_cost, total_risk_avoided, roi, payback_months.
    """
    total_hiring_cost = staffing_plan.get("total_cost_eur", 0)
    if not total_hiring_cost:
        total_hiring_cost = sum(
            item.get("estimated_cost_eur", 0)
            for item in staffing_plan.get("items", [])
        )

    total_risk_avoided = sum(
        c.get("estimated_cost_eur", 0) for c in cascade_impacts
    )

    roi = (
        (total_risk_avoided - total_hiring_cost) / max(total_hiring_cost, 1)
        if total_hiring_cost > 0
        else 0.0
    )

    payback_months = (
        round(total_hiring_cost / max(total_risk_avoided / 12, 1), 1)
        if total_risk_avoided > 0
        else 0
    )

    return {
        "total_hiring_cost": total_hiring_cost,
        "total_risk_avoided": round(total_risk_avoided, 2),
        "roi": round(roi, 4),
        "payback_months": payback_months,
    }
