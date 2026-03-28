"""Seed script for org_units and org_dependencies tables.

Populates the BMW Group organizational hierarchy (14 units) and
inter-unit dependencies (22 edges) used by NEXUS scenario modeling.
"""

import logging

from db.seed._ids import (
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
)
from src.supabase_client import fetch_all, upsert

logger = logging.getLogger(__name__)

# ── Org Unit Data (14 units) ────────────────────────────────────────────────

ORG_UNITS: list[dict] = [
    {
        "id": OU_GROUP,
        "name": "BMW Group",
        "unit_type": "group",
        "parent_id": None,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 159000,
        "strategic_priority": "transformation",
    },
    {
        "id": OU_AUTO,
        "name": "Automotive Division",
        "unit_type": "division",
        "parent_id": OU_GROUP,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 142000,
        "strategic_priority": "transformation",
    },
    {
        "id": OU_NK,
        "name": "Neue Klasse Program",
        "unit_type": "program",
        "parent_id": OU_GROUP,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 3500,
        "strategic_priority": "ramp_up",
    },
    {
        "id": OU_MUNICH,
        "name": "Plant Munich",
        "unit_type": "plant",
        "parent_id": OU_AUTO,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 6500,
        "strategic_priority": "transformation",
    },
    {
        "id": OU_DINGOLFING,
        "name": "Plant Dingolfing",
        "unit_type": "plant",
        "parent_id": OU_AUTO,
        "location_city": "Dingolfing",
        "location_country": "DEU",
        "employee_count": 18000,
        "strategic_priority": "steady_state",
    },
    {
        "id": OU_SPARTANBURG,
        "name": "Plant Spartanburg",
        "unit_type": "plant",
        "parent_id": OU_AUTO,
        "location_city": "Spartanburg",
        "location_country": "USA",
        "employee_count": 12000,
        "strategic_priority": "steady_state",
    },
    {
        "id": OU_DEBRECEN,
        "name": "Plant Debrecen (iFactory)",
        "unit_type": "plant",
        "parent_id": OU_AUTO,
        "location_city": "Debrecen",
        "location_country": "HUN",
        "employee_count": 2500,
        "strategic_priority": "greenfield",
    },
    {
        "id": OU_LANDSHUT,
        "name": "Plant Landshut",
        "unit_type": "plant",
        "parent_id": OU_AUTO,
        "location_city": "Landshut",
        "location_country": "DEU",
        "employee_count": 3800,
        "strategic_priority": "ramp_up",
    },
    {
        "id": OU_SUPPLYCHAIN,
        "name": "Supply Chain EMEA",
        "unit_type": "department",
        "parent_id": OU_AUTO,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 4200,
        "strategic_priority": "steady_state",
    },
    {
        "id": OU_ITDIGITAL,
        "name": "IT & Digital (iFACTORY)",
        "unit_type": "department",
        "parent_id": OU_GROUP,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 8500,
        "strategic_priority": "transformation",
    },
    {
        "id": OU_QUALITY,
        "name": "Quality Central",
        "unit_type": "department",
        "parent_id": OU_AUTO,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 2800,
        "strategic_priority": "steady_state",
    },
    {
        "id": OU_HR,
        "name": "HR Central",
        "unit_type": "department",
        "parent_id": OU_GROUP,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 1500,
        "strategic_priority": "steady_state",
    },
    {
        "id": OU_EVBATTERY,
        "name": "EV Battery Systems",
        "unit_type": "department",
        "parent_id": OU_NK,
        "location_city": "Straskirchen",
        "location_country": "DEU",
        "employee_count": 700,
        "strategic_priority": "ramp_up",
    },
    {
        "id": OU_FIZ,
        "name": "R&D FIZ",
        "unit_type": "department",
        "parent_id": OU_GROUP,
        "location_city": "Munich",
        "location_country": "DEU",
        "employee_count": 12000,
        "strategic_priority": "steady_state",
    },
]

# ── Org Dependency Data (22 edges) ──────────────────────────────────────────

_DEP_PREFIX = "21000000-0000-4000-a000-0000000000"

