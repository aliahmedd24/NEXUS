"""Tools for LEARN mode agents.

Provides retrieval, replay, and bias-correction tools for the Decision
Replay Agent and Pattern Intelligence Agent. Includes RAG-powered
semantic search from Phase 2.5 and the critical LEARN -> STAFF feedback
loop via calibration coefficient writes.
"""

import json

from src.embeddings import embed_query
from src.services.bias_correction import (
    compute_calibration_coefficients,
    detect_historical_biases,
)
from src.services.genome_computation import compute_weighted_fit_score
from src.supabase_client import (
    fetch_all,
    fetch_by_column,
    fetch_one,
    semantic_search_decisions,
    upsert,
)


# ─── RAG Tool (from Phase 2.5) ─────────────────────────────────────────


def find_analogous_decisions(
    context_description: str, top_k: int = 3,
) -> list[dict]:
    """Find past hiring decisions most similar to a current vacancy context.

    Instead of replaying ALL historical decisions sequentially, this tool
    retrieves only the most analogous past decisions based on semantic
    similarity of the decision reasoning and context.

    Use this to:
    - Find historical precedents for the current hiring decision
    - Learn from past decisions made in similar circumstances
    - Identify patterns: "the last 3 times we hired for a similar context,
      we overweighted X"

    Args:
        context_description: Natural language description of the current vacancy
            context. Example: "Hiring a VP Production for a plant transitioning
            from ICE to full EV manufacturing, with 6500 employees and active
            construction on site."
        top_k: Number of analogous decisions to return (default 3).

    Returns:
        List of similar past decisions with: role_title, decision_date,
        scenario_at_decision, decision_reasoning, selected_candidate_name,
        and similarity score.
    """
    query_vector = embed_query(context_description)
    results = semantic_search_decisions(
        query_embedding=query_vector,
        top_k=top_k,
        threshold=0.35,
    )

    # Enrich with role titles and candidate names
    for r in results:
        role = fetch_one("roles", r["role_id"])
        r["role_title"] = role["title"] if role else "Unknown"
        selected = fetch_one("leaders", r["selected_candidate_id"])
        r["selected_candidate_name"] = (
            selected["full_name"] if selected else "Unknown"
        )
        if r.get("runner_up_candidate_id"):
            runner = fetch_one("leaders", r["runner_up_candidate_id"])
            r["runner_up_name"] = runner["full_name"] if runner else "Unknown"

    return results


# ─── Decision Replay Tools ─────────────────────────────────────────────


def get_historical_decisions(limit: int = 10) -> list[dict]:
    """Retrieve past leadership decisions with outcomes.

    Returns decisions with role, date, selected/runner-up candidates,
    criteria used, and outcomes at 6/12/18/24 months.

    Args:
        limit: Maximum decisions to return (default 10).

    Returns:
        List of decisions with nested outcome data.
    """
    decisions = fetch_all("historical_decisions")[:limit]
    for d in decisions:
        d["outcomes"] = fetch_by_column(
            "decision_outcomes", "decision_id", d["id"],
        )
        role = fetch_one("roles", d["role_id"])
        d["role_title"] = role["title"] if role else "Unknown"
        selected = fetch_one("leaders", d["selected_candidate_id"])
        d["selected_name"] = selected["full_name"] if selected else "Unknown"
        if d.get("runner_up_candidate_id"):
            runner = fetch_one("leaders", d["runner_up_candidate_id"])
            d["runner_up_name"] = runner["full_name"] if runner else "Unknown"
    return decisions


def reconstruct_decision(decision_id: str) -> dict:
    """Fully reconstruct a past hiring decision with all context.

    Args:
        decision_id: UUID of the historical decision.

    Returns:
        Full context: candidates, criteria, reasoning, and outcomes.
    """
    decision = fetch_one("historical_decisions", decision_id)
    if not decision:
        return {"error": "Decision not found."}
    decision["outcomes"] = fetch_by_column(
        "decision_outcomes", "decision_id", decision_id,
    )
    # Get genomes for selected and runner-up
    for key in ["selected_candidate_id", "runner_up_candidate_id"]:
        cid = decision.get(key)
        if cid:
            scores = fetch_by_column(
                "leader_capability_scores", "leader_id", cid,
            )
            leader = fetch_one("leaders", cid)
            decision[key.replace("_id", "_genome")] = {
                s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
                for s in scores
                if s.get("assessor_type") == "composite"
            }
            decision[key.replace("_id", "_name")] = (
                leader["full_name"] if leader else "Unknown"
            )
    return decision


def get_decision_outcomes(decision_id: str) -> dict:
    """Retrieve actual outcomes for a historical hire at all time horizons.

    Args:
        decision_id: UUID of the historical decision.

    Returns:
        Outcomes at 6, 12, 18, 24 months with computed quality-of-hire score.
    """
    outcomes = fetch_by_column(
        "decision_outcomes", "decision_id", decision_id,
    )
    for o in outcomes:
        # Compute composite Quality of Hire (QoH)
        o["quality_of_hire"] = round(
            0.30 * (o.get("performance_rating", 5) / 10)
            + 0.25 * (o.get("goal_completion_pct", 50) / 100)
            + 0.20 * max(0, 0.5 + o.get("team_engagement_delta", 0))
            + 0.15 * max(0, 0.5 - o.get("team_attrition_delta", 0))
            + 0.10 * (1.0 if o.get("still_in_role", True) else 0.0),
            3,
        )
    return {"decision_id": decision_id, "outcomes": outcomes}


