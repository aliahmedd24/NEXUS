"""What-If analysis API routes.

Chains DIAGNOSE -> STAFF -> Brief in a single call for natural-language
hypothetical questions.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from src.tools.diagnose_tools import (
    compute_cascade_impact,
    get_scenario_by_name,
    scan_vulnerabilities,
)
from src.tools.staff_tools import rank_candidates

router = APIRouter(prefix="/api", tags=["what-if"])


class WhatIfRequest(BaseModel):
    """Request body for a what-if analysis."""

    question: str
    scenario_id: str | None = None
    scenario_name: str | None = None
    role_type: str | None = None


@router.post("/what-if")
async def run_what_if(request: WhatIfRequest):
    """Run a what-if analysis chaining DIAGNOSE -> STAFF.

    Accepts a natural-language question and optional scenario/role hints.
    Runs vulnerability scan, cascade analysis, and candidate ranking
    in a single call.

    For the hackathon demo, this enables judges to ask free-form questions
    and see the full NEXUS pipeline respond in one shot.
    """
    # Resolve scenario
    scenario_id = request.scenario_id
    scenario_data: dict = {}
    if not scenario_id and request.scenario_name:
        scenario_data = get_scenario_by_name(request.scenario_name)
        if "error" in scenario_data:
            return {"error": scenario_data["error"], "question": request.question}
        scenario_id = scenario_data["id"]
    elif scenario_id:
        from src.supabase_client import fetch_one

        scenario_data = fetch_one("scenarios", scenario_id) or {}

    if not scenario_id:
        return {
            "error": (
                "Provide scenario_id or scenario_name to run what-if analysis. "
                "Use GET /api/scenarios/suggest to find relevant scenarios."
            ),
            "question": request.question,
        }

    # Run vulnerability scan
    vuln = scan_vulnerabilities(scenario_id)

    # Compute cascades for RED cells
    cascades = []
    for cell in vuln.get("heatmap", []):
        if cell["status"] == "red":
            cascade = compute_cascade_impact(cell["role_id"], scenario_id)
            cascades.append(cascade)

    # Rank candidates for specified role or first RED/vacant role
    staffing = None
    role_type = request.role_type
    if not role_type:
        # Auto-detect from RED cells
        for cell in vuln.get("heatmap", []):
            if cell["status"] == "red" and not cell.get("leader_name"):
                # Vacant role — get role_type from JD template
                from src.supabase_client import fetch_one

                role = fetch_one("roles", cell["role_id"])
                if role and role.get("jd_template_id"):
                    jd = fetch_one("jd_templates", role["jd_template_id"])
                    if jd:
                        role_type = jd["role_type"]
                        break

    if role_type:
        ranked_result = rank_candidates(role_type, scenario_id)
        ranking = ranked_result.get("candidates", []) if isinstance(ranked_result, dict) else ranked_result
        staffing = {
            "role_type": role_type,
            "top_candidates": ranking[:5],
        }

    return {
        "question": request.question,
        "scenario_used": {
            "id": scenario_id,
            "name": scenario_data.get("name", "Unknown"),
        },
        "vulnerability_impact": vuln,
        "cascade_analysis": cascades,
        "staffing_recommendation": staffing,
    }
