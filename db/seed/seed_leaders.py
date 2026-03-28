"""Seed script for JD templates, roles, leaders, capability scores, reviews, and feedback.

Seeds the core leadership data that drives NEXUS analysis:
- 8 JD templates with competency weightings
- 10 roles (8 filled, 2 vacant)
- 8 current leader profiles
- Capability scores (12 dimensions per leader)
- Performance reviews (2-3 per leader, compressed ratings by design)
- 360 feedback (3-5 per leader, with deliberate contradictions for L3)

All operations use upsert for idempotency.
"""

import logging

from db.seed._ids import (
    DIMENSION_KEYS,
    JD_CTO,
    JD_HEAD_EV,
    JD_HEAD_RD,
    JD_PLANT_DIR,
    JD_SVP_MFG,
    JD_VP_IT,
    JD_VP_QUALITY,
    JD_VP_SUPPLY,
    L1_RICHTER,
    L2_STAHL,
    L3_BRENNER,
    L4_TANAKA,
    L5_GRUBER,
    L6_MITCHELL,
    L7_PATEL,
    L8_SANTOS,
    OU_AUTO,
    OU_DEBRECEN,
    OU_DINGOLFING,
    OU_EVBATTERY,
    OU_GROUP,
    OU_ITDIGITAL,
    OU_MUNICH,
    OU_QUALITY,
    OU_SPARTANBURG,
    OU_SUPPLYCHAIN,
    ROLE_CTO,
    ROLE_DIR_DEBRECEN,
    ROLE_DIR_DINGOLFING,
    ROLE_DIR_MUNICH,
    ROLE_DIR_SPARTANBURG,
    ROLE_HEAD_EV,
    ROLE_SVP_MFG,
    ROLE_VP_IT,
    ROLE_VP_QUALITY,
    ROLE_VP_SUPPLY,
)
from src.supabase_client import fetch_all, upsert

logger = logging.getLogger(__name__)


# ── Competency weighting helpers ────────────────────────────────────────────


def _weights(overrides: dict[str, float]) -> dict[str, float]:
    """Build a full 12-dimension weighting dict with defaults for unspecified keys.

    Args:
        overrides: Dict of dimension_key -> weight for high-priority dimensions.
            Unspecified dimensions get a default between 0.35 and 0.55 based on
            their position in DIMENSION_KEYS.

    Returns:
        Dict mapping all 12 DIMENSION_KEYS to float weights in [0.0, 1.0].
    """
    defaults = {
        "strategic_thinking": 0.50,
        "operational_execution": 0.45,
        "change_management": 0.40,
        "crisis_leadership": 0.45,
        "people_development": 0.50,
        "technical_depth": 0.40,
        "cross_functional_collab": 0.45,
        "innovation_orientation": 0.40,
        "cultural_sensitivity": 0.35,
        "risk_calibration": 0.45,
        "stakeholder_management": 0.50,
        "resilience_adaptability": 0.45,
    }
    result = {k: defaults.get(k, 0.45) for k in DIMENSION_KEYS}
    result.update(overrides)
    return result


# ── JD Templates ────────────────────────────────────────────────────────────


