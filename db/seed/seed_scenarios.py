"""Seed competency dimensions, stress scenarios, and interaction rules.

Populates the core analytical framework for NEXUS leadership assessment:
- 12 competency dimensions across cognitive, execution, interpersonal, character, and domain categories
- 8 stress scenarios modelling plausible BMW operational futures
- 32 dimension interaction rules capturing complementary, clash, and groupthink effects
"""

import logging

from db.seed._ids import (
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
    OU_AUTO,
    OU_DEBRECEN,
    OU_DINGOLFING,
    OU_EVBATTERY,
    OU_FIZ,
    OU_GROUP,
    OU_HR,
    OU_ITDIGITAL,
    OU_LANDSHUT,
    OU_MUNICH,
    OU_NK,
    OU_QUALITY,
    OU_SPARTANBURG,
    OU_SUPPLYCHAIN,
    SC_BATTERY_CRISIS,
    SC_COMPOUND,
    SC_CYBER_BREACH,
    SC_LEADER_CASCADE,
    SC_MUNICH_EV,
    SC_NK_RAMPUP,
    SC_REGULATORY,
    SC_TRADE_WAR,
)
from src.supabase_client import fetch_all, upsert

logger = logging.getLogger(__name__)

# ── Dimension Data ──────────────────────────────────────────────────────────

DIMENSIONS = [
    {
        "id": DIM_STRATEGIC,
        "key": "strategic_thinking",
        "name": "Strategic Thinking",
        "category": "cognitive",
        "description": (
            "See the big picture, connect signals across domains, "
            "formulate long-term plans under ambiguity."
        ),
    },
    {
        "id": DIM_OPERATIONAL,
        "key": "operational_execution",
        "name": "Operational Execution",
        "category": "execution",
        "description": (
            "Translate strategy into daily operations with process discipline, "
            "output focus, and KPI accountability."
        ),
    },
    {
        "id": DIM_CHANGE,
        "key": "change_management",
        "name": "Change Management",
        "category": "execution",
        "description": (
            "Lead through transformation, manage resistance, maintain momentum "
            "and morale under uncertainty."
        ),
    },
    {
        "id": DIM_CRISIS,
        "key": "crisis_leadership",
        "name": "Crisis Leadership",
        "category": "character",
        "description": (
            "Make fast decisions under pressure, communicate clearly in chaos, "
            "stabilize teams during emergencies."
        ),
    },
    {
        "id": DIM_PEOPLE,
        "key": "people_development",
        "name": "People Development",
        "category": "interpersonal",
        "description": (
            "Grow talent, build succession pipelines, coach effectively, "
            "delegate to empower rather than control."
        ),
    },
    {
        "id": DIM_TECHNICAL,
        "key": "technical_depth",
        "name": "Technical Depth",
        "category": "domain",
        "description": (
            "Domain expertise in the relevant area: manufacturing, EV, software, "
            "supply chain, quality systems, etc."
        ),
    },
    {
        "id": DIM_CROSSFUNC,
        "key": "cross_functional_collab",
        "name": "Cross-Functional Collaboration",
        "category": "interpersonal",
        "description": (
            "Work across silos, build bridges between departments, "
            "influence without direct authority."
        ),
    },
    {
        "id": DIM_INNOVATION,
        "key": "innovation_orientation",
        "name": "Innovation Orientation",
        "category": "cognitive",
        "description": (
            "Openness to new approaches, challenge status quo constructively, "
            "tolerate productive experimentation."
        ),
    },
    {
        "id": DIM_CULTURAL,
        "key": "cultural_sensitivity",
        "name": "Cultural Sensitivity",
        "category": "interpersonal",
        "description": (
            "Effectiveness in multinational contexts. At BMW Germany: "
            "works council (Betriebsrat) relationship management."
        ),
    },
    {
        "id": DIM_RISK,
        "key": "risk_calibration",
        "name": "Risk Calibration",
        "category": "cognitive",
        "description": (
            "Take calibrated risks — neither reckless nor paralyzed. "
            "Match risk appetite to organizational context."
        ),
    },
    {
        "id": DIM_STAKEHOLDER,
        "key": "stakeholder_management",
        "name": "Stakeholder Management",
        "category": "interpersonal",
        "description": (
            "Manage upward (board/SVP), sideways (peers), outward "
            "(suppliers, regulators, works council, public)."
        ),
    },
    {
        "id": DIM_RESILIENCE,
        "key": "resilience_adaptability",
        "name": "Resilience & Adaptability",
        "category": "character",
        "description": (
            "Personal stamina under sustained pressure, ability to pivot "
            "when plans fail, recover from setbacks."
        ),
    },
]

