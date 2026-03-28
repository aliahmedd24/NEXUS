"""Tools for the NEXUS Orchestrator agent.

Provides scenario suggestion and session management utilities.
"""

from src.supabase_client import fetch_all


def suggest_scenarios(industry_context: str = "") -> dict:
    """Suggest which scenarios are most relevant based on industry context.

    Retrieves all scenarios from Supabase, then ranks them by probability.
    If industry_context is provided, the LLM agent uses it to adjust
    relevance narrative (e.g., "EU battery regulation changes" increases
    Battery Supplier Default relevance).

    This tool provides the raw scenario data for the agent to reason over.

    Args:
        industry_context: Optional free-text description of current industry
            conditions (e.g., "semiconductor shortage worsening", "new EU
            emissions regulation announced"). If empty, returns scenarios
            ranked by base probability.

    Returns:
        Ranked list of scenarios with name, probability, affected org units,
        and capability demands for the agent to reason about.
    """
    scenarios = fetch_all("scenarios")
    ranked = sorted(
        scenarios, key=lambda s: s.get("probability", 0), reverse=True,
    )

    return {
        "scenarios": [
            {
                "id": s["id"],
                "name": s["name"],
                "description": s.get("narrative", ""),
                "probability": s.get("probability", 0),
                "affected_org_units": s.get("affected_org_units", []),
                "capability_demands": s.get("capability_demand_vector", {}),
            }
            for s in ranked
        ],
        "industry_context_provided": bool(industry_context),
        "industry_context": industry_context,
        "note": (
            "Agent should adjust probability assessments based on "
            "industry_context if provided."
        ),
    }