def seed_jd_templates() -> None:
    """Seed 8 JD templates with competency weightings.

    Each template defines the ideal competency profile for a leadership role type.
    Competency weightings map all 12 DIMENSION_KEYS to 0.0-1.0 importance weights.
    """
    templates = [
        {
            "id": JD_CTO,
            "role_type": "Chief Technology Officer",
            "base_description": (
                "The CTO leads BMW Group's technology strategy, driving innovation "
                "across vehicle platforms, manufacturing systems, and digital services. "
                "This role requires a visionary leader who can bridge deep technical "
                "expertise with enterprise-wide strategic execution."
            ),
            "competency_weightings": _weights({
                "strategic_thinking": 0.95,
                "innovation_orientation": 0.90,
                "technical_depth": 0.85,
                "stakeholder_management": 0.75,
                "change_management": 0.70,
                "cross_functional_collab": 0.65,
                "risk_calibration": 0.60,
                "resilience_adaptability": 0.55,
            }),
            "min_experience_years": 20,
            "typical_time_to_fill_days": 180,
        },
        {
            "id": JD_SVP_MFG,
            "role_type": "SVP Manufacturing",
            "base_description": (
                "The SVP Manufacturing oversees BMW Group's global production network "
                "spanning 30+ plants across four continents. This role demands an "
                "operational leader who can optimize throughput while managing complex "
                "workforce and supply chain dynamics."
            ),
            "competency_weightings": _weights({
                "operational_execution": 0.95,
                "people_development": 0.85,
                "crisis_leadership": 0.80,
                "resilience_adaptability": 0.75,
                "stakeholder_management": 0.70,
                "technical_depth": 0.65,
                "risk_calibration": 0.60,
                "cultural_sensitivity": 0.55,
            }),
            "min_experience_years": 18,
            "typical_time_to_fill_days": 150,
        },
        {
            "id": JD_VP_SUPPLY,
            "role_type": "VP Supply Chain",
            "base_description": (
                "The VP Supply Chain EMEA manages end-to-end supply operations across "
                "European manufacturing sites. This role requires balancing cost "
                "optimization with supply resilience in an increasingly volatile "
                "geopolitical environment."
            ),
            "competency_weightings": _weights({
                "operational_execution": 0.90,
                "risk_calibration": 0.85,
                "stakeholder_management": 0.80,
                "crisis_leadership": 0.70,
                "cross_functional_collab": 0.65,
                "resilience_adaptability": 0.60,
                "strategic_thinking": 0.55,
                "change_management": 0.50,
            }),
            "min_experience_years": 15,
            "typical_time_to_fill_days": 120,
        },
        {
            "id": JD_PLANT_DIR,
            "role_type": "Plant Director",
            "base_description": (
                "The Plant Director leads all manufacturing operations at a BMW Group "
                "production facility, responsible for output targets, quality standards, "
                "and workforce management. This role is the critical link between "
                "corporate strategy and shop-floor execution."
            ),
            "competency_weightings": _weights({
                "operational_execution": 0.90,
                "people_development": 0.85,
                "crisis_leadership": 0.80,
                "technical_depth": 0.70,
                "resilience_adaptability": 0.65,
                "risk_calibration": 0.60,
                "cultural_sensitivity": 0.55,
                "stakeholder_management": 0.55,
            }),
            "min_experience_years": 15,
            "typical_time_to_fill_days": 120,
        },
        {
            "id": JD_HEAD_EV,
            "role_type": "Head of EV Battery Systems",
            "base_description": (
                "The Head of EV Battery Systems leads BMW's next-generation battery "
                "development and production scaling. This role sits at the intersection "
                "of cutting-edge electrochemistry, manufacturing innovation, and the "
                "Group's Neue Klasse platform strategy."
            ),
            "competency_weightings": _weights({
                "technical_depth": 0.95,
                "innovation_orientation": 0.90,
                "change_management": 0.85,
                "strategic_thinking": 0.75,
                "cross_functional_collab": 0.70,
                "risk_calibration": 0.65,
                "resilience_adaptability": 0.60,
                "operational_execution": 0.55,
            }),
            "min_experience_years": 12,
            "typical_time_to_fill_days": 100,
        },
        {
            "id": JD_VP_QUALITY,
            "role_type": "VP Quality",
            "base_description": (
                "The VP Quality is the guardian of BMW Group's product and process "
                "quality standards across the global production network. This role "
                "requires a systematic thinker who can embed quality culture while "
                "managing risk across increasingly complex vehicle architectures."
            ),
            "competency_weightings": _weights({
                "operational_execution": 0.90,
                "risk_calibration": 0.90,
                "stakeholder_management": 0.80,
                "technical_depth": 0.75,
                "crisis_leadership": 0.65,
                "people_development": 0.60,
                "cultural_sensitivity": 0.55,
                "resilience_adaptability": 0.55,
            }),
            "min_experience_years": 15,
            "typical_time_to_fill_days": 120,
        },
        {
            "id": JD_VP_IT,
            "role_type": "VP IT & Digital",
            "base_description": (
                "The VP IT & Digital drives BMW Group's digital transformation across "
                "enterprise systems, manufacturing IT, and connected vehicle platforms. "
                "This role requires a technology leader who can modernize legacy "
                "infrastructure while delivering innovative digital capabilities."
            ),
            "competency_weightings": _weights({
                "technical_depth": 0.90,
                "innovation_orientation": 0.90,
                "change_management": 0.85,
                "strategic_thinking": 0.75,
                "cross_functional_collab": 0.70,
                "stakeholder_management": 0.60,
                "risk_calibration": 0.55,
                "resilience_adaptability": 0.55,
            }),
            "min_experience_years": 12,
            "typical_time_to_fill_days": 100,
        },
        {
            "id": JD_HEAD_RD,
            "role_type": "Head of R&D",
            "base_description": (
                "The Head of R&D leads BMW Group's research and advanced development "
                "across powertrain, autonomous driving, and materials science. This "
                "role shapes the technical direction of the Group's product portfolio "
                "for the next decade."
            ),
            "competency_weightings": _weights({
                "innovation_orientation": 0.95,
                "technical_depth": 0.90,
                "strategic_thinking": 0.85,
                "cross_functional_collab": 0.70,
                "change_management": 0.65,
                "people_development": 0.60,
                "risk_calibration": 0.55,
                "resilience_adaptability": 0.50,
            }),
            "min_experience_years": 18,
            "typical_time_to_fill_days": 150,
        },
    ]

    upsert("jd_templates", templates)
    logger.info("Seeded %d JD templates", len(templates))


