"""Seed script for candidate leaders and their capability scores.

Populates the ``leaders`` table with 5 internal candidates (BMW employees
considered for promotion) and 10 external candidates (from other automotive
and tech companies).  Each candidate also receives 12 rows in the
``leader_capability_scores`` table covering all NEXUS competency dimensions.
"""

import logging

from db.seed._ids import (
    DIMENSION_KEYS,
    DIM_CHANGE,
    DIM_CRISIS,
    DIM_CROSSFUNC,
    DIM_CULTURAL,
    DIM_INNOVATION,
    DIM_OPERATIONAL,
    DIM_PEOPLE,
    DIM_RESILIENCE,
    DIM_RISK,
    DIM_STAKEHOLDER,
    DIM_STRATEGIC,
    DIM_TECHNICAL,
    EC1_ZHOU,
    EC2_OKONKWO,
    EC3_NAKAMURA,
    EC4_JOHANSSON,
    EC5_GUPTA,
    EC6_MUELLER,
    EC7_PARK,
    EC8_SILVA,
    EC9_WILLIAMS,
    EC10_CHEN,
    IC1_WEBER,
    IC2_HOFFMANN,
    IC3_MEYER,
    IC4_KOWALSKI,
    IC5_SCHMIDT,
)
from src.supabase_client import fetch_all, upsert

logger = logging.getLogger(__name__)

# ── Dimension-key to UUID mapping ──────────────────────────────────────────

_DIM_ID_MAP: dict[str, str] = {
    "strategic_thinking": DIM_STRATEGIC,
    "operational_execution": DIM_OPERATIONAL,
    "change_management": DIM_CHANGE,
    "crisis_leadership": DIM_CRISIS,
    "people_development": DIM_PEOPLE,
    "technical_depth": DIM_TECHNICAL,
    "cross_functional_collab": DIM_CROSSFUNC,
    "innovation_orientation": DIM_INNOVATION,
    "cultural_sensitivity": DIM_CULTURAL,
    "risk_calibration": DIM_RISK,
    "stakeholder_management": DIM_STAKEHOLDER,
    "resilience_adaptability": DIM_RESILIENCE,
}

# ── Internal Candidates (5) ───────────────────────────────────────────────

INTERNAL_CANDIDATES: list[dict] = [
    {
        "id": IC1_WEBER,
        "full_name": "Anna Weber",
        "leader_type": "internal_candidate",
        "years_experience": 14,
        "years_at_bmw": 14,
        "education_level": "masters",
        "education_field": "Electrical Engineering",
        "location_current": "Munich",
        "flight_risk": 0.20,
    },
    {
        "id": IC2_HOFFMANN,
        "full_name": "Markus Hoffmann",
        "leader_type": "internal_candidate",
        "years_experience": 16,
        "years_at_bmw": 16,
        "education_level": "masters",
        "education_field": "Mechanical Engineering",
        "location_current": "Dingolfing",
        "flight_risk": 0.10,
    },
    {
        "id": IC3_MEYER,
        "full_name": "Lisa Meyer",
        "leader_type": "internal_candidate",
        "years_experience": 11,
        "years_at_bmw": 8,
        "education_level": "mba",
        "education_field": "Business + Engineering dual",
        "location_current": "Munich",
        "flight_risk": 0.30,
    },
    {
        "id": IC4_KOWALSKI,
        "full_name": "Tomasz Kowalski",
        "leader_type": "internal_candidate",
        "years_experience": 13,
        "years_at_bmw": 6,
        "education_level": "masters",
        "education_field": "Supply Chain Management",
        "location_current": "Munich",
        "flight_risk": 0.25,
    },
    {
        "id": IC5_SCHMIDT,
        "full_name": "Claudia Schmidt",
        "leader_type": "internal_candidate",
        "years_experience": 15,
        "years_at_bmw": 15,
        "education_level": "masters",
        "education_field": "Quality Engineering",
        "location_current": "Munich",
        "flight_risk": 0.10,
    },
]

# ── External Candidates (10) ──────────────────────────────────────────────