# ── Scenario Data ───────────────────────────────────────────────────────────


def _cdv(
    strategic: float = 0.35,
    operational: float = 0.35,
    change: float = 0.35,
    crisis: float = 0.35,
    people: float = 0.35,
    technical: float = 0.35,
    crossfunc: float = 0.35,
    innovation: float = 0.35,
    cultural: float = 0.35,
    risk: float = 0.35,
    stakeholder: float = 0.35,
    resilience: float = 0.35,
) -> dict[str, float]:
    """Build a capability demand vector with defaults for low-demand dimensions.

    Args:
        strategic: Demand for strategic_thinking (0.0-1.0).
        operational: Demand for operational_execution (0.0-1.0).
        change: Demand for change_management (0.0-1.0).
        crisis: Demand for crisis_leadership (0.0-1.0).
        people: Demand for people_development (0.0-1.0).
        technical: Demand for technical_depth (0.0-1.0).
        crossfunc: Demand for cross_functional_collab (0.0-1.0).
        innovation: Demand for innovation_orientation (0.0-1.0).
        cultural: Demand for cultural_sensitivity (0.0-1.0).
        risk: Demand for risk_calibration (0.0-1.0).
        stakeholder: Demand for stakeholder_management (0.0-1.0).
        resilience: Demand for resilience_adaptability (0.0-1.0).

    Returns:
        Dict mapping all 12 dimension keys to demand values.
    """
    return {
        "strategic_thinking": strategic,
        "operational_execution": operational,
        "change_management": change,
        "crisis_leadership": crisis,
        "people_development": people,
        "technical_depth": technical,
        "cross_functional_collab": crossfunc,
        "innovation_orientation": innovation,
        "cultural_sensitivity": cultural,
        "risk_calibration": risk,
        "stakeholder_management": stakeholder,
        "resilience_adaptability": resilience,
    }


# Pre-compute SC1 and SC2 vectors for compound scenario
_SC1_CDV = _cdv(
    strategic=0.5,
    operational=0.9,
    change=0.9,
    crisis=0.6,
    people=0.45,
    technical=0.85,
    crossfunc=0.5,
    innovation=0.5,
    cultural=0.4,
    risk=0.45,
    stakeholder=0.45,
    resilience=0.5,
)
_SC2_CDV = _cdv(
    strategic=0.4,
    operational=0.85,
    change=0.4,
    crisis=0.95,
    people=0.35,
    technical=0.5,
    crossfunc=0.4,
    innovation=0.35,
    cultural=0.35,
    risk=0.85,
    stakeholder=0.8,
    resilience=0.5,
)
_COMPOUND_CDV = {k: max(_SC1_CDV[k], _SC2_CDV[k]) for k in _SC1_CDV}


