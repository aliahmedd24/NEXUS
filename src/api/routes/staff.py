"""STAFF mode API routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.tools.staff_tools import (
    compute_candidate_fit,
    compute_team_compatibility,
    generate_development_pathway,
    generate_staffing_plan,
    get_candidate_pool,
    get_leader_genome,
    rank_candidates,
)

router = APIRouter(prefix="/api/staff", tags=["staff"])


class StaffRunRequest(BaseModel):
    """Request body for running the STAFF pipeline."""

    role_type: str
    scenario_id: str = ""
    org_unit_id: str = ""


class StaffPlanRequest(BaseModel):
    """Request body for generating a staffing plan."""

    role_ids: list[str]
    scenario_id: str
    budget_eur: float


@router.post("/run")
async def run_staff(request: StaffRunRequest):
    """Run STAFF analysis: rank candidates + chemistry + fit scores.

    Returns ranked candidates with fit scores, and team chemistry
    if org_unit_id is provided.
    """
    ranked_result = rank_candidates(request.role_type, request.scenario_id)
    ranking = ranked_result.get("candidates", []) if isinstance(ranked_result, dict) else ranked_result

    chemistry = None
    if request.org_unit_id and ranking:
        top_candidate_id = ranking[0].get("leader_id", "")
        if top_candidate_id:
            chemistry = compute_team_compatibility(
                top_candidate_id, request.org_unit_id,
            )

    return {
        "role_type": request.role_type,
        "scenario_id": request.scenario_id,
        "ranking": ranking,
        "chemistry": chemistry,
    }


@router.get("/candidates")
async def list_candidates(
    role_type: str = "",
    include_internal: bool = True,
    include_external: bool = True,
):
    """List candidate pool, optionally filtered by type."""
    return get_candidate_pool(role_type, include_internal, include_external)


@router.get("/genome/{leader_id}")
async def get_genome(leader_id: str):
    """Get the full 12-dimension leadership genome for a leader."""
    return get_leader_genome(leader_id)


@router.get("/fit/{leader_id}")
async def get_fit(leader_id: str, role_type: str, scenario_id: str = ""):
    """Compute candidate fit score for a specific role."""
    return compute_candidate_fit(leader_id, role_type, scenario_id)


@router.post("/chemistry")
async def get_chemistry(candidate_id: str, org_unit_id: str):
    """Compute team compatibility for a candidate in an org unit."""
    return compute_team_compatibility(candidate_id, org_unit_id)


@router.post("/plan")
async def create_staffing_plan(request: StaffPlanRequest):
    """Generate an optimized staffing plan across multiple roles."""
    import json

    return generate_staffing_plan(
        json.dumps(request.role_ids),
        request.scenario_id,
        request.budget_eur,
    )


@router.get("/develop/{leader_id}")
async def get_development_pathway(
    leader_id: str, role_type: str, scenario_id: str = "",
):
    """Generate a development pathway for an internal candidate.

    Returns competency gaps, recommended interventions, milestones,
    and estimated months to role-readiness.
    """
    return generate_development_pathway(leader_id, role_type, scenario_id)
