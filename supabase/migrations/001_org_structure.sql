-- NEXUS Migration 001: Organizational Structure
-- Tables: org_units, org_dependencies

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS org_units (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(200) NOT NULL,
    unit_type           VARCHAR(50) NOT NULL
                        CHECK (unit_type IN ('group','division','brand','plant','department','program','team')),
    parent_id           UUID REFERENCES org_units(id) ON DELETE SET NULL,
    location_city       VARCHAR(100),
    location_country    VARCHAR(3),
    employee_count      INTEGER DEFAULT 0,
    strategic_priority  VARCHAR(50) DEFAULT 'steady_state'
                        CHECK (strategic_priority IN ('transformation','steady_state','ramp_up','wind_down','greenfield')),
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_org_units_parent ON org_units(parent_id);
CREATE INDEX IF NOT EXISTS idx_org_units_type ON org_units(unit_type);

CREATE TABLE IF NOT EXISTS org_dependencies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upstream_unit_id    UUID NOT NULL REFERENCES org_units(id) ON DELETE CASCADE,
    downstream_unit_id  UUID NOT NULL REFERENCES org_units(id) ON DELETE CASCADE,
    dependency_type     VARCHAR(50) NOT NULL
                        CHECK (dependency_type IN (
                            'production_flow','quality_gate','supply_chain',
                            'reporting','shared_resource','talent_pipeline','budget'
                        )),
    coupling_strength   FLOAT NOT NULL CHECK (coupling_strength BETWEEN 0.0 AND 1.0),
    description         TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(upstream_unit_id, downstream_unit_id, dependency_type)
);

CREATE INDEX IF NOT EXISTS idx_org_deps_upstream ON org_dependencies(upstream_unit_id);
CREATE INDEX IF NOT EXISTS idx_org_deps_downstream ON org_dependencies(downstream_unit_id);