EXTERNAL_CANDIDATES: list[dict] = [
    {
        "id": EC1_ZHOU,
        "full_name": "Dr. Wei Zhou",
        "leader_type": "external_candidate",
        "years_experience": 18,
        "years_at_bmw": 0,
        "education_level": "phd",
        "education_field": "Battery Chemistry",
        "location_current": "Shanghai",
        "flight_risk": 0.15,
    },
    {
        "id": EC2_OKONKWO,
        "full_name": "Adaeze Okonkwo",
        "leader_type": "external_candidate",
        "years_experience": 15,
        "years_at_bmw": 0,
        "education_level": "mba",
        "education_field": "Operations Management",
        "location_current": "Detroit",
        "flight_risk": 0.20,
    },
    {
        "id": EC3_NAKAMURA,
        "full_name": "Kenji Nakamura",
        "leader_type": "external_candidate",
        "years_experience": 22,
        "years_at_bmw": 0,
        "education_level": "masters",
        "education_field": "Industrial Engineering",
        "location_current": "Tokyo",
        "flight_risk": 0.10,
    },
    {
        "id": EC4_JOHANSSON,
        "full_name": "Erik Johansson",
        "leader_type": "external_candidate",
        "years_experience": 16,
        "years_at_bmw": 0,
        "education_level": "masters",
        "education_field": "EV Powertrain Engineering",
        "location_current": "Gothenburg",
        "flight_risk": 0.25,
    },
    {
        "id": EC5_GUPTA,
        "full_name": "Priya Gupta",
        "leader_type": "external_candidate",
        "years_experience": 14,
        "years_at_bmw": 0,
        "education_level": "mba",
        "education_field": "Technology Management",
        "location_current": "Bangalore",
        "flight_risk": 0.20,
    },
    {
        "id": EC6_MUELLER,
        "full_name": "Friedrich Mueller",
        "leader_type": "external_candidate",
        "years_experience": 20,
        "years_at_bmw": 0,
        "education_level": "masters",
        "education_field": "Production Engineering",
        "location_current": "Stuttgart",
        "flight_risk": 0.15,
    },
    {
        "id": EC7_PARK,
        "full_name": "Jae-Won Park",
        "leader_type": "external_candidate",
        "years_experience": 13,
        "years_at_bmw": 0,
        "education_level": "phd",
        "education_field": "Computer Science",
        "location_current": "Seoul",
        "flight_risk": 0.30,
    },
    {
        "id": EC8_SILVA,
        "full_name": "Isabella Silva",
        "leader_type": "external_candidate",
        "years_experience": 17,
        "years_at_bmw": 0,
        "education_level": "masters",
        "education_field": "Supply Chain",
        "location_current": "Sao Paulo",
        "flight_risk": 0.20,
    },
    {
        "id": EC9_WILLIAMS,
        "full_name": "David Williams",
        "leader_type": "external_candidate",
        "years_experience": 19,
        "years_at_bmw": 0,
        "education_level": "mba",
        "education_field": "General Management",
        "location_current": "London",
        "flight_risk": 0.15,
    },
    {
        "id": EC10_CHEN,
        "full_name": "Dr. Mei Chen",
        "leader_type": "external_candidate",
        "years_experience": 16,
        "years_at_bmw": 0,
        "education_level": "phd",
        "education_field": "Materials Science",
        "location_current": "Munich",
        "flight_risk": 0.20,
    },
]

ALL_CANDIDATES: list[dict] = INTERNAL_CANDIDATES + EXTERNAL_CANDIDATES

# ── Capability Scores ─────────────────────────────────────────────────────
# Raw scores per candidate, keyed by dimension key (same order as DIMENSION_KEYS).