def simulate_counterfactual(
    decision_id: str, alternative_candidate_id: str,
) -> dict:
    """Simulate what would have happened with a different candidate.

    Uses the alternative candidate's genome, the role's requirements,
    and fit scoring to predict outcomes and compare against actual results.

    Args:
        decision_id: UUID of the historical decision.
        alternative_candidate_id: UUID of the candidate who wasn't chosen.

    Returns:
        Simulated outcomes with divergence score and category.
    """
    decision = fetch_one("historical_decisions", decision_id)
    if not decision:
        return {"error": f"Decision {decision_id} not found."}

    actual_outcomes = fetch_by_column(
        "decision_outcomes", "decision_id", decision_id,
    )
    role = fetch_one("roles", decision["role_id"])
    if not role:
        return {"error": f"Role for decision {decision_id} not found."}

    # Get alternative candidate genome
    alt_scores = fetch_by_column(
        "leader_capability_scores", "leader_id", alternative_candidate_id,
    )
    alt_genome = {
        s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
        for s in alt_scores
        if s.get("assessor_type") == "composite"
    }

    # Get role requirements from JD template
    required: dict[str, float] = {}
    if role.get("jd_template_id"):
        template = fetch_one("jd_templates", role["jd_template_id"])
        if template:
            required = template.get("competency_weightings", {})

    # Simulate fit -> predicted performance
    alt_fit = compute_weighted_fit_score(alt_genome, required) if required else 0.5

    # Compute divergence from actual outcome
    actual_qoh = 0.5
    if actual_outcomes:
        latest = max(actual_outcomes, key=lambda x: x["months_elapsed"])
        actual_qoh = latest.get("performance_rating", 5) / 10

    divergence = round(abs(alt_fit - actual_qoh), 3)
    category = (
        "optimal" if divergence < 0.05
        else "suboptimal" if divergence < 0.15
        else "costly_error" if divergence < 0.30
        else "critical_miss"
    )

    alt_leader = fetch_one("leaders", alternative_candidate_id)
    return {
        "decision_id": decision_id,
        "alternative_candidate_id": alternative_candidate_id,
        "alternative_candidate_name": (
            alt_leader["full_name"] if alt_leader else "Unknown"
        ),
        "predicted_fit_score": round(alt_fit, 3),
        "actual_quality_of_hire": round(actual_qoh, 3),
        "divergence_score": divergence,
        "divergence_category": category,
    }


# ─── Pattern Intelligence Tools ────────────────────────────────────────


def detect_bias_patterns() -> dict:
    """Analyze all historical decisions to find systematic biases.

    Correlates decision criteria weights with outcome quality to identify
    overweighted and underweighted dimensions.

    Returns:
        Dict of dimension -> overweight factor. Positive = overweighted,
        negative = underweighted. Zero = well-calibrated.
    """
    decisions = fetch_all("historical_decisions")
    outcomes = fetch_all("decision_outcomes")
    return detect_historical_biases(decisions, outcomes)


def get_calibration_coefficients() -> dict:
    """Retrieve current calibration coefficients from Supabase.

    Returns:
        Dict of {dimension: correction_factor}. Empty dict if none exist.
    """
    rows = fetch_all("calibration_coefficients")
    return {r["dimension"]: r["correction_factor"] for r in rows}


def update_calibration_from_biases(biases_json: str) -> dict:
    """Compute and write updated calibration coefficients to Supabase.

    This is the critical LEARN -> STAFF feedback loop write.
    Converts detected biases into correction factors and persists them
    so STAFF mode's compute_candidate_fit applies them automatically.

    Args:
        biases_json: JSON string of {dimension: overweight_factor} from
            detect_bias_patterns.

    Returns:
        Updated calibration coefficients with status.
    """
    biases = json.loads(biases_json) if isinstance(biases_json, str) else biases_json
    coefficients = compute_calibration_coefficients(biases)

    # Write to Supabase — use dimension as the on_conflict key
    # since dimension has a UNIQUE constraint
    rows = [
        {
            "dimension": dim,
            "correction_factor": coeff,
            "historical_overweight": biases.get(dim, 0),
            "evidence_count": 1,
            "confidence": 0.7,
        }
        for dim, coeff in coefficients.items()
    ]

    # Upsert each row individually to handle the UNIQUE constraint on dimension
    sb = __import__("src.supabase_client", fromlist=["get_supabase"]).get_supabase()
    for row in rows:
        sb.table("calibration_coefficients").upsert(
            row, on_conflict="dimension",
        ).execute()

    return {"status": "updated", "coefficients": coefficients}
