"""DIAGNOSE mode API routes."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.tools.diagnose_tools import (
    compute_cascade_impact,
    create_compound_scenario,
    get_scenario_by_name,
    scan_vulnerabilities,
)

router = APIRouter(prefix="/api/diagnose", tags=["diagnose"])


class DiagnoseRequest(BaseModel):
    """Request body for running a DIAGNOSE scan."""

    scenario_id: str | None = None
    scenario_name: str | None = None


class CompoundRequest(BaseModel):
    """Request body for creating a compound scenario."""

    scenario_a_name: str
    scenario_b_name: str


@router.post("/run")
async def run_diagnose(request: DiagnoseRequest):
    """Run vulnerability scan + cascade analysis for a scenario.

    Accepts either scenario_id or scenario_name. For each RED cell in
    the heatmap, auto-computes cascade impact.
    """
    scenario_id = request.scenario_id
    if not scenario_id and request.scenario_name:
        scenario = get_scenario_by_name(request.scenario_name)
        if "error" in scenario:
            return scenario
        scenario_id = scenario["id"]

    if not scenario_id:
        return {"error": "Provide scenario_id or scenario_name."}

    vuln = scan_vulnerabilities(scenario_id)
    if "error" in vuln:
        return vuln

    # Auto-compute cascades for RED cells
    cascades = []
    for cell in vuln.get("heatmap", []):
        if cell["status"] == "red":
            cascade = compute_cascade_impact(cell["role_id"], scenario_id)
            cascades.append(cascade)

    vuln["cascades"] = cascades
    return vuln


@router.post("/compound")
async def create_compound(request: CompoundRequest):
    """Create a compound scenario combining two simultaneous crises."""
    return create_compound_scenario(
        request.scenario_a_name, request.scenario_b_name,
    )


@router.get("/cascade/{role_id}")
async def get_cascade(role_id: str, scenario_id: str):
    """Get cascade impact for a specific role under a scenario."""
    return compute_cascade_impact(role_id, scenario_id)