_RAW_SCORES: dict[str, dict[str, float]] = {
    IC1_WEBER: {
        "technical_depth": 0.88,
        "operational_execution": 0.78,
        "innovation_orientation": 0.82,
        "change_management": 0.72,
        "strategic_thinking": 0.68,
        "risk_calibration": 0.70,
        "people_development": 0.62,
        "crisis_leadership": 0.60,
        "stakeholder_management": 0.58,
        "cross_functional_collab": 0.65,
        "cultural_sensitivity": 0.70,
        "resilience_adaptability": 0.75,
    },
    IC2_HOFFMANN: {
        "operational_execution": 0.90,
        "technical_depth": 0.82,
        "crisis_leadership": 0.78,
        "people_development": 0.75,
        "cultural_sensitivity": 0.80,
        "resilience_adaptability": 0.78,
        "risk_calibration": 0.72,
        "stakeholder_management": 0.68,
        "strategic_thinking": 0.55,
        "change_management": 0.50,
        "innovation_orientation": 0.42,
        "cross_functional_collab": 0.60,
    },
    IC3_MEYER: {
        "change_management": 0.85,
        "innovation_orientation": 0.88,
        "cross_functional_collab": 0.82,
        "strategic_thinking": 0.78,
        "people_development": 0.72,
        "resilience_adaptability": 0.80,
        "technical_depth": 0.68,
        "risk_calibration": 0.65,
        "stakeholder_management": 0.62,
        "operational_execution": 0.58,
        "crisis_leadership": 0.55,
        "cultural_sensitivity": 0.60,
    },
    IC4_KOWALSKI: {
        "operational_execution": 0.82,
        "risk_calibration": 0.80,
        "stakeholder_management": 0.75,
        "technical_depth": 0.72,
        "cultural_sensitivity": 0.78,
        "cross_functional_collab": 0.70,
        "resilience_adaptability": 0.72,
        "strategic_thinking": 0.65,
        "crisis_leadership": 0.62,
        "change_management": 0.58,
        "people_development": 0.55,
        "innovation_orientation": 0.50,
    },
    IC5_SCHMIDT: {
        "operational_execution": 0.85,
        "risk_calibration": 0.88,
        "technical_depth": 0.80,
        "stakeholder_management": 0.72,
        "cultural_sensitivity": 0.75,
        "people_development": 0.70,
        "resilience_adaptability": 0.68,
        "crisis_leadership": 0.65,
        "strategic_thinking": 0.60,
        "cross_functional_collab": 0.58,
        "change_management": 0.52,
        "innovation_orientation": 0.45,
    },
    EC1_ZHOU: {
        "technical_depth": 0.95,
        "innovation_orientation": 0.88,
        "strategic_thinking": 0.80,
        "operational_execution": 0.75,
        "change_management": 0.70,
        "risk_calibration": 0.72,
        "resilience_adaptability": 0.78,
        "crisis_leadership": 0.65,
        "people_development": 0.60,
        "stakeholder_management": 0.55,
        "cross_functional_collab": 0.50,
        "cultural_sensitivity": 0.35,
    },
    EC2_OKONKWO: {
        "change_management": 0.90,
        "operational_execution": 0.85,
        "people_development": 0.80,
        "crisis_leadership": 0.78,
        "resilience_adaptability": 0.82,
        "cross_functional_collab": 0.75,
        "strategic_thinking": 0.72,
        "innovation_orientation": 0.70,
        "stakeholder_management": 0.65,
        "risk_calibration": 0.68,
        "technical_depth": 0.62,
        "cultural_sensitivity": 0.45,
    },
    EC3_NAKAMURA: {
        "operational_execution": 0.95,
        "technical_depth": 0.88,
        "risk_calibration": 0.85,
        "crisis_leadership": 0.80,
        "resilience_adaptability": 0.82,
        "people_development": 0.75,
        "cultural_sensitivity": 0.60,
        "stakeholder_management": 0.65,
        "strategic_thinking": 0.62,
        "change_management": 0.55,
        "innovation_orientation": 0.48,
        "cross_functional_collab": 0.58,
    },
    EC4_JOHANSSON: {
        "technical_depth": 0.90,
        "innovation_orientation": 0.85,
        "change_management": 0.80,
        "strategic_thinking": 0.75,
        "operational_execution": 0.72,
        "cross_functional_collab": 0.70,
        "risk_calibration": 0.68,
        "resilience_adaptability": 0.75,
        "people_development": 0.62,
        "stakeholder_management": 0.60,
        "crisis_leadership": 0.58,
        "cultural_sensitivity": 0.55,
    },
    EC5_GUPTA: {
        "innovation_orientation": 0.88,
        "change_management": 0.85,
        "technical_depth": 0.80,
        "strategic_thinking": 0.78,
        "cross_functional_collab": 0.75,
        "people_development": 0.72,
        "resilience_adaptability": 0.76,
        "operational_execution": 0.65,
        "risk_calibration": 0.62,
        "stakeholder_management": 0.60,
        "crisis_leadership": 0.55,
        "cultural_sensitivity": 0.50,
    },
    EC6_MUELLER: {
        "operational_execution": 0.92,
        "cultural_sensitivity": 0.90,
        "stakeholder_management": 0.85,
        "technical_depth": 0.82,
        "people_development": 0.78,
        "crisis_leadership": 0.75,
        "risk_calibration": 0.78,
        "resilience_adaptability": 0.72,
        "strategic_thinking": 0.65,
        "change_management": 0.55,
        "innovation_orientation": 0.45,
        "cross_functional_collab": 0.68,
    },
    EC7_PARK: {
        "technical_depth": 0.92,
        "innovation_orientation": 0.90,
        "strategic_thinking": 0.78,
        "change_management": 0.72,
        "operational_execution": 0.68,
        "risk_calibration": 0.65,
        "resilience_adaptability": 0.70,
        "cross_functional_collab": 0.55,
        "crisis_leadership": 0.58,
        "people_development": 0.52,
        "stakeholder_management": 0.48,
        "cultural_sensitivity": 0.40,
    },
    EC8_SILVA: {
        "operational_execution": 0.85,
        "stakeholder_management": 0.82,
        "risk_calibration": 0.80,
        "cross_functional_collab": 0.78,
        "cultural_sensitivity": 0.75,
        "resilience_adaptability": 0.78,
        "people_development": 0.72,
        "crisis_leadership": 0.70,
        "technical_depth": 0.65,
        "strategic_thinking": 0.62,
        "change_management": 0.58,
        "innovation_orientation": 0.52,
    },
    EC9_WILLIAMS: {
        "strategic_thinking": 0.85,
        "change_management": 0.82,
        "stakeholder_management": 0.80,
        "people_development": 0.78,
        "cross_functional_collab": 0.75,
        "resilience_adaptability": 0.80,
        "innovation_orientation": 0.72,
        "risk_calibration": 0.70,
        "operational_execution": 0.68,
        "cultural_sensitivity": 0.65,
        "crisis_leadership": 0.62,
        "technical_depth": 0.55,
    },
    EC10_CHEN: {
        "technical_depth": 0.92,
        "innovation_orientation": 0.85,
        "strategic_thinking": 0.78,
        "operational_execution": 0.72,
        "change_management": 0.68,
        "risk_calibration": 0.70,
        "resilience_adaptability": 0.72,
        "cross_functional_collab": 0.62,
        "people_development": 0.58,
        "crisis_leadership": 0.55,
        "stakeholder_management": 0.52,
        "cultural_sensitivity": 0.65,
    },
}

