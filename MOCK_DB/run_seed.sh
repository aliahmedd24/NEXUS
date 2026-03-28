#!/bin/bash
# ============================================================================
# NEXUS — Master Seed Data Runner
# Executes all SQL files in the correct order to populate the database.
#
# Usage:
#   chmod +x run_seed.sh
#   ./run_seed.sh [DATABASE_URL]
#
# Default: postgresql://localhost:5432/nexus
# ============================================================================

DB_URL="${1:-postgresql://localhost:5432/nexus}"

echo "=========================================="
echo "NEXUS — Seeding Database"
echo "Target: $DB_URL"
echo "=========================================="

FILES=(
    "00_schema.sql"
    "01_org_structure.sql"
    "02_leaders_and_roles.sql"
    "03_jd_templates.sql"
    "04_leadership_genomes.sql"
    "05_scenarios.sql"
    "06_feedback_360.sql"
    "07_performance_reviews.sql"
    "08_interaction_rules.sql"
    "09_historical_decisions.sql"
    "10_vulnerability_and_cascades.sql"
    "11_counterfactuals_and_compatibility.sql"
)

for file in "${FILES[@]}"; do
    echo ""
    echo "--- Running: $file ---"
    psql "$DB_URL" -f "$file"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed on $file. Aborting."
        exit 1
    fi
    echo "    ✓ $file complete"
done

echo ""
echo "=========================================="
echo "NEXUS seed data loaded successfully!"
echo "=========================================="
echo ""
echo "Data Summary:"
echo "  - 13 org units (BMW Group structure)"
echo "  - 12 org dependencies (cascade graph)"
echo "  - 10 leadership roles (2 vacant)"
echo "  - 24 leaders/candidates (8 current + 6 internal + 10 external)"
echo "  - 8 historical-only leaders"
echo "  - 288 leadership genome scores (12 dimensions × 24 profiles)"
echo "  - 8 JD templates"
echo "  - 8 scenarios (including 1 compound)"
echo "  - 24 feedback entries (360°)"
echo "  - 18 performance reviews"
echo "  - 15 interaction rules"
echo "  - 10 historical decisions"
echo "  - 28 decision outcomes"
echo "  - 12 calibration coefficients"
echo "  - 18 vulnerability assessments (2 scenarios)"
echo "  - 5 cascade impact chains"
echo "  - 5 counterfactual results"
echo "  - 15 compatibility assessments"
echo ""
