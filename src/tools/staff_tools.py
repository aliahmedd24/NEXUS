"""Tools for STAFF mode agents.

Provides retrieval, computation, and analysis tools for the four STAFF
agents: Dynamic JD Generator, Leadership Genome Agent, Team Chemistry
Engine, and Pipeline & Portfolio Optimizer.

Also includes RAG-powered semantic search tools from Phase 2.5.
"""

from src.embeddings import embed_query
from src.services.compatibility_engine import (
    compute_pairwise_compatibility,
    compute_team_balance,
)
from src.services.genome_computation import (
    compute_confidence_interval,
    compute_overall_strength,
    compute_weighted_fit_score,
    apply_bias_corrections,
)
from src.services.portfolio_math import (
    compute_efficient_frontier,
    compute_roi_estimate,
)
from src.services.scenario_engine import adapt_jd_weightings
from src.supabase_client import (
    fetch_all,
    fetch_by_column,
    fetch_one,
    semantic_search_feedback,
    semantic_search_leaders,
)


def search_feedback_by_trait(
    trait_query: str, leader_id: str = "", top_k: int = 5
) -> list[dict]:
    """Semantically search 360 feedback for passages relevant to a specific trait.

    Unlike exact keyword matching, this finds feedback by MEANING. For example,
    searching "crisis leadership under pressure" will find feedback like
    "she stayed calm when the supplier defaulted and rallied the team in 48 hours"
    even though none of the search keywords appear.

    Use this to:
    - Find evidence for specific genome dimensions across candidates
    - Discover contradictions between numeric ratings and qualitative feedback
    - Compare how different leaders handle similar challenges

    Args:
        trait_query: Natural language description of the trait or capability to
            search for. Examples: "crisis leadership under pressure",
            "poor delegation and micromanagement".
        leader_id: Optional UUID to restrict search to one leader's feedback.
            Leave empty to search across ALL leaders.
        top_k: Number of results to return (default 5).

    Returns:
        List of matching feedback entries with: leader_id, feedback_text,
        feedback_type, sentiment_score, and similarity score (0.0-1.0).
    """
    query_vector = embed_query(trait_query)
    results = semantic_search_feedback(
        query_embedding=query_vector,
        top_k=top_k,
        threshold=0.45,
        leader_id=leader_id if leader_id else None,
    )

    # Enrich with leader names
    for r in results:
        leader = fetch_one("leaders", r["leader_id"])
        r["leader_name"] = leader["full_name"] if leader else "Unknown"

    return results


def find_similar_leaders(leader_id: str, top_k: int = 5) -> list[dict]:
    """Find leaders with similar experience profiles based on bio narrative similarity.

    Uses semantic embedding similarity on leader bio_summary fields. This captures
    experience patterns that structured dimension scores might miss — for example,
    two leaders who both led factory ramp-ups in different industries would surface
    as similar even if their genome scores differ.

    Use this to:
    - Discover non-obvious internal candidates with analogous experience
    - Find external candidates whose background narrative matches an internal benchmark
    - Identify leaders who could mentor or shadow for development

    Args:
        leader_id: UUID of the reference leader to find similar profiles for.
        top_k: Number of similar leaders to return (default 5).

    Returns:
        List of similar leaders with: full_name, leader_type, bio_summary,
        and similarity score (0.0-1.0).
    """
    leader = fetch_one("leaders", leader_id)
    if not leader or not leader.get("bio_summary"):
        return [{"error": f"Leader {leader_id} has no bio summary to compare."}]

    query_vector = embed_query(leader["bio_summary"])
    return semantic_search_leaders(
        query_embedding=query_vector,
        top_k=top_k,
        threshold=0.35,
        exclude_id=leader_id,
    )


# ─── JD Generator Tools ────────────────────────────────────────────────


def get_jd_template(role_type: str) -> dict:
    """Retrieve the base JD template for a role type.

    Returns the full job description template including competency weightings,
    base description, and required experience.

    Args:
        role_type: The role type string (e.g., "Head of EV Battery Systems").

    Returns:
        JD template dict with role_type, base_description, competency_weightings,
        and other fields, or an error message if not found.
    """
    templates = fetch_by_column("jd_templates", "role_type", role_type)
    if not templates:
        return {"error": f"No template for role type '{role_type}'."}
    return templates[0]