# ── Roles ───────────────────────────────────────────────────────────────────


def seed_roles() -> None:
    """Seed 10 leadership roles (8 filled, 2 vacant).

    Roles define positions in the BMW org hierarchy. current_holder_id is NOT set
    here; it is set after leaders are inserted in seed_leaders().
    """
    roles = [
        {
            "id": ROLE_CTO,
            "title": "Chief Technology Officer",
            "role_level": "c_suite",
            "org_unit_id": OU_GROUP,
            "jd_template_id": JD_CTO,
            "is_filled": True,
            "criticality": "critical",
        },
        {
            "id": ROLE_SVP_MFG,
            "title": "SVP Manufacturing Operations",
            "role_level": "svp",
            "org_unit_id": OU_AUTO,
            "jd_template_id": JD_SVP_MFG,
            "is_filled": True,
            "reports_to_role_id": ROLE_CTO,
            "criticality": "critical",
        },
        {
            "id": ROLE_VP_SUPPLY,
            "title": "VP Supply Chain EMEA",
            "role_level": "vp",
            "org_unit_id": OU_SUPPLYCHAIN,
            "jd_template_id": JD_VP_SUPPLY,
            "is_filled": True,
            "reports_to_role_id": ROLE_SVP_MFG,
            "criticality": "high",
        },
        {
            "id": ROLE_DIR_MUNICH,
            "title": "Plant Director Munich",
            "role_level": "director",
            "org_unit_id": OU_MUNICH,
            "jd_template_id": JD_PLANT_DIR,
            "is_filled": True,
            "reports_to_role_id": ROLE_SVP_MFG,
            "criticality": "critical",
        },
        {
            "id": ROLE_DIR_DINGOLFING,
            "title": "Plant Director Dingolfing",
            "role_level": "director",
            "org_unit_id": OU_DINGOLFING,
            "jd_template_id": JD_PLANT_DIR,
            "is_filled": True,
            "reports_to_role_id": ROLE_SVP_MFG,
            "criticality": "high",
        },
        {
            "id": ROLE_DIR_SPARTANBURG,
            "title": "Plant Director Spartanburg",
            "role_level": "director",
            "org_unit_id": OU_SPARTANBURG,
            "jd_template_id": JD_PLANT_DIR,
            "is_filled": True,
            "reports_to_role_id": ROLE_SVP_MFG,
            "criticality": "high",
        },
        {
            "id": ROLE_VP_IT,
            "title": "VP IT & Digital",
            "role_level": "vp",
            "org_unit_id": OU_ITDIGITAL,
            "jd_template_id": JD_VP_IT,
            "is_filled": True,
            "criticality": "critical",
        },
        {
            "id": ROLE_VP_QUALITY,
            "title": "VP Quality",
            "role_level": "vp",
            "org_unit_id": OU_QUALITY,
            "jd_template_id": JD_VP_QUALITY,
            "is_filled": True,
            "reports_to_role_id": ROLE_SVP_MFG,
            "criticality": "high",
        },
        {
            "id": ROLE_HEAD_EV,
            "title": "Head of EV Battery Systems",
            "role_level": "director",
            "org_unit_id": OU_EVBATTERY,
            "jd_template_id": JD_HEAD_EV,
            "is_filled": False,
            "vacancy_date": "2026-01-15",
            "criticality": "critical",
        },
        {
            "id": ROLE_DIR_DEBRECEN,
            "title": "Plant Director Debrecen (iFactory)",
            "role_level": "director",
            "org_unit_id": OU_DEBRECEN,
            "jd_template_id": JD_PLANT_DIR,
            "is_filled": False,
            "vacancy_date": "2026-02-01",
            "criticality": "critical",
        },
    ]

    upsert("roles", roles)
    logger.info("Seeded %d roles", len(roles))


# ── Leaders ─────────────────────────────────────────────────────────────────

# Leader genome scores keyed by dimension order in DIMENSION_KEYS:
# [strategic_thinking, operational_execution, change_management, crisis_leadership,
#  people_development, technical_depth, cross_functional_collab, innovation_orientation,
#  cultural_sensitivity, risk_calibration, stakeholder_management, resilience_adaptability]