SCENARIOS = [
    {
        "id": SC_NK_RAMPUP,
        "name": "Neue Klasse Ramp-Up Acceleration",
        "category": "transformation",
        "narrative": (
            "BMW's next-generation Neue Klasse platform enters critical "
            "industrialization phase across multiple plants simultaneously. "
            "Any ramp-up delay risks market share loss to competitors "
            "already shipping next-gen EVs."
        ),
        "probability": 0.85,
        "capability_demand_vector": _SC1_CDV,
        "affected_org_units": [
            OU_NK, OU_MUNICH, OU_DEBRECEN, OU_EVBATTERY, OU_LANDSHUT,
        ],
        "time_horizon_months": 18,
        "compound_of": [],
    },
    {
        "id": SC_BATTERY_CRISIS,
        "name": "Battery Supply Chain Crisis",
        "category": "crisis",
        "narrative": (
            "A critical battery cell supplier faces insolvency, threatening "
            "EV production across all plants. Immediate action needed to "
            "secure alternative supply while maintaining production targets."
        ),
        "probability": 0.55,
        "capability_demand_vector": _SC2_CDV,
        "affected_org_units": [OU_EVBATTERY, OU_SUPPLYCHAIN, OU_NK],
        "time_horizon_months": 6,
        "compound_of": [],
    },
    {
        "id": SC_MUNICH_EV,
        "name": "Munich Plant EV Transformation",
        "category": "transformation",
        "narrative": (
            "BMW's flagship Munich plant must convert from ICE to full EV "
            "production while maintaining output. This requires retraining "
            "thousands of workers and managing works council negotiations."
        ),
        "probability": 0.90,
        "capability_demand_vector": _cdv(
            strategic=0.5,
            operational=0.5,
            change=0.95,
            crisis=0.4,
            people=0.8,
            technical=0.8,
            crossfunc=0.5,
            innovation=0.5,
            cultural=0.75,
            risk=0.45,
            stakeholder=0.5,
            resilience=0.5,
        ),
        "affected_org_units": [OU_MUNICH, OU_HR, OU_ITDIGITAL],
        "time_horizon_months": 24,
        "compound_of": [],
    },
    {
        "id": SC_TRADE_WAR,
        "name": "Trade War / Tariff Escalation",
        "category": "competitive",
        "narrative": (
            "Escalating US-EU-China tariffs disrupt BMW's global production "
            "network. Spartanburg export economics shift dramatically, "
            "requiring rapid strategic repositioning of manufacturing footprint."
        ),
        "probability": 0.40,
        "capability_demand_vector": _cdv(
            strategic=0.9,
            operational=0.45,
            change=0.4,
            crisis=0.45,
            people=0.35,
            technical=0.35,
            crossfunc=0.5,
            innovation=0.4,
            cultural=0.5,
            risk=0.8,
            stakeholder=0.85,
            resilience=0.7,
        ),
        "affected_org_units": [OU_SPARTANBURG, OU_SUPPLYCHAIN, OU_GROUP],
        "time_horizon_months": 12,
        "compound_of": [],
    },
    {
        "id": SC_LEADER_CASCADE,
        "name": "Key Leader Departure Cascade",
        "category": "crisis",
        "narrative": (
            "Three senior plant directors resign within a quarter, triggered "
            "by competitor poaching. Succession pipelines are shallow and "
            "institutional knowledge loss is acute."
        ),
        "probability": 0.30,
        "capability_demand_vector": _cdv(
            strategic=0.4,
            operational=0.45,
            change=0.45,
            crisis=0.8,
            people=0.9,
            technical=0.35,
            crossfunc=0.8,
            innovation=0.35,
            cultural=0.45,
            risk=0.5,
            stakeholder=0.5,
            resilience=0.85,
        ),
        "affected_org_units": [OU_AUTO, OU_MUNICH, OU_DINGOLFING],
        "time_horizon_months": 6,
        "compound_of": [],
    },
    {
        "id": SC_CYBER_BREACH,
        "name": "Digital Factory Cybersecurity Breach",
        "category": "crisis",
        "narrative": (
            "A sophisticated cyberattack compromises OT systems in connected "
            "factories, halting production lines. Recovery requires coordinated "
            "IT-OT response while managing public disclosure obligations."
        ),
        "probability": 0.25,
        "capability_demand_vector": _cdv(
            strategic=0.4,
            operational=0.5,
            change=0.35,
            crisis=0.95,
            people=0.35,
            technical=0.9,
            crossfunc=0.45,
            innovation=0.4,
            cultural=0.35,
            risk=0.8,
            stakeholder=0.85,
            resilience=0.5,
        ),
        "affected_org_units": [OU_ITDIGITAL, OU_MUNICH, OU_DEBRECEN],
        "time_horizon_months": 3,
        "compound_of": [],
    },
    {
        "id": SC_REGULATORY,
        "name": "EU Regulatory Compliance Overhaul",
        "category": "regulatory",
        "narrative": (
            "New EU emissions, battery passport, and AI Act regulations "
            "require sweeping compliance changes across production and digital "
            "systems. Non-compliance penalties threaten market access."
        ),
        "probability": 0.60,
        "capability_demand_vector": _cdv(
            strategic=0.45,
            operational=0.7,
            change=0.45,
            crisis=0.35,
            people=0.4,
            technical=0.5,
            crossfunc=0.45,
            innovation=0.35,
            cultural=0.7,
            risk=0.85,
            stakeholder=0.9,
            resilience=0.4,
        ),
        "affected_org_units": [OU_QUALITY, OU_GROUP, OU_FIZ],
        "time_horizon_months": 12,
        "compound_of": [],
    },
    {
        "id": SC_COMPOUND,
        "name": "Compound: NK + Supply Crisis",
        "category": "compound",
        "narrative": (
            "The Neue Klasse ramp-up coincides with a battery supply crisis, "
            "creating compounding pressure on manufacturing leadership. "
            "Resource contention and decision fatigue amplify both scenarios."
        ),
        "probability": 0.20,
        "capability_demand_vector": _COMPOUND_CDV,
        "affected_org_units": list(
            set([
                OU_NK, OU_MUNICH, OU_DEBRECEN, OU_EVBATTERY, OU_LANDSHUT,
                OU_SUPPLYCHAIN,
            ])
        ),
        "time_horizon_months": 12,
        "compound_of": [SC_NK_RAMPUP, SC_BATTERY_CRISIS],
    },
]