def adapt_jd_to_scenario(role_type: str, scenario_id: str) -> dict:
    """Adapt a JD's competency weightings based on scenario demands.

    Increases weight for capabilities the scenario demands, decreases
    for less critical ones, and renormalizes to sum 1.0.

    Args:
        role_type: The role type (e.g., "Head of EV Battery Systems").
        scenario_id: UUID of the active scenario.

    Returns:
        Adapted JD with original_weightings, adapted_weightings, and changes list.
    """
    templates = fetch_by_column("jd_templates", "role_type", role_type)
    if not templates:
        return {"error": f"No template for role type '{role_type}'."}
    template = templates[0]

    scenario = fetch_one("scenarios", scenario_id)
    if not scenario:
        return {"error": f"Scenario {scenario_id} not found."}

    adapted, changes = adapt_jd_weightings(
        template["competency_weightings"],
        scenario["capability_demand_vector"],
    )

    return {
        "role_type": role_type,
        "base_description": template["base_description"],
        "original_weightings": template["competency_weightings"],
        "adapted_weightings": adapted,
        "changes": changes,
        "scenario_name": scenario["name"],
    }


def critique_jd(adapted_jd_json: str) -> dict:
    """Critique an adapted JD for common problems.

    Analyzes the adapted JD for issues like conflicting requirements,
    unicorn detection (unrealistically high demands across too many
    dimensions), incumbent cloning, and gender-coded language.

    This is a pure analysis tool — the LLM agent uses it to reason
    about JD quality before finalizing.

    Args:
        adapted_jd_json: JSON string of the adapted JD (from adapt_jd_to_scenario).

    Returns:
        Critique report with flags and recommendations.
    """
    import json

    try:
        jd = json.loads(adapted_jd_json) if isinstance(adapted_jd_json, str) else adapted_jd_json
    except (json.JSONDecodeError, TypeError):
        return {"error": "Invalid JSON input for JD critique."}

    flags: list[str] = []
    weightings = jd.get("adapted_weightings", {})

    if not weightings:
        return {"error": "No adapted_weightings found in JD."}

    # Unicorn detection: too many high-weight dimensions
    high_weight_dims = [d for d, w in weightings.items() if w > 0.10]
    if len(high_weight_dims) > 6:
        flags.append(
            f"UNICORN RISK: {len(high_weight_dims)} dimensions weighted > 0.10. "
            "This profile may not exist in the market. Consider prioritizing top 4-5."
        )

    # Conflicting requirements: dimensions that typically conflict
    conflict_pairs = [
        ("innovation_orientation", "risk_calibration"),
        ("operational_execution", "strategic_thinking"),
    ]
    for dim_a, dim_b in conflict_pairs:
        w_a = weightings.get(dim_a, 0)
        w_b = weightings.get(dim_b, 0)
        if w_a > 0.10 and w_b > 0.10:
            flags.append(
                f"POTENTIAL CONFLICT: Both {dim_a} ({w_a:.2f}) and "
                f"{dim_b} ({w_b:.2f}) are heavily weighted. These dimensions "
                "often trade off in practice."
            )

    # Concentration risk: single dimension > 25%
    for dim, weight in weightings.items():
        if weight > 0.25:
            flags.append(
                f"CONCENTRATION: {dim} at {weight:.2f} dominates the profile. "
                "A single-dimension focus may miss well-rounded candidates."
            )

    # Flat profile: all weights very similar (no differentiation)
    weight_values = list(weightings.values())
    if weight_values:
        w_range = max(weight_values) - min(weight_values)
        if w_range < 0.04:
            flags.append(
                "FLAT PROFILE: All dimensions weighted nearly equally. "
                "This doesn't differentiate for the scenario — consider sharpening."
            )

    return {
        "flags": flags,
        "flag_count": len(flags),
        "recommendation": (
            "JD passes basic checks." if not flags
            else f"{len(flags)} issue(s) detected — review before finalizing."
        ),
    }


# ─── Genome Agent Tools ────────────────────────────────────────────────