_LEADER_GENOMES: dict[str, list[float]] = {
    L1_RICHTER: [
        0.92, 0.55, 0.60, 0.50, 0.65, 0.85, 0.72, 0.88, 0.70, 0.78, 0.80, 0.68,
    ],
    L2_STAHL: [
        0.62, 0.94, 0.58, 0.88, 0.82, 0.80, 0.65, 0.45, 0.72, 0.75, 0.78, 0.85,
    ],
    L3_BRENNER: [
        0.60, 0.76, 0.48, 0.50, 0.55, 0.70, 0.58, 0.42, 0.68, 0.74, 0.72, 0.65,
    ],
    L4_TANAKA: [
        0.70, 0.85, 0.50, 0.68, 0.58, 0.93, 0.52, 0.75, 0.55, 0.78, 0.62, 0.72,
    ],
    L5_GRUBER: [
        0.48, 0.90, 0.35, 0.75, 0.60, 0.82, 0.45, 0.30, 0.85, 0.70, 0.78, 0.72,
    ],
    L6_MITCHELL: [
        0.75, 0.62, 0.82, 0.55, 0.78, 0.58, 0.80, 0.80, 0.52, 0.65, 0.68, 0.82,
    ],
    L7_PATEL: [
        0.82, 0.65, 0.78, 0.62, 0.60, 0.92, 0.55, 0.90, 0.40, 0.72, 0.50, 0.75,
    ],
    L8_SANTOS: [
        0.58, 0.88, 0.52, 0.65, 0.72, 0.82, 0.62, 0.40, 0.75, 0.92, 0.78, 0.70,
    ],
}

_LEADER_PROFILES = [
    {
        "id": L1_RICHTER,
        "full_name": "Dr. Klaus Richter",
        "current_role_id": ROLE_CTO,
        "leader_type": "internal_current",
        "years_experience": 25,
        "years_at_bmw": 18,
        "education_level": "phd",
        "education_field": "Electrical Engineering",
        "industry_background": ["automotive", "semiconductors"],
        "location_current": "Munich",
        "flight_risk": 0.15,
        "bio_summary": (
            "Strategic visionary who shaped BMW's technology roadmap through the EV "
            "transition. Exceptional at long-range planning and board-level "
            "communication but has a blind spot for day-to-day operational follow-through. "
            "His teams respect his intellect but sometimes feel unsupported on execution."
        ),
    },
    {
        "id": L2_STAHL,
        "full_name": "Petra Stahl",
        "current_role_id": ROLE_SVP_MFG,
        "leader_type": "internal_current",
        "years_experience": 22,
        "years_at_bmw": 20,
        "education_level": "masters",
        "education_field": "Industrial Engineering",
        "industry_background": ["automotive"],
        "location_current": "Munich",
        "flight_risk": 0.10,
        "bio_summary": (
            "Operations powerhouse who rose through the BMW production system. "
            "Can diagnose a bottleneck from a Gemba walk faster than any dashboard. "
            "Fiercely loyal but struggles to champion disruptive innovation — her "
            "instinct is always to optimize the existing process rather than reimagine it."
        ),
    },
    {
        "id": L3_BRENNER,
        "full_name": "Thomas Brenner",
        "current_role_id": ROLE_VP_SUPPLY,
        "leader_type": "internal_current",
        "years_experience": 18,
        "years_at_bmw": 15,
        "education_level": "masters",
        "education_field": "Supply Chain Management",
        "industry_background": ["automotive", "logistics"],
        "location_current": "Munich",
        "flight_risk": 0.20,
        "bio_summary": (
            "Appears to be a safe pair of hands on paper — steady ratings, no crises "
            "on his watch. However, 360 feedback reveals a pattern of conflict avoidance "
            "and decision paralysis under pressure. His team self-manages despite him, "
            "not because of him. A critical test case for NEXUS's ability to surface "
            "hidden leadership risk."
        ),
    },
    {
        "id": L4_TANAKA,
        "full_name": "Dr. Yuki Tanaka",
        "current_role_id": ROLE_DIR_MUNICH,
        "leader_type": "internal_current",
        "years_experience": 20,
        "years_at_bmw": 8,
        "education_level": "phd",
        "education_field": "Mechanical Engineering",
        "industry_background": ["automotive", "robotics"],
        "location_current": "Munich",
        "flight_risk": 0.25,
        "bio_summary": (
            "Brilliant technical mind who joined from Toyota's production engineering "
            "division. Has elevated Munich plant's automation capabilities significantly "
            "but finds BMW's consensus-driven culture frustrating. Struggles with the "
            "people-side of transformation — tends to lead with data rather than "
            "building coalitions."
        ),
    },
    {
        "id": L5_GRUBER,
        "full_name": "Hans Gruber",
        "current_role_id": ROLE_DIR_DINGOLFING,
        "leader_type": "internal_current",
        "years_experience": 28,
        "years_at_bmw": 28,
        "education_level": "masters",
        "education_field": "Production Management",
        "industry_background": ["automotive"],
        "location_current": "Dingolfing",
        "flight_risk": 0.05,
        "bio_summary": (
            "BMW lifer who knows every production line in Dingolfing by heart. "
            "Deeply respected by the workforce and runs a tight, efficient operation. "
            "However, actively resists digital transformation and EV-related changes, "
            "viewing them as threats to proven methods. Represents the institutional "
            "inertia NEXUS must identify."
        ),
    },
    {
        "id": L6_MITCHELL,
        "full_name": "Sarah Mitchell",
        "current_role_id": ROLE_DIR_SPARTANBURG,
        "leader_type": "internal_current",
        "years_experience": 12,
        "years_at_bmw": 5,
        "education_level": "mba",
        "education_field": "Business Administration",
        "industry_background": ["automotive", "consulting"],
        "location_current": "Spartanburg",
        "flight_risk": 0.35,
        "bio_summary": (
            "Rising star who joined from McKinsey's automotive practice. Brings fresh "
            "thinking on change management and cross-functional collaboration. Her "
            "Spartanburg team loves her energy, but she lacks deep operational tenure "
            "and has not yet been tested in a serious crisis. High flight risk — "
            "headhunters call regularly."
        ),
    },
    {
        "id": L7_PATEL,
        "full_name": "Dr. Raj Patel",
        "current_role_id": ROLE_VP_IT,
        "leader_type": "internal_current",
        "years_experience": 15,
        "years_at_bmw": 3,
        "education_level": "phd",
        "education_field": "Computer Science",
        "industry_background": ["big tech", "automotive"],
        "location_current": "Munich",
        "flight_risk": 0.40,
        "bio_summary": (
            "Digital native recruited from Google's autonomous vehicle division. "
            "Technically brilliant and drives innovation at speed, but has created "
            "significant cultural friction with BMW's traditional engineering culture. "
            "Highest flight risk in the leadership team — frustrated by what he sees "
            "as slow decision-making and resistance to modern engineering practices."
        ),
    },
    {
        "id": L8_SANTOS,
        "full_name": "Maria Santos",
        "current_role_id": ROLE_VP_QUALITY,
        "leader_type": "internal_current",
        "years_experience": 17,
        "years_at_bmw": 12,
        "education_level": "masters",
        "education_field": "Quality Engineering",
        "industry_background": ["automotive", "aerospace"],
        "location_current": "Munich",
        "flight_risk": 0.15,
        "bio_summary": (
            "Methodical quality leader who built BMW's predictive quality analytics "
            "capability. Her risk calibration is the best on the leadership team, but "
            "she can be overly cautious — sometimes blocking necessary speed-to-market "
            "decisions. Reliable and trusted but unlikely to drive bold transformation."
        ),
    },
]

