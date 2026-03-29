"""Cascade failure engine — pure functions, no DB or LLM access.

BFS traversal of org dependency graph to model cascading impacts
from leadership vacancies or capability gaps.
"""

from collections import deque


def compute_cascade(
    start_unit_id: str,
    gap_score: float,
    dependencies: list[dict],
    scenario_severity: float = 1.0,
) -> list[dict]:
    """Compute cascade failure chain from a starting org unit.

    BFS from start unit through dependency graph. Impact attenuates
    by coupling_strength at each step. Stops at depth 5 or impact < 0.1.

    Args:
        start_unit_id: UUID string of the originating org unit.
        gap_score: Initial gap severity (0-1).
        dependencies: List of dependency dicts with keys:
            upstream, downstream, coupling_strength, dependency_type.
        scenario_severity: Multiplier from active scenario (0-1).

    Returns:
        List of cascade node dicts in BFS order.
    """
    max_depth = 5
    min_impact = 0.1

    # Build adjacency lists in both directions — coupling is neutral (0.5)
    # for all edges. The LLM reasons about actual coupling strength from
    # dependency type and organizational context.
    adj_down: dict[str, list[tuple[str, float, str]]] = {}
    adj_up: dict[str, list[tuple[str, float, str]]] = {}
    for dep in dependencies:
        upstream = dep["upstream"]
        downstream = dep["downstream"]
        coupling = 0.5  # neutral — no hardcoded bias
        dep_type = dep.get("dependency_type", "unknown")
        adj_down.setdefault(upstream, []).append((downstream, coupling, dep_type))
        adj_up.setdefault(downstream, []).append((upstream, coupling, dep_type))

    # If the start unit has no downstream edges, it is a leaf node.
    # A leaf failure cascades UPSTREAM — units that depend on it are affected.
    has_downstream = start_unit_id in adj_down
    adj = adj_down if has_downstream else adj_up

    visited: set[str] = {start_unit_id}
    queue: deque[tuple[str, float, int]] = deque()
    cascade: list[dict] = []

    # Seed with direct neighbors (downstream, or upstream for leaf nodes)
    initial_impact = gap_score * scenario_severity
    for neighbor, coupling, dep_type in adj.get(start_unit_id, []):
        impact = initial_impact * coupling
        if impact >= min_impact and neighbor not in visited:
            queue.append((neighbor, impact, 1))
            visited.add(neighbor)

    while queue:
        unit_id, impact, depth = queue.popleft()

        node = {
            "org_unit_id": unit_id,
            "depth": depth,
            "impact_score": round(impact, 4),
            "dependency_type": "",
            "coupling_strength": 0.0,
        }

        # Find which dependency brought us here (for metadata)
        for dep in dependencies:
            if dep["downstream"] == unit_id and dep["upstream"] in visited:
                node["dependency_type"] = dep.get("dependency_type", "")
                node["coupling_strength"] = dep.get("coupling_strength", 0.0)
                break

        # Quantify impact
        quantified = quantify_impact(node, node["dependency_type"], unit_id)
        node.update(quantified)
        cascade.append(node)

        # Continue BFS if within limits
        if depth < max_depth:
            for neighbor, coupling, dep_type in adj.get(unit_id, []):
                child_impact = impact * coupling
                if child_impact >= min_impact and neighbor not in visited:
                    queue.append((neighbor, child_impact, depth + 1))
                    visited.add(neighbor)

    return cascade


def find_optimal_intervention_point(cascade: list[dict]) -> dict | None:
    """Find the best node to intervene in a cascade chain.

    Scores each node: blocked_downstream_impact / estimated_intervention_cost.
    Returns the node with the highest score.

    Args:
        cascade: List of cascade nodes from compute_cascade.

    Returns:
        Best intervention node dict, or None if cascade is empty.
    """
    if not cascade:
        return None

    best_node = None
    best_score = -1.0

    for i, node in enumerate(cascade):
        # Estimate downstream impact that would be blocked
        downstream_impact = sum(
            n["impact_score"] for n in cascade[i + 1:]
            if n["depth"] > node["depth"]
        )

        # Intervention cost estimate: proportional to impact + depth
        intervention_cost = max(node["impact_score"] * (1 + node["depth"] * 0.2), 0.01)

        score = downstream_impact / intervention_cost

        if score > best_score:
            best_score = score
            best_node = dict(node)
            best_node["intervention_score"] = round(score, 4)
            best_node["blocked_downstream_impact"] = round(downstream_impact, 4)

    return best_node


def quantify_impact(
    cascade_node: dict,
    dependency_type: str,
    org_unit_id: str,
) -> dict:
    """Quantify financial and operational impact of a cascade node.

    Args:
        cascade_node: The cascade node dict.
        dependency_type: Type of dependency (production_flow, quality_gate, etc.)
        org_unit_id: The affected org unit ID.

    Returns:
        Dict with mechanical_cost_eur, estimated_delay_days, units_affected.
    """
    impact = cascade_node.get("impact_score", 0.0)

    if dependency_type == "production_flow":
        return {
            "mechanical_cost_eur": round(impact * 500_000, 2),
            "estimated_delay_days": 0,
            "units_affected": round(impact * 1000),
        }
    elif dependency_type == "quality_gate":
        return {
            "mechanical_cost_eur": round(impact * 200_000, 2),
            "estimated_delay_days": round(impact * 14),
            "units_affected": 0,
        }
    elif dependency_type == "supply_chain":
        return {
            "mechanical_cost_eur": round(impact * 300_000, 2),
            "estimated_delay_days": round(impact * 21),
            "units_affected": round(impact * 500),
        }
    else:
        return {
            "mechanical_cost_eur": round(impact * 100_000, 2),
            "estimated_delay_days": round(impact * 7),
            "units_affected": 0,
        }