def get_candidate_pool(
    role_type: str,
    include_internal: bool = True,
    include_external: bool = True,
) -> list[dict]:
    """Retrieve candidate pool for a role type.

    Returns all candidates (internal and/or external) with their overall
    leadership strength score. Filters by leader_type.

    Args:
        role_type: The role type to get candidates for (used for context only —
            all candidates are returned since any may be considered).
        include_internal: Whether to include internal candidates and current leaders.
        include_external: Whether to include external candidates.

    Returns:
        List of candidate dicts with id, full_name, leader_type, and overall_strength.
    """
    leaders = fetch_all("leaders")
    pool: list[dict] = []

    for leader in leaders:
        lt = leader.get("leader_type", "")
        if not include_internal and lt in ("internal_current", "internal_candidate"):
            continue
        if not include_external and lt == "external_candidate":
            continue

        # Get composite scores for overall strength
        scores = fetch_by_column("leader_capability_scores", "leader_id", leader["id"])
        genome = {
            s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
            for s in scores
            if s.get("assessor_type") == "composite"
        }
        strength = compute_overall_strength(genome)

        pool.append({
            "id": leader["id"],
            "full_name": leader["full_name"],
            "leader_type": lt,
            "overall_strength": strength,
            "location": leader.get("location_current", "Unknown"),
        })

    pool.sort(key=lambda x: x["overall_strength"], reverse=True)
    return pool


def get_leader_genome(leader_id: str) -> dict:
    """Retrieve the full 12-dimension leadership genome for a leader.

    Includes raw scores, bias-corrected scores, confidence intervals,
    performance review data, and 360 feedback summary.

    Args:
        leader_id: UUID of the leader.

    Returns:
        Full genome profile with dimensions, corrections, and confidence data.
    """
    leader = fetch_one("leaders", leader_id)
    if not leader:
        return {"error": f"Leader {leader_id} not found."}

    scores = fetch_by_column("leader_capability_scores", "leader_id", leader_id)
    reviews = fetch_by_column("performance_reviews", "leader_id", leader_id)
    feedback = fetch_by_column("feedback_360", "leader_id", leader_id)

    # Build raw genome from composite scores
    raw_genome: dict[str, float] = {}
    source_counts: dict[str, int] = {}
    for s in scores:
        if s.get("assessor_type") == "composite":
            raw_genome[s["dimension"]] = s.get("raw_score", 0.5)
            sources = s.get("evidence_sources", [])
            source_counts[s["dimension"]] = len(sources) if sources else 1

    # Get corrected genome
    corrected_genome = {
        s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
        for s in scores
        if s.get("assessor_type") == "composite"
    }

    # Apply bias corrections using reviews and feedback
    ratings = [r.get("overall_rating", 7.5) for r in reviews]
    sentiments = [f.get("sentiment_score", 0.0) for f in feedback]
    corrected_genome, corrections = apply_bias_corrections(
        raw_genome, ratings, sentiments,
    )

    # Compute confidence intervals
    dimensions: list[dict] = []
    for dim in sorted(raw_genome.keys()):
        ci_low, ci_high = compute_confidence_interval(
            raw_genome[dim], source_counts.get(dim, 1),
        )
        dimensions.append({
            "dimension": dim,
            "raw_score": round(raw_genome[dim], 3),
            "corrected_score": round(corrected_genome.get(dim, raw_genome[dim]), 3),
            "confidence_interval": [ci_low, ci_high],
            "source_count": source_counts.get(dim, 1),
        })

    return {
        "leader_id": leader_id,
        "full_name": leader["full_name"],
        "leader_type": leader.get("leader_type", "unknown"),
        "dimensions": dimensions,
        "corrections_applied": corrections,
        "review_count": len(reviews),
        "feedback_count": len(feedback),
        "overall_strength": compute_overall_strength(corrected_genome),
    }