# ── Interaction Rules ───────────────────────────────────────────────────────


def _rule_id(n: int) -> str:
    """Generate a fixed UUID for interaction rule number n.

    Args:
        n: Rule number (1-32).

    Returns:
        Fixed UUID string.
    """
    return f"70000000-0000-4000-a000-0000000000{n:02d}"


INTERACTION_RULES = [
    # 1-5: Hierarchical complementary pairs
    {
        "id": _rule_id(1),
        "dimension_a": "strategic_thinking",
        "dimension_b": "operational_execution",
        "relationship_type": "hierarchical",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.8,
        "description": (
            "A strategic thinker paired with an operational executor creates "
            "vision-to-action alignment critical for BMW plant transformations."
        ),
    },
    {
        "id": _rule_id(2),
        "dimension_a": "crisis_leadership",
        "dimension_b": "operational_execution",
        "relationship_type": "hierarchical",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.75,
        "description": (
            "Crisis leaders who delegate execution effectively keep production "
            "running while managing the emergency response."
        ),
    },
    {
        "id": _rule_id(3),
        "dimension_a": "strategic_thinking",
        "dimension_b": "technical_depth",
        "relationship_type": "hierarchical",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.7,
        "description": (
            "Strategic vision grounded in technical reality avoids moonshot "
            "plans that cannot be industrialized on BMW timelines."
        ),
    },
    {
        "id": _rule_id(4),
        "dimension_a": "people_development",
        "dimension_b": "operational_execution",
        "relationship_type": "hierarchical",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.65,
        "description": (
            "Leaders who develop their teams while maintaining output "
            "discipline build sustainable plant performance."
        ),
    },
    {
        "id": _rule_id(5),
        "dimension_a": "stakeholder_management",
        "dimension_b": "change_management",
        "relationship_type": "hierarchical",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.75,
        "description": (
            "Board-level stakeholder alignment from above combined with "
            "ground-level change execution drives transformation success."
        ),
    },
    # 6-10: Peer complementary pairs
    {
        "id": _rule_id(6),
        "dimension_a": "change_management",
        "dimension_b": "resilience_adaptability",
        "relationship_type": "cross_functional",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.75,
        "description": (
            "Change leaders paired with resilient adapters sustain momentum "
            "through inevitable setbacks in EV transformation programs."
        ),
    },
    {
        "id": _rule_id(7),
        "dimension_a": "cross_functional_collab",
        "dimension_b": "cultural_sensitivity",
        "relationship_type": "peer",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.7,
        "description": (
            "Cross-functional collaborators with cultural sensitivity navigate "
            "BMW's multinational matrix structure and works council dynamics."
        ),
    },
    {
        "id": _rule_id(8),
        "dimension_a": "technical_depth",
        "dimension_b": "innovation_orientation",
        "relationship_type": "peer",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.7,
        "description": (
            "Deep technical knowledge combined with innovation openness "
            "enables practical breakthroughs in manufacturing processes."
        ),
    },
    {
        "id": _rule_id(9),
        "dimension_a": "risk_calibration",
        "dimension_b": "stakeholder_management",
        "relationship_type": "peer",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.65,
        "description": (
            "Calibrated risk-takers who manage stakeholder expectations "
            "can push bold initiatives without triggering board anxiety."
        ),
    },
    {
        "id": _rule_id(10),
        "dimension_a": "people_development",
        "dimension_b": "cross_functional_collab",
        "relationship_type": "peer",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.6,
        "description": (
            "Talent developers who collaborate across functions build "
            "the rotation and mobility culture BMW needs for succession."
        ),
    },
    # 11-16: Clash / negative interactions
    {
        "id": _rule_id(11),
        "dimension_a": "innovation_orientation",
        "dimension_b": "risk_calibration",
        "relationship_type": "peer",
        "interaction_effect": "clash_negative",
        "effect_magnitude": 0.6,
        "description": (
            "Innovation pushers and risk calibrators may clash on experiment "
            "scope, creating decision gridlock in fast-moving EV programs."
        ),
    },
    {
        "id": _rule_id(12),
        "dimension_a": "strategic_thinking",
        "dimension_b": "operational_execution",
        "relationship_type": "peer",
        "interaction_effect": "clash_negative",
        "effect_magnitude": 0.55,
        "description": (
            "At peer level, strategists and operators may talk past each "
            "other — one sees the horizon, the other sees today's line rate."
        ),
    },
    {
        "id": _rule_id(13),
        "dimension_a": "crisis_leadership",
        "dimension_b": "people_development",
        "relationship_type": "peer",
        "interaction_effect": "clash_negative",
        "effect_magnitude": 0.5,
        "description": (
            "Crisis-mode leaders may override developmental approaches, "
            "creating tension with people-first leaders during emergencies."
        ),
    },
    {
        "id": _rule_id(14),
        "dimension_a": "innovation_orientation",
        "dimension_b": "operational_execution",
        "relationship_type": "peer",
        "interaction_effect": "clash_negative",
        "effect_magnitude": 0.6,
        "description": (
            "Innovators disrupt process stability that operators depend on. "
            "In BMW plants, this tension surfaces during process changes."
        ),
    },
    {
        "id": _rule_id(15),
        "dimension_a": "change_management",
        "dimension_b": "cultural_sensitivity",
        "relationship_type": "hierarchical",
        "interaction_effect": "clash_negative",
        "effect_magnitude": 0.5,
        "description": (
            "Aggressive change drivers may clash with culturally sensitive "
            "leaders over transformation pace, especially in German plants "
            "with strong works council traditions."
        ),
    },
    {
        "id": _rule_id(16),
        "dimension_a": "crisis_leadership",
        "dimension_b": "stakeholder_management",
        "relationship_type": "peer",
        "interaction_effect": "clash_negative",
        "effect_magnitude": 0.55,
        "description": (
            "Crisis leaders favor speed; stakeholder managers favor "
            "consultation. Under time pressure, these approaches conflict."
        ),
    },
    # 17-24: Groupthink / overlap interactions
    {
        "id": _rule_id(17),
        "dimension_a": "technical_depth",
        "dimension_b": "technical_depth",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.65,
        "description": (
            "Two deep technologists may reinforce each other's assumptions, "
            "missing strategic or people dimensions of a decision."
        ),
    },
    {
        "id": _rule_id(18),
        "dimension_a": "strategic_thinking",
        "dimension_b": "strategic_thinking",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.55,
        "description": (
            "Multiple strategists without an operator may produce elegant "
            "plans that cannot be executed on the shop floor."
        ),
    },
    {
        "id": _rule_id(19),
        "dimension_a": "operational_execution",
        "dimension_b": "operational_execution",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.6,
        "description": (
            "Paired operators may optimize current processes but resist "
            "the fundamental changes required for EV transformation."
        ),
    },
    {
        "id": _rule_id(20),
        "dimension_a": "risk_calibration",
        "dimension_b": "risk_calibration",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.5,
        "description": (
            "Two risk calibrators may become overly cautious together, "
            "missing the boldness window BMW needs for Neue Klasse."
        ),
    },
    {
        "id": _rule_id(21),
        "dimension_a": "stakeholder_management",
        "dimension_b": "stakeholder_management",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.5,
        "description": (
            "Dual stakeholder managers may over-index on consensus-building, "
            "slowing decisions when speed matters more than buy-in."
        ),
    },
    {
        "id": _rule_id(22),
        "dimension_a": "innovation_orientation",
        "dimension_b": "innovation_orientation",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.6,
        "description": (
            "Two innovators may chase novelty without grounding, "
            "undermining the process discipline BMW manufacturing requires."
        ),
    },
    {
        "id": _rule_id(23),
        "dimension_a": "cultural_sensitivity",
        "dimension_b": "cultural_sensitivity",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.45,
        "description": (
            "Over-indexing on cultural sensitivity may slow decisions "
            "as leaders seek excessive consensus across all stakeholder groups."
        ),
    },
    {
        "id": _rule_id(24),
        "dimension_a": "crisis_leadership",
        "dimension_b": "crisis_leadership",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.55,
        "description": (
            "Two crisis leaders may compete for command, creating confusion "
            "about who is directing the response."
        ),
    },
    # 25-28: Cross-functional complementary pairs
    {
        "id": _rule_id(25),
        "dimension_a": "technical_depth",
        "dimension_b": "change_management",
        "relationship_type": "cross_functional",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.7,
        "description": (
            "Technical credibility from one leader combined with change "
            "expertise from another builds trust during plant retooling."
        ),
    },
    {
        "id": _rule_id(26),
        "dimension_a": "resilience_adaptability",
        "dimension_b": "crisis_leadership",
        "relationship_type": "cross_functional",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.7,
        "description": (
            "Resilient leaders sustain team morale while crisis leaders "
            "drive rapid response — essential during supply disruptions."
        ),
    },
    {
        "id": _rule_id(27),
        "dimension_a": "cultural_sensitivity",
        "dimension_b": "stakeholder_management",
        "relationship_type": "cross_functional",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.65,
        "description": (
            "Cultural sensitivity enriches stakeholder management in BMW's "
            "global operations, especially with works council engagement."
        ),
    },
    {
        "id": _rule_id(28),
        "dimension_a": "people_development",
        "dimension_b": "resilience_adaptability",
        "relationship_type": "cross_functional",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.6,
        "description": (
            "Talent developers paired with resilient leaders build teams "
            "that can sustain performance through prolonged transformation."
        ),
    },
    # 29-32: Mixed hierarchical interactions
    {
        "id": _rule_id(29),
        "dimension_a": "innovation_orientation",
        "dimension_b": "change_management",
        "relationship_type": "hierarchical",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.7,
        "description": (
            "Innovation vision from above with change management execution "
            "below translates new ideas into operational reality."
        ),
    },
    {
        "id": _rule_id(30),
        "dimension_a": "resilience_adaptability",
        "dimension_b": "resilience_adaptability",
        "relationship_type": "peer",
        "interaction_effect": "overlap_groupthink",
        "effect_magnitude": 0.4,
        "description": (
            "Two resilient leaders may normalize adversity instead of "
            "escalating systemic issues that require structural fixes."
        ),
    },
    {
        "id": _rule_id(31),
        "dimension_a": "strategic_thinking",
        "dimension_b": "risk_calibration",
        "relationship_type": "hierarchical",
        "interaction_effect": "complementary_positive",
        "effect_magnitude": 0.7,
        "description": (
            "Strategic direction from above with risk calibration below "
            "ensures bold plans are stress-tested before execution."
        ),
    },
    {
        "id": _rule_id(32),
        "dimension_a": "people_development",
        "dimension_b": "technical_depth",
        "relationship_type": "cross_functional",
        "interaction_effect": "clash_negative",
        "effect_magnitude": 0.45,
        "description": (
            "People developers may push rotation and generalism while "
            "technical depth leaders insist on deep specialization — "
            "a tension visible in BMW engineering career paths."
        ),
    },
]


