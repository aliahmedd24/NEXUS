"""Master seeder — runs all seeders in dependency order. Idempotent."""

import logging

from db.seed.seed_candidates import seed_candidates
from db.seed.seed_embeddings import seed_all_embeddings
from db.seed.seed_historical_decisions import seed_historical_decisions
from db.seed.seed_leaders import seed_jd_templates, seed_leaders, seed_roles
from db.seed.seed_org_units import seed_org_dependencies, seed_org_units
from db.seed.seed_scenarios import seed_dimensions, seed_interaction_rules, seed_scenarios

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def seed_all() -> None:
    """Run all seeders in dependency order."""
    logger.info("═══ NEXUS Data Seeding ═══")

    # Tier 1: No dependencies
    seed_dimensions()  # competency_dimensions
    seed_org_units()  # org_units

    # Tier 2: Depends on tier 1
    seed_org_dependencies()  # org_dependencies (needs org_units)
    seed_jd_templates()  # jd_templates (needs competency_dimensions)
    seed_scenarios()  # scenarios (needs org_units for affected_org_units)
    seed_interaction_rules()  # interaction_rules (needs competency_dimensions)

    # Tier 3: Depends on tier 2
    seed_roles()  # roles (needs org_units + jd_templates)

    # Tier 4: Depends on tier 3
    seed_leaders()  # leaders + capability_scores + feedback + reviews (needs roles)
    seed_candidates()  # additional leaders as candidates

    # Tier 5: Depends on tier 4
    seed_historical_decisions()  # historical_decisions + outcomes (needs leaders + roles)

    # Tier 6: Embeddings (depends on ALL text data being seeded)
    seed_all_embeddings()

    logger.info("═══ Seeding Complete (with embeddings) ═══")


if __name__ == "__main__":
    seed_all()