# Mapping of leader_id -> role_id for updating roles with current_holder_id
_LEADER_ROLE_MAP = {
    L1_RICHTER: ROLE_CTO,
    L2_STAHL: ROLE_SVP_MFG,
    L3_BRENNER: ROLE_VP_SUPPLY,
    L4_TANAKA: ROLE_DIR_MUNICH,
    L5_GRUBER: ROLE_DIR_DINGOLFING,
    L6_MITCHELL: ROLE_DIR_SPARTANBURG,
    L7_PATEL: ROLE_VP_IT,
    L8_SANTOS: ROLE_VP_QUALITY,
}


def _build_capability_scores() -> list[dict]:
    """Build capability_scores rows for all 8 leaders across 12 dimensions.

    Uses fixed UUIDs with pattern 53000000-0000-4000-a000-LLLLDDDDDDDD where
    LLLL is the 1-indexed leader number and DDDDDDDD is the 1-indexed dimension.

    Returns:
        List of capability_scores row dicts ready for upsert.
    """
    rows: list[dict] = []
    leader_ids = [
        L1_RICHTER, L2_STAHL, L3_BRENNER, L4_TANAKA,
        L5_GRUBER, L6_MITCHELL, L7_PATEL, L8_SANTOS,
    ]

    for leader_idx, leader_id in enumerate(leader_ids, start=1):
        scores = _LEADER_GENOMES[leader_id]
        for dim_idx, dim_key in enumerate(DIMENSION_KEYS, start=1):
            raw = scores[dim_idx - 1]
            score_id = f"53000000-0000-4000-a000-{leader_idx:04d}{dim_idx:08d}"
            rows.append({
                "id": score_id,
                "leader_id": leader_id,
                "dimension": dim_key,
                "raw_score": raw,
                "corrected_score": raw,
                "confidence_low": max(0.0, round(raw - 0.05, 2)),
                "confidence_high": min(1.0, round(raw + 0.05, 2)),
                "assessor_type": "composite",
            })

    return rows


