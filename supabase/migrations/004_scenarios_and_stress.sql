-- NEXUS Migration 004: Scenarios, Vulnerability Assessments, Cascade Impacts

CREATE TABLE IF NOT EXISTS scenarios (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                        VARCHAR(200) NOT NULL,
    category                    VARCHAR(50) NOT NULL
                                CHECK (category IN ('transformation','crisis','market','competitive','regulatory','compound')),
    narrative                   TEXT NOT NULL,
    probability                 FLOAT NOT NULL CHECK (probability BETWEEN 0.0 AND 1.0),
    capability_demand_vector    JSONB NOT NULL,
    affected_org_units          UUID[] DEFAULT '{}',
    time_horizon_months         INTEGER DEFAULT 12,
    compound_of                 UUID[] DEFAULT '{}',
    created_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vulnerability_assessments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id     UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    leader_id       UUID REFERENCES leaders(id) ON DELETE SET NULL,
    gap_score       FLOAT NOT NULL CHECK (gap_score BETWEEN 0.0 AND 1.0),
    status          VARCHAR(10) NOT NULL CHECK (status IN ('green','yellow','red')),
    gap_dimensions  JSONB DEFAULT '{}',
    bench_strength  INTEGER DEFAULT 0 CHECK (bench_strength BETWEEN 0 AND 3),
    assessed_at     TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(scenario_id, role_id)
);

CREATE INDEX IF NOT EXISTS idx_vuln_scenario ON vulnerability_assessments(scenario_id);
CREATE INDEX IF NOT EXISTS idx_vuln_status ON vulnerability_assessments(status);

CREATE TABLE IF NOT EXISTS cascade_impacts (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vulnerability_id            UUID NOT NULL REFERENCES vulnerability_assessments(id) ON DELETE CASCADE,
    cascade_chain               JSONB NOT NULL,
    total_impact_eur            FLOAT DEFAULT 0,
    production_units_lost       INTEGER DEFAULT 0,
    delay_days                  INTEGER DEFAULT 0,
    attrition_risk_increase     FLOAT DEFAULT 0,
    optimal_intervention_point  JSONB,
    created_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cascade_vuln ON cascade_impacts(vulnerability_id);