# ── Seed Functions ──────────────────────────────────────────────────────────


def seed_dimensions() -> None:
    """Seed the 12 competency dimensions into the dimensions table.

    Each dimension represents a leadership competency axis used by NEXUS
    agents to evaluate candidates. Uses fixed UUIDs from _ids.py for
    idempotent upserts.
    """
    existing = fetch_all("competency_dimensions")
    if len(existing) >= len(DIMENSIONS):
        logger.info(
            "Dimensions already seeded (%d rows), skipping.", len(existing)
        )
        return

    upsert("competency_dimensions", DIMENSIONS)
    logger.info("Seeded %d competency dimensions.", len(DIMENSIONS))


def seed_scenarios() -> None:
    """Seed the 8 stress scenarios into the scenarios table.

    Each scenario models a plausible BMW operational future with probability,
    capability demand vectors, affected org units, and time horizons.
    Uses fixed UUIDs from _ids.py for idempotent upserts.
    """
    existing = fetch_all("scenarios")
    if len(existing) >= len(SCENARIOS):
        logger.info(
            "Scenarios already seeded (%d rows), skipping.", len(existing)
        )
        return

    upsert("scenarios", SCENARIOS)
    logger.info("Seeded %d stress scenarios.", len(SCENARIOS))


def seed_interaction_rules() -> None:
    """Seed the 32 dimension interaction rules into the interaction_rules table.

    Each rule describes how two competency dimensions interact in a given
    relationship context (hierarchical, peer, cross-functional), including
    whether the effect is complementary, clashing, or groupthink-inducing.
    """
    existing = fetch_all("interaction_rules")
    if len(existing) >= len(INTERACTION_RULES):
        logger.info(
            "Interaction rules already seeded (%d rows), skipping.",
            len(existing),
        )
        return

    upsert("interaction_rules", INTERACTION_RULES)
    logger.info("Seeded %d interaction rules.", len(INTERACTION_RULES))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_dimensions()
    seed_scenarios()
    seed_interaction_rules()
