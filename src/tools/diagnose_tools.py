"""Tools for DIAGNOSE mode agents.

Query Supabase for scenario/role/leader data and delegate computation
to Phase 3 services. All database access via supabase_client helpers.
"""

from src.services.cascade_engine import compute_cascade, find_optimal_intervention_point
from src.services.scenario_engine import combine_scenarios
from src.supabase_client import fetch_all, fetch_by_column, fetch_ilike, fetch_one


def get_scenario_library() -> list[dict]:
    """Retrieve all available stress scenarios from the database.

    Returns a list of scenarios with id, name, category, narrative,
    probability, capability_demand_vector, and time_horizon_months.
    """
    return fetch_all("scenarios")


def get_scenario_by_name(scenario_name: str) -> dict:
    """Retrieve a specific scenario by name or partial match.

    Args:
        scenario_name: Full or partial name of the scenario.

    Returns:
        The matching scenario object with all fields, or an error message.
    """
    results = fetch_ilike("scenarios", "name", f"%{scenario_name}%")
    if not results:
        return {"error": f"No scenario matching '{scenario_name}' found."}
    return results[0]


def create_compound_scenario(
    scenario_name_a: str, scenario_name_b: str
) -> dict:
    """Create a compound scenario combining two simultaneous crises.

    The compound demand vector uses element-wise maximum with interaction
    boosts for dimensions that are critical in both scenarios.

    Args:
        scenario_name_a: Name of the first scenario.
        scenario_name_b: Name of the second scenario.

    Returns:
        A new compound scenario with combined demands and adjusted probability.
    """
    sa = fetch_ilike("scenarios", "name", f"%{scenario_name_a}%")
    sb = fetch_ilike("scenarios", "name", f"%{scenario_name_b}%")
    if not sa or not sb:
        return {"error": "One or both scenarios not found."}

    scenario_a = sa[0]
    scenario_b = sb[0]
    demand_a = scenario_a.get("capability_demand_vector", {})
    demand_b = scenario_b.get("capability_demand_vector", {})

    combined_demand = combine_scenarios(demand_a, demand_b)

    return {
        "name": f"{scenario_a['name']} + {scenario_b['name']}",
        "category": "compound",
        "narrative": (
            f"Compound scenario: {scenario_a['name']} occurring simultaneously "
            f"with {scenario_b['name']}."
        ),
        "probability": round(scenario_a["probability"] * scenario_b["probability"], 4),
        "capability_demand_vector": combined_demand,
        "time_horizon_months": max(
            scenario_a.get("time_horizon_months", 12),
            scenario_b.get("time_horizon_months", 12),
        ),
        "affected_org_units": list(
            set(scenario_a.get("affected_org_units", []))
            | set(scenario_b.get("affected_org_units", []))
        ),
    }


def scan_vulnerabilities(scenario_id: str) -> dict:
    """Run vulnerability scan: evaluate all critical leadership roles against a scenario.

    For each filled role, computes gap between leader's genome and scenario demands.
    Vacant roles are automatic RED. Returns a heatmap with aggregate resilience score.

    Args:
        scenario_id: UUID of the scenario to test against.

    Returns:
        Heatmap data with per-role gap scores, status colors, and aggregate resilience.
    """
    scenario = fetch_one("scenarios", scenario_id)
    if not scenario:
        return {"error": f"Scenario {scenario_id} not found."}

    demand_vector = scenario["capability_demand_vector"]
    roles = fetch_all("roles")
    critical_roles = [
        r for r in roles if r.get("criticality") in ("critical", "high")
    ]

    results = []
    for role in critical_roles:
        if role.get("current_holder_id"):
            scores = fetch_by_column(
                "leader_capability_scores", "leader_id", role["current_holder_id"]
            )
            # Build genome dict (scores already on 0-1 scale)
            genome: dict[str, float] = {}
            for s in scores:
                if s.get("assessor_type") == "composite":
                    score_val = s.get("corrected_score") or s.get("raw_score", 0.5)
                    genome[s["dimension"]] = score_val

            gap_dimensions: dict[str, float] = {}
            total_gap = 0.0
            total_weight = 0.0
            for dim, demand in demand_vector.items():
                current = genome.get(dim, 0.5)
                gap = max(0, demand - current)
                gap_dimensions[dim] = round(gap, 3)
                total_gap += gap * demand
                total_weight += demand

            gap_score = round(total_gap / max(total_weight, 0.01), 3)
            status = (
                "green"
                if gap_score < 0.15
                else ("yellow" if gap_score < 0.35 else "red")
            )
            leader = fetch_one("leaders", role["current_holder_id"])
            leader_name = leader["full_name"] if leader else "Unknown"
        else:
            gap_score = 1.0
            status = "red"
            gap_dimensions = {dim: demand for dim, demand in demand_vector.items()}
            leader_name = None

        results.append(
            {
                "role_id": role["id"],
                "role_title": role["title"],
                "leader_name": leader_name,
                "gap_score": gap_score,
                "status": status,
                "gap_dimensions": gap_dimensions,
            }
        )

    critical = sum(1 for r in results if r["status"] == "red")
    warning = sum(1 for r in results if r["status"] == "yellow")
    covered = sum(1 for r in results if r["status"] == "green")
    resilience = round(
        1.0 - (sum(r["gap_score"] for r in results) / max(len(results), 1)),
        3,
    )

    return {
        "scenario_name": scenario["name"],
        "heatmap": results,
        "critical_count": critical,
        "warning_count": warning,
        "covered_count": covered,
        "aggregate_resilience_score": resilience,
    }


