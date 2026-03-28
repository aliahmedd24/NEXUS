"""Seed historical hiring decisions with planted biases.

Populates 8 past leadership hiring decisions and their tracked outcomes
for NEXUS bias-detection analysis:
- 3 decisions where industry tenure was overweighted (+35% bias)
- 2 decisions where change management was underweighted (-28% bias)
- 2 decisions where the scenario that emerged differed from the one at decision time
- 1 genuinely good decision for contrast
"""

import logging

from db.seed._ids import (
    EC2_OKONKWO,
    EC3_NAKAMURA,
    EC5_GUPTA,
    EC6_MUELLER,
    EC9_WILLIAMS,
    HD1,
    HD2,
    HD3,
    HD4,
    HD5,
    HD6,
    HD7,
    HD8,
    IC2_HOFFMANN,
    IC4_KOWALSKI,
    IC5_SCHMIDT,
    L1_RICHTER,
    L2_STAHL,
    L3_BRENNER,
    L4_TANAKA,
    L5_GRUBER,
    L6_MITCHELL,
    L7_PATEL,
    L8_SANTOS,
    ROLE_CTO,
    ROLE_DIR_DINGOLFING,
    ROLE_DIR_MUNICH,
    ROLE_DIR_SPARTANBURG,
    ROLE_SVP_MFG,
    ROLE_VP_IT,
    ROLE_VP_QUALITY,
    ROLE_VP_SUPPLY,
)
from src.supabase_client import fetch_all, upsert

logger = logging.getLogger(__name__)


# ── Outcome UUID helper ────────────────────────────────────────────────────


def _outcome_id(decision_index: int, outcome_index: int) -> str:
    """Generate a fixed UUID for a decision outcome.

    Args:
        decision_index: Decision number (1-8).
        outcome_index: Outcome number within that decision (1-3).

    Returns:
        Fixed UUID string following the pattern
        81000000-0000-4000-a000-00HHOOOOOOOO.
    """
    return f"81000000-0000-4000-a000-00{decision_index:02d}{outcome_index:08d}"


# ── Historical Decisions ───────────────────────────────────────────────────