def _build_performance_reviews() -> list[dict]:
    """Build performance_reviews rows (2-3 per leader).

    Ratings are deliberately compressed in the 7.0-8.2 range to simulate the
    real-world problem of undifferentiated performance ratings in senior leadership.

    Uses fixed UUIDs: 54000000-0000-4000-a000-LLLLPPPPPPPP.

    Returns:
        List of performance_reviews row dicts ready for upsert.
    """
    leader_ids = [
        L1_RICHTER, L2_STAHL, L3_BRENNER, L4_TANAKA,
        L5_GRUBER, L6_MITCHELL, L7_PATEL, L8_SANTOS,
    ]

    # (overall_rating, goal_completion_pct, team_engagement_score, team_attrition_rate)
    # Per leader, per review period
    review_data: dict[str, list[tuple[str, float, float, float, float]]] = {
        L1_RICHTER: [
            ("2024-H1", 7.8, 0.85, 0.72, 0.08),
            ("2024-H2", 8.0, 0.88, 0.74, 0.07),
            ("2025-H1", 8.2, 0.90, 0.75, 0.06),
        ],
        L2_STAHL: [
            ("2024-H1", 7.9, 0.92, 0.78, 0.06),
            ("2024-H2", 8.1, 0.94, 0.80, 0.05),
            ("2025-H1", 7.8, 0.90, 0.76, 0.07),
        ],
        L3_BRENNER: [
            ("2024-H1", 7.4, 0.78, 0.65, 0.12),
            ("2024-H2", 7.5, 0.80, 0.63, 0.13),
            ("2025-H1", 7.3, 0.76, 0.60, 0.15),
        ],
        L4_TANAKA: [
            ("2024-H1", 7.7, 0.86, 0.68, 0.10),
            ("2024-H2", 7.9, 0.88, 0.70, 0.09),
            ("2025-H1", 7.6, 0.84, 0.66, 0.11),
        ],
        L5_GRUBER: [
            ("2024-H1", 7.6, 0.82, 0.74, 0.06),
            ("2024-H2", 7.5, 0.80, 0.72, 0.07),
        ],
        L6_MITCHELL: [
            ("2024-H1", 7.5, 0.80, 0.78, 0.09),
            ("2024-H2", 7.8, 0.84, 0.80, 0.08),
            ("2025-H1", 8.0, 0.87, 0.82, 0.07),
        ],
        L7_PATEL: [
            ("2024-H1", 7.9, 0.88, 0.62, 0.14),
            ("2024-H2", 8.1, 0.90, 0.64, 0.13),
            ("2025-H1", 7.7, 0.85, 0.60, 0.15),
        ],
        L8_SANTOS: [
            ("2024-H1", 7.6, 0.84, 0.76, 0.07),
            ("2024-H2", 7.8, 0.86, 0.78, 0.06),
            ("2025-H1", 7.7, 0.85, 0.77, 0.07),
        ],
    }

    rows: list[dict] = []
    for leader_idx, leader_id in enumerate(leader_ids, start=1):
        for period_idx, (period, rating, goal_pct, engagement, attrition) in enumerate(
            review_data[leader_id], start=1
        ):
            review_id = f"54000000-0000-4000-a000-{leader_idx:04d}{period_idx:08d}"
            rows.append({
                "id": review_id,
                "leader_id": leader_id,
                "review_period": period,
                "overall_rating": rating,
                "goal_completion_pct": goal_pct,
                "team_engagement_score": engagement,
                "team_attrition_rate": attrition,
            })

    return rows