# ── Candidate index mapping for score UUID generation ─────────────────────
# IC candidates get indices 1001-1005, EC candidates get 2001-2010.

_CANDIDATE_INDEX: dict[str, int] = {
    IC1_WEBER: 1001,
    IC2_HOFFMANN: 1002,
    IC3_MEYER: 1003,
    IC4_KOWALSKI: 1004,
    IC5_SCHMIDT: 1005,
    EC1_ZHOU: 2001,
    EC2_OKONKWO: 2002,
    EC3_NAKAMURA: 2003,
    EC4_JOHANSSON: 2004,
    EC5_GUPTA: 2005,
    EC6_MUELLER: 2006,
    EC7_PARK: 2007,
    EC8_SILVA: 2008,
    EC9_WILLIAMS: 2009,
    EC10_CHEN: 2010,
}

# Dimension index: 1-based position in DIMENSION_KEYS list.
_DIMENSION_INDEX: dict[str, int] = {
    key: idx + 1 for idx, key in enumerate(DIMENSION_KEYS)
}


def _score_uuid(candidate_idx: int, dimension_idx: int) -> str:
    """Generate a deterministic UUID for a capability score row.

    Format: ``56000000-0000-4000-a000-CCCCDDDDDDDD`` where CCCC is the
    zero-padded candidate index and DDDDDDDD is the zero-padded dimension
    index.

    Args:
        candidate_idx: Candidate index (1001-1005 for IC, 2001-2010 for EC).
        dimension_idx: Dimension index (1-12).

    Returns:
        Deterministic UUID string.
    """
    return f"56000000-0000-4000-a000-{candidate_idx:04d}{dimension_idx:08d}"


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value to [lo, hi].

    Args:
        value: The value to clamp.
        lo: Lower bound (inclusive).
        hi: Upper bound (inclusive).

    Returns:
        Clamped value.
    """
    return max(lo, min(hi, value))


def _build_capability_scores() -> list[dict]:
    """Build all leader_capability_scores rows for every candidate.

    Each candidate gets 12 rows (one per competency dimension). The
    ``corrected_score`` equals the ``raw_score``, and confidence bounds
    are raw_score +/- 0.06 clamped to [0, 1].

    Returns:
        List of score row dicts ready for upsert.
    """
    rows: list[dict] = []
    for leader_id, scores in _RAW_SCORES.items():
        candidate_idx = _CANDIDATE_INDEX[leader_id]
        for dim_key, raw_score in scores.items():
            dimension_idx = _DIMENSION_INDEX[dim_key]
            rows.append(
                {
                    "id": _score_uuid(candidate_idx, dimension_idx),
                    "leader_id": leader_id,
                    "dimension": dim_key,
                    "raw_score": raw_score,
                    "corrected_score": raw_score,
                    "confidence_low": round(_clamp(raw_score - 0.06), 4),
                    "confidence_high": round(_clamp(raw_score + 0.06), 4),
                    "assessor_type": "composite",
                }
            )
    return rows


CAPABILITY_SCORES: list[dict] = _build_capability_scores()


def seed_candidates(dry_run: bool = False) -> None:
    """Seed the leaders table with 15 candidates and their capability scores.

    Inserts 5 internal candidates (BMW employees considered for promotion)
    and 10 external candidates (from other automotive/tech companies) into
    the ``leaders`` table.  Also seeds 12 ``leader_capability_scores`` rows
    per candidate (180 total).

    The function is idempotent: it checks for existing rows and skips
    seeding if data is already present (unless ``dry_run`` is True).

    Args:
        dry_run: If True, log planned inserts without writing to Supabase.
    """
    # ── Leaders ────────────────────────────────────────────────────────
    existing_leaders = fetch_all(
        "leaders", filters={"leader_type": "internal_candidate"}
    )
    existing_external = fetch_all(
        "leaders", filters={"leader_type": "external_candidate"}
    )
    existing_count = len(existing_leaders) + len(existing_external)

    if existing_count >= len(ALL_CANDIDATES) and not dry_run:
        logger.info(
            "Candidate leaders already seeded (%d rows), skipping.",
            existing_count,
        )
    elif dry_run:
        for c in ALL_CANDIDATES:
            logger.info(
                "[DRY RUN] Would upsert leader: %s (%s)",
                c["full_name"],
                c["leader_type"],
            )
    else:
        logger.info("Seeding %d candidate leaders ...", len(ALL_CANDIDATES))
        upsert("leaders", ALL_CANDIDATES)
        logger.info("Candidate leaders seeded successfully.")

    # ── Capability Scores ──────────────────────────────────────────────
    existing_scores = fetch_all("leader_capability_scores")
    # Filter to only scores belonging to our candidates
    candidate_ids = {c["id"] for c in ALL_CANDIDATES}
    candidate_score_count = sum(
        1 for s in existing_scores if s.get("leader_id") in candidate_ids
    )

    if candidate_score_count >= len(CAPABILITY_SCORES) and not dry_run:
        logger.info(
            "Candidate capability scores already seeded (%d rows), skipping.",
            candidate_score_count,
        )
    elif dry_run:
        logger.info(
            "[DRY RUN] Would upsert %d capability scores.",
            len(CAPABILITY_SCORES),
        )
    else:
        logger.info(
            "Seeding %d candidate capability scores ...",
            len(CAPABILITY_SCORES),
        )
        upsert("leader_capability_scores", CAPABILITY_SCORES)
        logger.info("Candidate capability scores seeded successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_candidates()