HISTORICAL_DECISIONS = [
    # HD1 — Plant Director Dingolfing (BIAS: tenure overweighted)
    {
        "id": HD1,
        "role_id": ROLE_DIR_DINGOLFING,
        "decision_date": "2024-03-15",
        "scenario_at_decision": "Steady state production optimization",
        "selected_candidate_id": L5_GRUBER,
        "runner_up_candidate_id": IC2_HOFFMANN,
        "decision_criteria_used": {
            "industry_tenure": 0.40,
            "operational_execution": 0.25,
            "cultural_fit": 0.20,
            "technical_depth": 0.15,
        },
        "decision_reasoning": (
            "Hans's unmatched tenure and deep institutional knowledge "
            "make him the safe choice for Dingolfing."
        ),
        "time_to_fill_days": 45,
        "cost_of_hire_eur": 15000,
    },
    # HD2 — VP Supply Chain (BIAS: tenure overweighted)
    {
        "id": HD2,
        "role_id": ROLE_VP_SUPPLY,
        "decision_date": "2023-06-01",
        "scenario_at_decision": "Post-COVID supply chain stabilization",
        "selected_candidate_id": L3_BRENNER,
        "runner_up_candidate_id": IC4_KOWALSKI,
        "decision_criteria_used": {
            "industry_tenure": 0.35,
            "operational_execution": 0.30,
            "stakeholder_relationships": 0.20,
            "risk_management": 0.15,
        },
        "decision_reasoning": (
            "Thomas's 15 years at BMW and established supplier "
            "relationships are critical for recovery."
        ),
        "time_to_fill_days": 60,
        "cost_of_hire_eur": 20000,
    },
    # HD3 — Plant Director Munich (BIAS: change_management underweighted)
    {
        "id": HD3,
        "role_id": ROLE_DIR_MUNICH,
        "decision_date": "2024-01-10",
        "scenario_at_decision": "Munich production efficiency upgrade",
        "selected_candidate_id": L4_TANAKA,
        "runner_up_candidate_id": EC2_OKONKWO,
        "decision_criteria_used": {
            "technical_depth": 0.40,
            "operational_execution": 0.30,
            "industry_knowledge": 0.20,
            "change_management": 0.10,
        },
        "decision_reasoning": (
            "Dr. Tanaka's technical excellence and precision-focus "
            "are ideal for the efficiency program."
        ),
        "time_to_fill_days": 90,
        "cost_of_hire_eur": 35000,
    },
    # HD4 — VP IT & Digital (BIAS: tenure overweighted by NOT selecting
    #        Patel initially, then reversing)
    {
        "id": HD4,
        "role_id": ROLE_VP_IT,
        "decision_date": "2025-01-20",
        "scenario_at_decision": "iFACTORY digital infrastructure rollout",
        "selected_candidate_id": L7_PATEL,
        "runner_up_candidate_id": EC5_GUPTA,
        "decision_criteria_used": {
            "technical_depth": 0.35,
            "innovation_orientation": 0.30,
            "change_management": 0.20,
            "cultural_fit": 0.15,
        },
        "decision_reasoning": (
            "Raj's Silicon Valley experience and deep tech expertise "
            "are essential for the iFACTORY vision."
        ),
        "time_to_fill_days": 120,
        "cost_of_hire_eur": 85000,
    },
    # HD5 — SVP Manufacturing (GOOD decision)
    {
        "id": HD5,
        "role_id": ROLE_SVP_MFG,
        "decision_date": "2022-09-01",
        "scenario_at_decision": "Post-pandemic manufacturing recovery",
        "selected_candidate_id": L2_STAHL,
        "runner_up_candidate_id": EC6_MUELLER,
        "decision_criteria_used": {
            "operational_execution": 0.30,
            "crisis_leadership": 0.25,
            "people_development": 0.25,
            "stakeholder_management": 0.20,
        },
        "decision_reasoning": (
            "Petra's operational track record and crisis management "
            "during COVID make her the clear choice."
        ),
        "time_to_fill_days": 75,
        "cost_of_hire_eur": 25000,
    },
    # HD6 — Plant Director Spartanburg (BIAS: change_management underweighted)
    {
        "id": HD6,
        "role_id": ROLE_DIR_SPARTANBURG,
        "decision_date": "2024-09-01",
        "scenario_at_decision": "Spartanburg X model production expansion",
        "selected_candidate_id": L6_MITCHELL,
        "runner_up_candidate_id": EC3_NAKAMURA,
        "decision_criteria_used": {
            "people_development": 0.30,
            "innovation_orientation": 0.25,
            "operational_execution": 0.25,
            "change_management": 0.08,
            "cultural_sensitivity": 0.12,
        },
        "decision_reasoning": (
            "Sarah brings fresh energy and strong people skills "
            "needed for the expansion."
        ),
        "time_to_fill_days": 80,
        "cost_of_hire_eur": 45000,
    },
    # HD7 — CTO (BIAS: scenario mismatch)
    {
        "id": HD7,
        "role_id": ROLE_CTO,
        "decision_date": "2021-06-01",
        "scenario_at_decision": "EV technology strategy development",
        "selected_candidate_id": L1_RICHTER,
        "runner_up_candidate_id": EC9_WILLIAMS,
        "decision_criteria_used": {
            "strategic_thinking": 0.40,
            "technical_depth": 0.30,
            "innovation_orientation": 0.20,
            "stakeholder_management": 0.10,
        },
        "decision_reasoning": (
            "Dr. Richter's strategic vision and technical credibility "
            "are essential to lead the EV transition."
        ),
        "time_to_fill_days": 150,
        "cost_of_hire_eur": 120000,
    },
    # HD8 — VP Quality (mixed result)
    {
        "id": HD8,
        "role_id": ROLE_VP_QUALITY,
        "decision_date": "2023-09-15",
        "scenario_at_decision": "Quality system modernization",
        "selected_candidate_id": L8_SANTOS,
        "runner_up_candidate_id": IC5_SCHMIDT,
        "decision_criteria_used": {
            "operational_execution": 0.30,
            "risk_calibration": 0.30,
            "technical_depth": 0.25,
            "change_management": 0.15,
        },
        "decision_reasoning": (
            "Maria's methodical approach and risk awareness are "
            "critical for quality system integrity."
        ),
        "time_to_fill_days": 65,
        "cost_of_hire_eur": 18000,
    },
]


# ── Decision Outcomes ──────────────────────────────────────────────────────