def _build_feedback_360() -> list[dict]:
    """Build feedback_360 rows (3-5 per leader).

    CRITICAL: L3 Brenner's feedback deliberately contradicts his safe-looking
    performance ratings, revealing conflict avoidance and decision paralysis.
    Other leaders have realistic mixed feedback reflecting their archetype.

    Uses fixed UUIDs: 55000000-0000-4000-a000-LLLLFFFFFFFF.

    Returns:
        List of feedback_360 row dicts ready for upsert.
    """
    leader_ids = [
        L1_RICHTER, L2_STAHL, L3_BRENNER, L4_TANAKA,
        L5_GRUBER, L6_MITCHELL, L7_PATEL, L8_SANTOS,
    ]

    # (feedback_type, sentiment_score, summary_text)
    feedback_data: dict[str, list[tuple[str, float, str]]] = {
        L1_RICHTER: [
            (
                "peer_review", 0.75,
                "Klaus is the smartest person in any room and his technology vision "
                "is genuinely world-class. But he sets direction and then disappears "
                "— the execution gap between his strategy decks and reality is growing."
            ),
            (
                "direct_report", 0.60,
                "Inspiring to listen to in town halls, but when we need a decision on "
                "resource allocation or priority conflicts, he's unavailable. We spend "
                "weeks waiting for approvals that should take days."
            ),
            (
                "manager", 0.80,
                "Klaus has been instrumental in positioning BMW's technology narrative "
                "with the board and investors. His strategic thinking is exceptional. "
                "I need him to delegate less of the operational follow-through."
            ),
            (
                "self", 0.82,
                "I believe my strength is in setting long-term technology direction. "
                "I acknowledge I could improve on ensuring my teams have the day-to-day "
                "support they need to execute against our roadmaps."
            ),
        ],
        L2_STAHL: [
            (
                "peer_review", 0.80,
                "Petra runs the tightest ship in BMW. When a crisis hits production, "
                "she's the first person everyone calls. But she can be dismissive of "
                "ideas that don't come from the shop floor."
            ),
            (
                "direct_report", 0.85,
                "Best boss I've had at BMW. She knows every production line and "
                "genuinely develops her people. Only frustration: she shuts down "
                "conversations about new digital tools too quickly."
            ),
            (
                "manager", 0.78,
                "Petra's operational excellence is unmatched. My concern is her "
                "resistance to the digital manufacturing transformation. She optimizes "
                "the current system brilliantly but doesn't reimagine it."
            ),
        ],
        L3_BRENNER: [
            (
                "peer_review", 0.40,
                "Thomas avoids conflict at all costs. When the chip shortage hit, "
                "he deferred every decision upward rather than taking ownership. "
                "His suppliers don't respect him because he never pushes back."
            ),
            (
                "direct_report", 0.35,
                "He's a nice person but provides zero direction. Our team basically "
                "self-manages because he won't make calls. When I asked for a clear "
                "priority between two conflicting supplier negotiations, he said "
                "'both are important' and walked away."
            ),
            (
                "manager", 0.45,
                "Solid on paper but I'm concerned about his ability to handle the "
                "upcoming NK ramp. He freezes under real pressure. His ratings look "
                "fine because his team compensates for his lack of decisiveness."
            ),
            (
                "peer_review", 0.42,
                "I've worked with Thomas on three cross-functional initiatives. Each "
                "time, he agreed to everything in the meeting then did nothing. He's "
                "a professional head-nodder who avoids any position that might create "
                "friction."
            ),
            (
                "direct_report", 0.38,
                "I'm actively looking to transfer out. Thomas creates an illusion of "
                "calm but it's actually paralysis. During the logistics crisis last "
                "quarter, he held eleven alignment meetings before making a single "
                "decision. By then the damage was done."
            ),
        ],
        L4_TANAKA: [
            (
                "peer_review", 0.65,
                "Yuki's technical capabilities are outstanding — she upgraded the "
                "Munich paint shop automation beyond anything we thought possible. "
                "But she struggles to bring people along on the journey. Her "
                "presentations are data-perfect and emotionally flat."
            ),
            (
                "direct_report", 0.55,
                "Brilliant engineer, challenging manager. She expects everyone to "
                "operate at her technical level and gets visibly frustrated when "
                "they don't. Mentoring and coaching aren't her strengths."
            ),
            (
                "manager", 0.70,
                "Yuki delivers exceptional technical results but I worry about "
                "her team retention. Three senior engineers have transferred out "
                "this year. She needs to invest more in the people side."
            ),
            (
                "self", 0.72,
                "I am most effective when solving complex technical challenges. "
                "I recognize that BMW's culture requires more consensus-building "
                "than I am accustomed to from my previous role at Toyota."
            ),
        ],
        L5_GRUBER: [
            (
                "peer_review", 0.60,
                "Hans is a Dingolfing institution. The plant runs like clockwork "
                "under his leadership. But he actively sabotages digital initiatives "
                "— he told his team to ignore the new MES rollout timeline."
            ),
            (
                "direct_report", 0.70,
                "He genuinely cares about the workforce and production quality. "
                "But he's stuck in 2015. When we suggest process innovations, "
                "he always says 'we tried something like that and it failed.' "
                "He hasn't tried anything new in years."
            ),
            (
                "manager", 0.55,
                "Hans delivers solid numbers quarter after quarter, but Dingolfing "
                "is falling behind on Industry 4.0 adoption. He sees every change "
                "as a threat rather than an opportunity. Succession planning for "
                "this role is becoming urgent."
            ),
        ],
        L6_MITCHELL: [
            (
                "peer_review", 0.78,
                "Sarah brings incredible energy and fresh thinking. She's transformed "
                "the culture at Spartanburg in just two years. My only concern is "
                "whether she can handle a real production crisis — she hasn't been "
                "tested yet."
            ),
            (
                "direct_report", 0.88,
                "Best leader I've worked for. She actually listens, empowers her "
                "team, and creates space for new ideas. She's not the deepest on "
                "production technology but she hires experts and trusts them."
            ),
            (
                "manager", 0.75,
                "Sarah is our highest-potential leader. She needs more operational "
                "depth and crisis experience. I'm concerned about flight risk — "
                "she's been approached by Tesla and Rivian this quarter."
            ),
            (
                "interview_note", 0.80,
                "During the leadership assessment center, Sarah demonstrated "
                "exceptional change management instincts and cross-functional "
                "collaboration. Her weakest area was the crisis simulation exercise "
                "where she hesitated under time pressure."
            ),
        ],
        L7_PATEL: [
            (
                "peer_review", 0.45,
                "Raj is technically brilliant but culturally tone-deaf at BMW. He "
                "pushes Silicon Valley speed into a German engineering culture and "
                "then is surprised when people resist. He calls BMW processes "
                "'legacy thinking' in meetings — that doesn't win allies."
            ),
            (
                "direct_report", 0.72,
                "Working for Raj is exciting — he moves fast and gives us real "
                "autonomy. But he burns bridges with other departments constantly. "
                "We've become isolated because no one wants to collaborate with IT "
                "anymore."
            ),
            (
                "manager", 0.58,
                "Raj's technical output is exceptional but I receive complaints "
                "weekly about his stakeholder management. He needs to understand "
                "that at BMW, how you drive change matters as much as what you "
                "change. Flight risk is very high — he's openly frustrated."
            ),
            (
                "peer_review", 0.40,
                "I tried to partner with Raj on the factory digital twin initiative. "
                "He dismissed our team's domain expertise and tried to rebuild "
                "everything from scratch using his Silicon Valley playbook. The "
                "project is now six months behind."
            ),
            (
                "self", 0.65,
                "I joined BMW to drive a digital transformation that I believe is "
                "existential for the company. I am frustrated by the pace of change "
                "but I understand I need to improve how I bring people along. "
                "Cultural integration remains my biggest personal challenge."
            ),
        ],
        L8_SANTOS: [
            (
                "peer_review", 0.72,
                "Maria is the conscience of our quality system — thorough, methodical, "
                "and uncompromising on standards. Sometimes too uncompromising — she "
                "held up the i5 launch for three weeks over a cosmetic defect that "
                "was within spec tolerance."
            ),
            (
                "direct_report", 0.78,
                "Maria develops her team well and creates a culture of precision. "
                "She could be more decisive under time pressure — sometimes perfect "
                "is the enemy of good enough, especially with launch deadlines."
            ),
            (
                "manager", 0.75,
                "Maria's risk calibration is the best on the leadership team. She "
                "catches issues others miss. My feedback is that she needs to balance "
                "quality rigor with business agility. Not every decision needs the "
                "same level of analysis."
            ),
        ],
    }

    rows: list[dict] = []
    for leader_idx, leader_id in enumerate(leader_ids, start=1):
        for fb_idx, (fb_type, sentiment, text) in enumerate(
            feedback_data[leader_id], start=1
        ):
            fb_id = f"55000000-0000-4000-a000-{leader_idx:04d}{fb_idx:08d}"
            rows.append({
                "id": fb_id,
                "leader_id": leader_id,
                "feedback_type": fb_type,
                "sentiment_score": sentiment,
                "feedback_text": text,
            })

    return rows