def compute_cascade_impact(role_id: str, scenario_id: str) -> dict:
    """Model cascade impact if a role fails under a scenario.

    Traces the dependency graph downstream from the role's org unit,
    computing impact at each node and quantifying total EUR exposure.

    Args:
        role_id: UUID of the vulnerable role.
        scenario_id: UUID of the active scenario.

    Returns:
        Cascade chain, total impact in EUR, and optimal intervention point.
    """
    role = fetch_one("roles", role_id)
    scenario = fetch_one("scenarios", scenario_id)
    if not role or not scenario:
        return {"error": "Role or scenario not found."}

    # Transform org_dependencies to the format compute_cascade expects
    raw_deps = fetch_all("org_dependencies")
    dependencies = [
        {
            "upstream": d["upstream_unit_id"],
            "downstream": d["downstream_unit_id"],
            "coupling_strength": d.get("coupling_strength", 0.5),
            "dependency_type": d.get("dependency_type", "unknown"),
        }
        for d in raw_deps
    ]

    # Use a default gap score based on whether role is filled
    gap_score = 0.7 if role.get("current_holder_id") else 1.0

    chain = compute_cascade(
        start_unit_id=role["org_unit_id"],
        gap_score=gap_score,
        dependencies=dependencies,
        scenario_severity=scenario.get("probability", 0.5),
    )

    intervention = find_optimal_intervention_point(chain)

    # Enrich chain nodes with org unit names
    org_units = {u["id"]: u["name"] for u in fetch_all("org_units")}
    for node in chain:
        node["org_unit_name"] = org_units.get(node["org_unit_id"], "Unknown")

    return {
        "role_title": role["title"],
        "scenario_name": scenario["name"],
        "cascade_chain": chain,
        "total_impact_eur": sum(n.get("estimated_cost_eur", 0) for n in chain),
        "optimal_intervention": intervention,
    }


def identify_single_points_of_failure() -> list[dict]:
    """Find leaders who are the sole holder of a critical capability.

    Returns leaders where they are the only person in the organization
    scoring above 7.0 (on 0-10 scale) on a dimension.

    Returns:
        List of SPOF entries with leader name, dimension, and backup count.
    """
    all_scores = fetch_all("leader_capability_scores")
    leaders = fetch_all("leaders")
    current_leaders = {
        l["id"]: l for l in leaders if l.get("leader_type") == "internal_current"
    }

    # Group by dimension: find dims where only 1 current leader scores > 0.85
    dim_holders: dict[str, list[dict]] = {}
    for score in all_scores:
        score_val = score.get("corrected_score") or score.get("raw_score", 0)
        if score_val >= 0.85 and score["leader_id"] in current_leaders:
            dim_holders.setdefault(score["dimension"], []).append(
                {
                    "leader_id": score["leader_id"],
                    "leader_name": current_leaders[score["leader_id"]]["full_name"],
                    "score": score_val,
                }
            )

    spofs = []
    for dim, holders in dim_holders.items():
        if len(holders) == 1:
            spofs.append(
                {
                    "dimension": dim,
                    "leader_name": holders[0]["leader_name"],
                    "score": holders[0]["score"],
                    "backup_count": 0,
                    "risk": "CRITICAL — no backup for this capability",
                }
            )

    return spofs