DECISION_OUTCOMES = [
    # HD1 outcomes — 6mo and 12mo
    {
        "id": _outcome_id(1, 1),
        "decision_id": HD1,
        "months_elapsed": 6,
        "performance_rating": 7.5,
        "goal_completion_pct": 72,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(1, 2),
        "decision_id": HD1,
        "months_elapsed": 12,
        "performance_rating": 7.2,
        "goal_completion_pct": 68,
        "team_engagement_delta": -0.05,
        "team_attrition_delta": 0.03,
        "still_in_role": True,
    },
    # HD2 outcomes — 6mo, 12mo, 24mo
    {
        "id": _outcome_id(2, 1),
        "decision_id": HD2,
        "months_elapsed": 6,
        "performance_rating": 7.8,
        "goal_completion_pct": 75,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(2, 2),
        "decision_id": HD2,
        "months_elapsed": 12,
        "performance_rating": 7.4,
        "goal_completion_pct": 70,
        "team_engagement_delta": -0.08,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(2, 3),
        "decision_id": HD2,
        "months_elapsed": 24,
        "performance_rating": 7.0,
        "goal_completion_pct": 65,
        "team_engagement_delta": -0.12,
        "team_attrition_delta": 0.06,
        "still_in_role": True,
    },
    # HD3 outcomes — 6mo and 12mo (struggled when transformation replaced efficiency)
    {
        "id": _outcome_id(3, 1),
        "decision_id": HD3,
        "months_elapsed": 6,
        "performance_rating": 7.8,
        "goal_completion_pct": 80,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(3, 2),
        "decision_id": HD3,
        "months_elapsed": 12,
        "performance_rating": 7.2,
        "goal_completion_pct": 65,
        "team_engagement_delta": -0.10,
        "still_in_role": True,
    },
    # HD4 outcomes — 6mo and 12mo (cultural friction emerging)
    {
        "id": _outcome_id(4, 1),
        "decision_id": HD4,
        "months_elapsed": 6,
        "performance_rating": 7.5,
        "goal_completion_pct": 78,
        "team_engagement_delta": -0.15,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(4, 2),
        "decision_id": HD4,
        "months_elapsed": 12,
        "performance_rating": 7.0,
        "goal_completion_pct": 72,
        "team_engagement_delta": -0.20,
        "still_in_role": True,
    },
    # HD5 outcomes — 12mo and 24mo (genuinely good)
    {
        "id": _outcome_id(5, 1),
        "decision_id": HD5,
        "months_elapsed": 12,
        "performance_rating": 8.2,
        "goal_completion_pct": 88,
        "team_engagement_delta": 0.05,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(5, 2),
        "decision_id": HD5,
        "months_elapsed": 24,
        "performance_rating": 8.0,
        "goal_completion_pct": 85,
        "team_engagement_delta": 0.08,
        "team_attrition_delta": -0.02,
        "still_in_role": True,
    },
    # HD6 outcomes — 6mo
    {
        "id": _outcome_id(6, 1),
        "decision_id": HD6,
        "months_elapsed": 6,
        "performance_rating": 7.8,
        "goal_completion_pct": 82,
        "team_engagement_delta": 0.10,
        "still_in_role": True,
    },
    # HD7 outcomes — 12mo and 24mo (struggling with execution demands)
    {
        "id": _outcome_id(7, 1),
        "decision_id": HD7,
        "months_elapsed": 12,
        "performance_rating": 8.0,
        "goal_completion_pct": 82,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(7, 2),
        "decision_id": HD7,
        "months_elapsed": 24,
        "performance_rating": 7.5,
        "goal_completion_pct": 70,
        "team_engagement_delta": -0.05,
        "still_in_role": True,
    },
    # HD8 outcomes — 6mo, 12mo, 24mo (struggling with innovation side)
    {
        "id": _outcome_id(8, 1),
        "decision_id": HD8,
        "months_elapsed": 6,
        "performance_rating": 7.8,
        "goal_completion_pct": 80,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(8, 2),
        "decision_id": HD8,
        "months_elapsed": 12,
        "performance_rating": 7.5,
        "goal_completion_pct": 75,
        "still_in_role": True,
    },
    {
        "id": _outcome_id(8, 3),
        "decision_id": HD8,
        "months_elapsed": 24,
        "performance_rating": 7.2,
        "goal_completion_pct": 68,
        "still_in_role": True,
    },
]


# ── Seed Function ──────────────────────────────────────────────────────────


def seed_historical_decisions() -> None:
    """Seed 8 historical hiring decisions with planted biases and outcomes.

    Populates the ``historical_decisions`` and ``decision_outcomes`` tables
    with synthetic data designed to test NEXUS bias-detection capabilities:

    - HD1, HD2, HD4: industry tenure overweighted (+35% bias).
    - HD3, HD6: change management underweighted (-28% bias).
    - HD3, HD7: scenario at decision differed from actual emerging scenario.
    - HD5: genuinely good decision for contrast.
    - HD6, HD8: mixed results.

    Uses fixed UUIDs from ``_ids.py`` for decisions and a deterministic
    UUID scheme for outcomes, ensuring full idempotency via upsert.
    """
    # Seed decisions
    existing_decisions = fetch_all("historical_decisions")
    if len(existing_decisions) >= len(HISTORICAL_DECISIONS):
        logger.info(
            "Historical decisions already seeded (%d rows), skipping.",
            len(existing_decisions),
        )
    else:
        upsert("historical_decisions", HISTORICAL_DECISIONS)
        logger.info(
            "Seeded %d historical decisions.", len(HISTORICAL_DECISIONS)
        )

    # Seed outcomes
    existing_outcomes = fetch_all("decision_outcomes")
    if len(existing_outcomes) >= len(DECISION_OUTCOMES):
        logger.info(
            "Decision outcomes already seeded (%d rows), skipping.",
            len(existing_outcomes),
        )
    else:
        upsert("decision_outcomes", DECISION_OUTCOMES)
        logger.info("Seeded %d decision outcomes.", len(DECISION_OUTCOMES))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_historical_decisions()