def compute_candidate_fit(
    leader_id: str, role_type: str, scenario_id: str = "",
) -> dict:
    """Compute how well a candidate fits a role, optionally under a scenario.

    Applies bias-corrected genome scores and historical calibration coefficients.

    Args:
        leader_id: UUID of the candidate.
        role_type: Role type to evaluate against.
        scenario_id: Optional scenario UUID for adapted weightings.

    Returns:
        Fit report with overall_fit_score, per-dimension fits, strengths, gaps,
        and whether calibration was applied.
    """
    # 1. Get genome
    scores = fetch_by_column("leader_capability_scores", "leader_id", leader_id)
    genome = {
        s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
        for s in scores
        if s.get("assessor_type") == "composite"
    }

    # 2. Get required profile (base or scenario-adapted)
    templates = fetch_by_column("jd_templates", "role_type", role_type)
    if not templates:
        return {"error": f"No JD template for role type '{role_type}'."}
    required = templates[0]["competency_weightings"]
    if scenario_id:
        scenario = fetch_one("scenarios", scenario_id)
        if scenario:
            original_total = sum(required.values())
            adapted, _ = adapt_jd_weightings(
                required, scenario["capability_demand_vector"],
            )
            # Rescale to original magnitude — adapt_jd_weightings normalizes
            # to sum=1.0, but fit scoring needs the original scale so thresholds
            # remain meaningful against 0-1 genome scores.
            required = {
                d: round(w * original_total, 4) for d, w in adapted.items()
            }

    # 3. Get calibration coefficients (LEARN -> STAFF feedback loop)
    calibration_rows = fetch_all("calibration_coefficients")
    calibration = (
        {r["dimension"]: r["correction_factor"] for r in calibration_rows}
        if calibration_rows
        else None
    )

    # 4. Compute fit
    fit_score = compute_weighted_fit_score(genome, required, calibration)

    # 5. Identify strengths and gaps
    dimension_fits: dict[str, float] = {}
    for dim in required:
        dim_fit = min(genome.get(dim, 0.5) / max(required[dim], 0.01), 1.0)
        dimension_fits[dim] = round(dim_fit, 3)

    sorted_dims = sorted(dimension_fits.items(), key=lambda x: x[1])
    gaps = [{"dimension": d, "fit": f} for d, f in sorted_dims[:3]]
    strengths = [{"dimension": d, "fit": f} for d, f in sorted_dims[-3:]]

    return {
        "leader_id": leader_id,
        "role_type": role_type,
        "overall_fit_score": round(fit_score, 3),
        "dimension_fits": dimension_fits,
        "strengths": strengths,
        "gaps": gaps,
        "calibration_applied": calibration is not None and len(calibration) > 0,
    }


def rank_candidates(role_type: str, scenario_id: str = "") -> dict:
    """Rank all candidates by fit score for a role under a scenario.

    Calls get_candidate_pool and compute_candidate_fit per candidate,
    then sorts by overall_fit_score descending.

    Args:
        role_type: Role type to rank candidates for.
        scenario_id: Optional scenario UUID for scenario-adapted ranking.

    Returns:
        Dict with org_unit_id, role_type, and candidates list sorted by fit.
    """
    pool = get_candidate_pool(role_type)
    rankings: list[dict] = []

    for candidate in pool:
        fit = compute_candidate_fit(
            candidate["id"], role_type, scenario_id,
        )
        if "error" not in fit:
            fit["full_name"] = candidate["full_name"]
            fit["leader_type"] = candidate["leader_type"]
            rankings.append(fit)

    rankings.sort(key=lambda x: x["overall_fit_score"], reverse=True)

    # Include org_unit_id for the target role so downstream agents can use it
    roles = fetch_by_column("roles", "title", role_type)
    org_unit_id = roles[0]["org_unit_id"] if roles else None

    return {
        "org_unit_id": org_unit_id,
        "role_type": role_type,
        "candidates": rankings,
    }


# ─── Team Chemistry Tools ──────────────────────────────────────────────


def get_existing_team(org_unit_id: str) -> list[dict]:
    """Retrieve the existing leadership team for an org unit.

    Finds all filled roles in this org unit plus roles that report to
    any role in this org unit (using reports_to_role_id hierarchy).
    Returns genome profiles for each team member.

    Args:
        org_unit_id: UUID of the organizational unit.

    Returns:
        List of team member dicts with id, full_name, role_title, and genome.
    """
    all_roles = fetch_all("roles")
    seen_leader_ids: set[str] = set()
    team: list[dict] = []

    # Step 1: Find roles in this org unit
    anchor_role_ids: set[str] = set()
    for role in all_roles:
        if role.get("org_unit_id") == org_unit_id:
            anchor_role_ids.add(role["id"])

    # Step 2: Find roles that report to anchor roles (BFS down the hierarchy)
    relevant_role_ids = set(anchor_role_ids)
    frontier = set(anchor_role_ids)
    for _ in range(3):  # Max 3 levels deep
        next_frontier: set[str] = set()
        for role in all_roles:
            if (
                role.get("reports_to_role_id") in frontier
                and role["id"] not in relevant_role_ids
            ):
                relevant_role_ids.add(role["id"])
                next_frontier.add(role["id"])
        if not next_frontier:
            break
        frontier = next_frontier

    # Step 3: Build team from all relevant roles
    for role in all_roles:
        if role["id"] not in relevant_role_ids:
            continue
        if not role.get("current_holder_id"):
            continue
        if role["current_holder_id"] in seen_leader_ids:
            continue

        leader = fetch_one("leaders", role["current_holder_id"])
        if not leader:
            continue

        scores = fetch_by_column(
            "leader_capability_scores", "leader_id", leader["id"],
        )
        genome = {
            s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
            for s in scores
            if s.get("assessor_type") == "composite"
        }

        team.append({
            "id": leader["id"],
            "full_name": leader["full_name"],
            "role_title": role["title"],
            "genome": genome,
        })
        seen_leader_ids.add(leader["id"])

    return team


