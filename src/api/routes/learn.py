"""LEARN mode API routes."""

import json

from fastapi import APIRouter

from src.tools.learn_tools import (
    detect_bias_patterns,
    get_calibration_coefficients,
    get_decision_outcomes,
    get_historical_decisions,
    reconstruct_decision,
    simulate_counterfactual,
    update_calibration_from_biases,
)

router = APIRouter(prefix="/api/learn", tags=["learn"])


@router.get("/decisions")
async def list_decisions(limit: int = 10):
    """List historical hiring decisions with outcomes."""
    return get_historical_decisions(limit)


@router.get("/replay/{decision_id}")
async def replay_decision(decision_id: str):
    """Fully reconstruct a past hiring decision with all context."""
    return reconstruct_decision(decision_id)


@router.get("/outcomes/{decision_id}")
async def get_outcomes(decision_id: str):
    """Get actual outcomes for a historical hire."""
    return get_decision_outcomes(decision_id)


@router.post("/counterfactual")
async def run_counterfactual(decision_id: str, alternative_candidate_id: str):
    """Simulate what would have happened with a different candidate."""
    return simulate_counterfactual(decision_id, alternative_candidate_id)


@router.get("/biases")
async def get_biases():
    """Get detected bias patterns from historical decisions."""
    return detect_bias_patterns()


@router.get("/calibration")
async def get_calibration():
    """Get current calibration coefficients."""
    return get_calibration_coefficients()


@router.post("/run")
async def run_learn():
    """Run full LEARN pipeline: detect biases and update calibration.

    This executes the feedback loop: analyze past decisions -> detect
    biases -> write calibration coefficients -> STAFF mode benefits.
    """
    biases = detect_bias_patterns()
    result = update_calibration_from_biases(json.dumps(biases))
    return {
        "biases": biases,
        "calibration": result,
    }
