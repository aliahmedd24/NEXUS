"""Tests for cascade engine services."""

from src.services.cascade_engine import (
    compute_cascade,
    find_optimal_intervention_point,
)


def test_cascade_stops_at_threshold():
    """Cascade stops when impact drops below 0.1."""
    deps = [
        {"upstream": "A", "downstream": "B", "coupling_strength": 0.5, "dependency_type": "production_flow"},
        {"upstream": "B", "downstream": "C", "coupling_strength": 0.3, "dependency_type": "supply_chain"},
        {"upstream": "C", "downstream": "D", "coupling_strength": 0.1, "dependency_type": "reporting"},
    ]
    chain = compute_cascade("A", 0.8, deps, 0.9)
    # A->B impact = 0.8*0.9*0.5 = 0.36, B->C = 0.36*0.3 = 0.108, C->D = 0.108*0.1 = 0.0108 (below 0.1)
    assert len(chain) <= 3
    unit_ids = [n["org_unit_id"] for n in chain]
    assert "D" not in unit_ids


def test_cascade_includes_direct_dependency():
    """Direct downstream with strong coupling is always included."""
    deps = [
        {"upstream": "A", "downstream": "B", "coupling_strength": 0.9, "dependency_type": "production_flow"},
    ]
    chain = compute_cascade("A", 0.8, deps, 1.0)
    assert len(chain) == 1
    assert chain[0]["org_unit_id"] == "B"
    assert chain[0]["impact_score"] > 0.5


def test_cascade_traverses_upstream_for_leaf_nodes():
    """Leaf nodes (no downstream edges) cascade upstream to units that depend on them."""
    deps = [
        {"upstream": "A", "downstream": "B", "coupling_strength": 0.8, "dependency_type": "budget"},
        {"upstream": "C", "downstream": "B", "coupling_strength": 0.7, "dependency_type": "shared_resource"},
    ]
    # B is a leaf — only appears as downstream, never as upstream
    chain = compute_cascade("B", 1.0, deps, 0.8)
    assert len(chain) >= 1
    unit_ids = [n["org_unit_id"] for n in chain]
    # Should traverse upstream to A and/or C
    assert "A" in unit_ids or "C" in unit_ids
    # Should NOT be empty like it was before the fix
    assert len(chain) > 0


def test_find_optimal_intervention():
    """Intervention finder returns a node."""
    cascade = [
        {"org_unit_id": "B", "depth": 1, "impact_score": 0.5},
        {"org_unit_id": "C", "depth": 2, "impact_score": 0.3},
        {"org_unit_id": "D", "depth": 3, "impact_score": 0.1},
    ]
    result = find_optimal_intervention_point(cascade)
    assert result is not None
    assert "intervention_score" in result