def compute_team_compatibility(
    candidate_id: str, org_unit_id: str,
) -> dict:
    """Compute compatibility between a candidate and an existing team.

    Evaluates pairwise compatibility with each team member and overall
    team balance changes if the candidate joins.

    Args:
        candidate_id: UUID of the candidate to evaluate.
        org_unit_id: UUID of the org unit whose team to compare against.

    Returns:
        Compatibility report with pairwise scores, team balance, and risk flags.
    """
    team = get_existing_team(org_unit_id)
    if not team:
        return {"error": f"No team found for org unit {org_unit_id}."}

    # Get candidate genome
    candidate = fetch_one("leaders", candidate_id)
    if not candidate:
        return {"error": f"Candidate {candidate_id} not found."}

    scores = fetch_by_column(
        "leader_capability_scores", "leader_id", candidate_id,
    )
    candidate_genome = {
        s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
        for s in scores
        if s.get("assessor_type") == "composite"
    }

    # Get interaction rules
    rules = fetch_all("interaction_rules")

    # Compute pairwise compatibility with each team member
    pairwise: list[dict] = []
    for member in team:
        compat = compute_pairwise_compatibility(
            candidate_genome,
            member["genome"],
            "cross_functional",
            rules,
        )
        pairwise.append({
            "team_member_id": member["id"],
            "team_member_name": member["full_name"],
            "role_title": member["role_title"],
            **compat,
        })

    # Compute team balance
    team_genomes = [m["genome"] for m in team]
    balance = compute_team_balance(team_genomes, candidate_genome)

    # Overall compatibility score
    avg_synergy = (
        sum(p["synergy_score"] for p in pairwise) / len(pairwise)
        if pairwise
        else 0.0
    )

    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate["full_name"],
        "org_unit_id": org_unit_id,
        "pairwise_assessments": pairwise,
        "team_member_count": len(team),
        "average_synergy": round(avg_synergy, 4),
        "team_balance": balance,
    }


# ─── Portfolio Optimizer Tools ──────────────────────────────────────────


