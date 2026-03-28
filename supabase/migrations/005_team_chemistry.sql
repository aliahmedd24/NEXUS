-- NEXUS Migration 005: Interaction Rules, Compatibility Assessments

CREATE TABLE IF NOT EXISTS interaction_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dimension_a         VARCHAR(50) NOT NULL,
    dimension_b         VARCHAR(50) NOT NULL,
    relationship_type   VARCHAR(20) NOT NULL
                        CHECK (relationship_type IN ('cross_functional','hierarchical','peer')),
    interaction_effect  VARCHAR(30) NOT NULL
                        CHECK (interaction_effect IN ('complementary_positive','clash_negative','overlap_groupthink')),
    effect_magnitude    FLOAT NOT NULL CHECK (effect_magnitude BETWEEN 0.0 AND 1.0),
    description         TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(dimension_a, dimension_b, relationship_type)
);

CREATE TABLE IF NOT EXISTS compatibility_assessments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leader_a_id         UUID NOT NULL REFERENCES leaders(id) ON DELETE CASCADE,
    leader_b_id         UUID NOT NULL REFERENCES leaders(id) ON DELETE CASCADE,
    relationship_type   VARCHAR(20) NOT NULL
                        CHECK (relationship_type IN ('cross_functional','hierarchical','peer')),
    synergy_score       FLOAT NOT NULL CHECK (synergy_score BETWEEN -1.0 AND 1.0),
    friction_dimensions TEXT[] DEFAULT '{}',
    synergy_dimensions  TEXT[] DEFAULT '{}',
    groupthink_risk     FLOAT DEFAULT 0 CHECK (groupthink_risk BETWEEN 0.0 AND 1.0),
    detail              JSONB DEFAULT '{}',
    assessed_at         TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(leader_a_id, leader_b_id, relationship_type)
);

CREATE INDEX IF NOT EXISTS idx_compat_a ON compatibility_assessments(leader_a_id);
CREATE INDEX IF NOT EXISTS idx_compat_b ON compatibility_assessments(leader_b_id);