ORG_DEPENDENCIES: list[dict] = [
    {
        "id": f"{_DEP_PREFIX}01",
        "upstream_unit_id": OU_MUNICH,
        "downstream_unit_id": OU_DINGOLFING,
        "dependency_type": "production_flow",
        "coupling_strength": 0.85,
        "description": "Munich body-in-white feeds Dingolfing final assembly",
    },
    {
        "id": f"{_DEP_PREFIX}02",
        "upstream_unit_id": OU_DINGOLFING,
        "downstream_unit_id": OU_SPARTANBURG,
        "dependency_type": "production_flow",
        "coupling_strength": 0.45,
        "description": "Dingolfing supplies drivetrain components to Spartanburg",
    },
    {
        "id": f"{_DEP_PREFIX}03",
        "upstream_unit_id": OU_MUNICH,
        "downstream_unit_id": OU_QUALITY,
        "dependency_type": "quality_gate",
        "coupling_strength": 0.90,
        "description": "Munich production must pass Quality Central gate reviews",
    },
    {
        "id": f"{_DEP_PREFIX}04",
        "upstream_unit_id": OU_DINGOLFING,
        "downstream_unit_id": OU_QUALITY,
        "dependency_type": "quality_gate",
        "coupling_strength": 0.85,
        "description": "Dingolfing production subject to Quality Central audits",
    },
    {
        "id": f"{_DEP_PREFIX}05",
        "upstream_unit_id": OU_SPARTANBURG,
        "downstream_unit_id": OU_QUALITY,
        "dependency_type": "quality_gate",
        "coupling_strength": 0.80,
        "description": "Spartanburg quality metrics reported to Quality Central",
    },
    {
        "id": f"{_DEP_PREFIX}06",
        "upstream_unit_id": OU_SUPPLYCHAIN,
        "downstream_unit_id": OU_MUNICH,
        "dependency_type": "supply_chain",
        "coupling_strength": 0.90,
        "description": "Supply Chain EMEA manages inbound logistics for Munich",
    },
    {
        "id": f"{_DEP_PREFIX}07",
        "upstream_unit_id": OU_SUPPLYCHAIN,
        "downstream_unit_id": OU_DINGOLFING,
        "dependency_type": "supply_chain",
        "coupling_strength": 0.95,
        "description": "Supply Chain EMEA coordinates Dingolfing JIT deliveries",
    },
    {
        "id": f"{_DEP_PREFIX}08",
        "upstream_unit_id": OU_SUPPLYCHAIN,
        "downstream_unit_id": OU_SPARTANBURG,
        "dependency_type": "supply_chain",
        "coupling_strength": 0.70,
        "description": "Supply Chain EMEA handles transatlantic parts for Spartanburg",
    },
    {
        "id": f"{_DEP_PREFIX}09",
        "upstream_unit_id": OU_SUPPLYCHAIN,
        "downstream_unit_id": OU_LANDSHUT,
        "dependency_type": "supply_chain",
        "coupling_strength": 0.75,
        "description": "Supply Chain EMEA supplies raw materials to Landshut",
    },
    {
        "id": f"{_DEP_PREFIX}10",
        "upstream_unit_id": OU_AUTO,
        "downstream_unit_id": OU_GROUP,
        "dependency_type": "reporting",
        "coupling_strength": 0.90,
        "description": "Automotive Division reports financials to BMW Group board",
    },
    {
        "id": f"{_DEP_PREFIX}11",
        "upstream_unit_id": OU_NK,
        "downstream_unit_id": OU_GROUP,
        "dependency_type": "reporting",
        "coupling_strength": 0.85,
        "description": "Neue Klasse program reports milestones to BMW Group board",
    },
    {
        "id": f"{_DEP_PREFIX}12",
        "upstream_unit_id": OU_ITDIGITAL,
        "downstream_unit_id": OU_MUNICH,
        "dependency_type": "shared_resource",
        "coupling_strength": 0.75,
        "description": "IT & Digital provides MES and iFACTORY platform to Munich",
    },
    {
        "id": f"{_DEP_PREFIX}13",
        "upstream_unit_id": OU_ITDIGITAL,
        "downstream_unit_id": OU_DINGOLFING,
        "dependency_type": "shared_resource",
        "coupling_strength": 0.70,
        "description": "IT & Digital manages Dingolfing digital twin infrastructure",
    },
    {
        "id": f"{_DEP_PREFIX}14",
        "upstream_unit_id": OU_ITDIGITAL,
        "downstream_unit_id": OU_DEBRECEN,
        "dependency_type": "shared_resource",
        "coupling_strength": 0.90,
        "description": "IT & Digital builds greenfield iFACTORY stack for Debrecen",
    },
    {
        "id": f"{_DEP_PREFIX}15",
        "upstream_unit_id": OU_HR,
        "downstream_unit_id": OU_AUTO,
        "dependency_type": "talent_pipeline",
        "coupling_strength": 0.65,
        "description": "HR Central manages leadership pipeline for Automotive",
    },
    {
        "id": f"{_DEP_PREFIX}16",
        "upstream_unit_id": OU_HR,
        "downstream_unit_id": OU_NK,
        "dependency_type": "talent_pipeline",
        "coupling_strength": 0.80,
        "description": "HR Central fast-tracks talent acquisition for Neue Klasse",
    },
    {
        "id": f"{_DEP_PREFIX}17",
        "upstream_unit_id": OU_GROUP,
        "downstream_unit_id": OU_AUTO,
        "dependency_type": "budget",
        "coupling_strength": 0.95,
        "description": "BMW Group allocates annual budget to Automotive Division",
    },
    {
        "id": f"{_DEP_PREFIX}18",
        "upstream_unit_id": OU_GROUP,
        "downstream_unit_id": OU_NK,
        "dependency_type": "budget",
        "coupling_strength": 0.90,
        "description": "BMW Group funds Neue Klasse strategic investment program",
    },
    {
        "id": f"{_DEP_PREFIX}19",
        "upstream_unit_id": OU_NK,
        "downstream_unit_id": OU_EVBATTERY,
        "dependency_type": "budget",
        "coupling_strength": 0.85,
        "description": "Neue Klasse program funds EV Battery Systems R&D",
    },
    {
        "id": f"{_DEP_PREFIX}20",
        "upstream_unit_id": OU_FIZ,
        "downstream_unit_id": OU_EVBATTERY,
        "dependency_type": "shared_resource",
        "coupling_strength": 0.70,
        "description": "R&D FIZ shares test facilities with EV Battery Systems",
    },
    {
        "id": f"{_DEP_PREFIX}21",
        "upstream_unit_id": OU_MUNICH,
        "downstream_unit_id": OU_QUALITY,
        "dependency_type": "reporting",
        "coupling_strength": 0.55,
        "description": "Munich plant submits weekly quality KPIs to Quality Central",
    },
    {
        "id": f"{_DEP_PREFIX}22",
        "upstream_unit_id": OU_ITDIGITAL,
        "downstream_unit_id": OU_LANDSHUT,
        "dependency_type": "shared_resource",
        "coupling_strength": 0.60,
        "description": "IT & Digital deploys lightweight MES to Landshut plant",
    },
]