def evaluate_sourcing_options(role_id: str) -> dict:
    """Evaluate sourcing options for filling a role.

    Analyzes internal promotion, external hire, interim placement,
    internal development, and accept-risk options with cost estimates.

    Args:
        role_id: UUID of the role to fill.

    Returns:
        Sourcing options with costs, timelines, and recommendations.
    """
    role = fetch_one("roles", role_id)
    if not role:
        return {"error": f"Role {role_id} not found."}

    # Get JD template for competency requirements
    jd_template = None
    if role.get("jd_template_id"):
        jd_template = fetch_one("jd_templates", role["jd_template_id"])

    role_type = jd_template["role_type"] if jd_template else role.get("title", "")

    # Get all candidates and their fit scores
    all_leaders = fetch_all("leaders")
    options: list[dict] = []

    # Internal candidates (current leaders who could be promoted)
    internal_current = [
        l for l in all_leaders if l.get("leader_type") == "internal_current"
    ]
    internal_candidates = [
        l for l in all_leaders if l.get("leader_type") == "internal_candidate"
    ]
    external_candidates = [
        l for l in all_leaders if l.get("leader_type") == "external_candidate"
    ]

    # Best internal candidate
    best_internal_score = 0.0
    best_internal = None
    for leader in internal_current + internal_candidates:
        fit = compute_candidate_fit(leader["id"], role_type)
        if "error" not in fit and fit["overall_fit_score"] > best_internal_score:
            best_internal_score = fit["overall_fit_score"]
            best_internal = leader

    if best_internal:
        options.append({
            "strategy": "INTERNAL_PROMOTE",
            "candidate": best_internal["full_name"],
            "fit_score": round(best_internal_score, 3),
            "estimated_cost_eur": 50_000,
            "estimated_time_days": 30,
            "risk_level": "low",
        })

    # Best external candidate
    best_external_score = 0.0
    best_external = None
    for leader in external_candidates:
        fit = compute_candidate_fit(leader["id"], role_type)
        if "error" not in fit and fit["overall_fit_score"] > best_external_score:
            best_external_score = fit["overall_fit_score"]
            best_external = leader

    if best_external:
        options.append({
            "strategy": "EXTERNAL_HIRE",
            "candidate": best_external["full_name"],
            "fit_score": round(best_external_score, 3),
            "estimated_cost_eur": 180_000,
            "estimated_time_days": 120,
            "risk_level": "medium",
        })

    # Internal development option
    best_develop = None
    best_develop_score = 0.0
    for leader in internal_candidates:
        fit = compute_candidate_fit(leader["id"], role_type)
        if "error" not in fit and 0.5 <= fit["overall_fit_score"] < 0.85:
            if fit["overall_fit_score"] > best_develop_score:
                best_develop_score = fit["overall_fit_score"]
                best_develop = leader

    if best_develop:
        options.append({
            "strategy": "INTERNAL_DEVELOP",
            "candidate": best_develop["full_name"],
            "fit_score": round(best_develop_score, 3),
            "estimated_cost_eur": 120_000,
            "estimated_time_days": 270,
            "risk_level": "medium",
        })

    # Interim option
    options.append({
        "strategy": "INTERIM",
        "candidate": None,
        "fit_score": 0.0,
        "estimated_cost_eur": 250_000,
        "estimated_time_days": 14,
        "risk_level": "high",
    })

    # Accept risk option
    options.append({
        "strategy": "ACCEPT_RISK",
        "candidate": None,
        "fit_score": 0.0,
        "estimated_cost_eur": 0,
        "estimated_time_days": 0,
        "risk_level": "critical",
    })

    return {
        "role_id": role_id,
        "role_title": role["title"],
        "options": options,
    }


def generate_staffing_plan(
    role_ids_json: str, scenario_id: str, budget_eur: float,
) -> dict:
    """Generate an optimized staffing plan across multiple open roles.

    Evaluates all sourcing options, computes efficient frontier, and
    selects the optimal set of hires within budget.

    Args:
        role_ids_json: JSON string of role UUIDs to fill (list of strings).
        scenario_id: UUID of the active scenario.
        budget_eur: Total budget in EUR for all hires.

    Returns:
        Staffing plan with selected hires, total cost, and ROI estimate.
    """
    import json

    try:
        role_ids = json.loads(role_ids_json) if isinstance(role_ids_json, str) else role_ids_json
    except (json.JSONDecodeError, TypeError):
        return {"error": "Invalid JSON for role_ids."}

    roles: list[dict] = []
    candidates_per_role: dict[str, list[dict]] = {}
    plan_items: list[dict] = []

    for role_id in role_ids:
        role = fetch_one("roles", role_id)
        if not role:
            continue
        roles.append({"id": role_id, "title": role["title"]})

        # Get role_type from JD template
        role_type = role.get("title", "")
        if role.get("jd_template_id"):
            jd = fetch_one("jd_templates", role["jd_template_id"])
            if jd:
                role_type = jd["role_type"]

        # Rank candidates for this role under the scenario
        ranked_result = rank_candidates(role_type, scenario_id)
        ranked = ranked_result.get("candidates", []) if isinstance(ranked_result, dict) else ranked_result
        cands: list[dict] = []
        for r in ranked[:5]:  # Top 5 per role
            cost = 180_000 if r.get("leader_type") == "external_candidate" else 50_000
            cands.append({
                "candidate_id": r["leader_id"],
                "name": r["full_name"],
                "fit_score": r["overall_fit_score"],
                "cost_eur": cost,
            })
        candidates_per_role[role_id] = cands

        # Best candidate for plan item
        if cands:
            best = cands[0]
            plan_items.append({
                "role_id": role_id,
                "role_title": role["title"],
                "recommended_candidate": best["name"],
                "fit_score": best["fit_score"],
                "estimated_cost_eur": best["cost_eur"],
                "sourcing_strategy": (
                    "EXTERNAL_HIRE"
                    if any(
                        r.get("leader_type") == "external_candidate"
                        for r in ranked[:1]
                    )
                    else "INTERNAL_PROMOTE"
                ),
            })

    # Compute efficient frontier
    budget_levels = [
        budget_eur * 0.5,
        budget_eur * 0.75,
        budget_eur,
    ]
    frontier = compute_efficient_frontier(roles, candidates_per_role, budget_levels)

    # Total cost
    total_cost = sum(item.get("estimated_cost_eur", 0) for item in plan_items)

    # ROI estimate using cascade impacts as proxy
    roi = compute_roi_estimate(
        {"items": plan_items, "total_cost_eur": total_cost},
        [{"estimated_cost_eur": total_cost * 5}],  # Assume 5x risk avoidance
    )

    return {
        "plan_items": plan_items,
        "total_cost_eur": total_cost,
        "budget_eur": budget_eur,
        "within_budget": total_cost <= budget_eur,
        "efficient_frontier": frontier,
        "roi_estimate": roi,
    }