def seed_leaders() -> None:
    """Seed 8 current leaders with profiles, capability scores, reviews, and feedback.

    Inserts leader profiles, then updates roles with current_holder_id, then
    inserts capability_scores, performance_reviews, and feedback_360 rows.
    All operations use upsert for idempotency.
    """
    # 1. Insert leader profiles
    upsert("leaders", _LEADER_PROFILES)
    logger.info("Seeded %d leader profiles", len(_LEADER_PROFILES))

    # 2. Update roles with current_holder_id (use direct update, not upsert)
    from src.supabase_client import get_supabase

    sb = get_supabase()
    for leader_id, role_id in _LEADER_ROLE_MAP.items():
        sb.table("roles").update({"current_holder_id": leader_id}).eq(
            "id", role_id
        ).execute()
    logger.info("Updated %d roles with current_holder_id", len(_LEADER_ROLE_MAP))

    # 3. Insert capability scores (8 leaders x 12 dimensions = 96 rows)
    cap_scores = _build_capability_scores()
    upsert("leader_capability_scores", cap_scores)
    logger.info("Seeded %d capability_scores rows", len(cap_scores))

    # 4. Insert performance reviews
    reviews = _build_performance_reviews()
    upsert("performance_reviews", reviews)
    logger.info("Seeded %d performance_reviews rows", len(reviews))

    # 5. Insert 360 feedback
    feedback = _build_feedback_360()
    upsert("feedback_360", feedback)
    logger.info("Seeded %d feedback_360 rows", len(feedback))


# ── Main entry point ────────────────────────────────────────────────────────


def main() -> None:
    """Run all seed functions in dependency order.

    Order: JD templates -> Roles -> Leaders (which also seeds scores,
    reviews, and feedback).
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    logger.info("Starting leadership seed...")

    seed_jd_templates()
    seed_roles()
    seed_leaders()

    logger.info("Leadership seed complete.")


if __name__ == "__main__":
    main()