def seed_org_units(dry_run: bool = False) -> None:
    """Seed the org_units table with 14 BMW Group organizational units.

    Checks whether data already exists before inserting. If rows are present
    and ``dry_run`` is False, the function skips seeding. When ``dry_run``
    is True, it logs what would be inserted without writing to the database.

    Args:
        dry_run: If True, log planned inserts without writing to Supabase.
    """
    existing = fetch_all("org_units")
    if existing and not dry_run:
        logger.info(
            "org_units already seeded (%d rows), skipping.", len(existing)
        )
        return

    if dry_run:
        for unit in ORG_UNITS:
            logger.info("[DRY RUN] Would upsert org_unit: %s", unit["name"])
        return

    logger.info("Seeding %d org_units ...", len(ORG_UNITS))
    upsert("org_units", ORG_UNITS)
    logger.info("org_units seeded successfully.")


def seed_org_dependencies(dry_run: bool = False) -> None:
    """Seed the org_dependencies table with 22 inter-unit dependency edges.

    Covers all seven dependency types: production_flow, quality_gate,
    supply_chain, reporting, shared_resource, talent_pipeline, and budget.

    Args:
        dry_run: If True, log planned inserts without writing to Supabase.
    """
    existing = fetch_all("org_dependencies")
    if existing and not dry_run:
        logger.info(
            "org_dependencies already seeded (%d rows), skipping.",
            len(existing),
        )
        return

    if dry_run:
        for dep in ORG_DEPENDENCIES:
            logger.info(
                "[DRY RUN] Would upsert org_dependency: %s (%s)",
                dep["id"],
                dep["dependency_type"],
            )
        return

    logger.info("Seeding %d org_dependencies ...", len(ORG_DEPENDENCIES))
    upsert("org_dependencies", ORG_DEPENDENCIES)
    logger.info("org_dependencies seeded successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_org_units()
    seed_org_dependencies()
