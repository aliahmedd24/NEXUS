"""Scenario API routes."""

from fastapi import APIRouter

from src.tools.diagnose_tools import get_scenario_library
from src.tools.orchestrator_tools import suggest_scenarios as _suggest_scenarios

router = APIRouter(prefix="/api/scenarios", tags=["scenarios"])


@router.get("")
async def list_scenarios():
    """List all available stress-test scenarios."""
    return get_scenario_library()


@router.get("/suggest")
async def suggest_scenarios(context: str = ""):
    """Suggest the most relevant scenarios based on industry context.

    If context is provided (e.g., "EU battery regulations tightening"),
    the scenarios are returned with context for adjusted reasoning.
    Without context, returns scenarios ranked by base probability.
    """
    return _suggest_scenarios(industry_context=context)