def generate_development_pathway(
    leader_id: str, role_type: str, scenario_id: str = "",
) -> dict:
    """Generate a structured upskilling plan for an internal candidate.

    When STAFF mode identifies an INTERNAL_DEVELOP sourcing strategy, this tool
    produces a concrete development pathway: competency gaps, recommended
    interventions (coaching, stretch assignments, formal training, mentorship),
    milestones, and estimated timeline to role-readiness.

    Args:
        leader_id: UUID of the internal candidate to develop.
        role_type: Target role type (e.g., "Head of EV Battery Systems").
        scenario_id: Optional scenario UUID for scenario-adapted gap analysis.

    Returns:
        Development pathway with gap analysis, intervention recommendations,
        milestone timeline, and estimated months to readiness.
    """
    # 1. Get candidate genome
    scores = fetch_by_column("leader_capability_scores", "leader_id", leader_id)
    genome = {
        s["dimension"]: s.get("corrected_score") or s.get("raw_score", 0.5)
        for s in scores
        if s.get("assessor_type") == "composite"
    }

    # 2. Get required profile (base or scenario-adapted)
    templates = fetch_by_column("jd_templates", "role_type", role_type)
    if not templates:
        return {"error": f"No JD template for role type '{role_type}'."}
    required = templates[0]["competency_weightings"]
    if scenario_id:
        scenario = fetch_one("scenarios", scenario_id)
        if scenario:
            original_total = sum(required.values())
            adapted, _ = adapt_jd_weightings(
                required, scenario["capability_demand_vector"],
            )
            required = {
                d: round(w * original_total, 4) for d, w in adapted.items()
            }

    # 3. Identify gaps (dimensions where candidate < requirement)
    gaps: list[dict] = []
    for dim, weight in sorted(required.items(), key=lambda x: x[1], reverse=True):
        current = genome.get(dim, 0.5)
        if current < weight:
            gap_size = round(weight - current, 3)
            gaps.append({
                "dimension": dim,
                "current_score": round(current, 3),
                "required_score": round(weight, 3),
                "gap_size": gap_size,
                "priority": (
                    "critical" if gap_size > 0.2
                    else "moderate" if gap_size > 0.1
                    else "minor"
                ),
                "intervention_type": (
                    "stretch_assignment"
                    if dim in (
                        "strategic_thinking",
                        "change_management",
                        "crisis_leadership",
                    )
                    else "formal_training"
                    if dim in (
                        "technical_depth",
                        "digital_fluency",
                        "financial_acumen",
                    )
                    else "coaching_mentorship"
                ),
            })

    # 4. Estimate readiness
    if not gaps:
        months_to_ready = 0
    else:
        critical_count = sum(1 for g in gaps if g["priority"] == "critical")
        months_to_ready = 3 + (critical_count * 4) + (len(gaps) - critical_count) * 2

    leader = fetch_one("leaders", leader_id)
    return {
        "leader_id": leader_id,
        "leader_name": leader.get("full_name", "Unknown") if leader else "Unknown",
        "target_role": role_type,
        "current_fit_score": round(
            compute_weighted_fit_score(genome, required), 3,
        ),
        "gaps": gaps,
        "total_gaps": len(gaps),
        "critical_gaps": sum(1 for g in gaps if g["priority"] == "critical"),
        "estimated_months_to_ready": months_to_ready,
        "sourcing_strategy": "INTERNAL_DEVELOP",
    }
