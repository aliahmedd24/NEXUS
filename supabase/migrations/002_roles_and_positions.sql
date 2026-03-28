-- NEXUS Migration 002: Competency Dimensions, JD Templates, Roles

CREATE TABLE IF NOT EXISTS competency_dimensions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key         VARCHAR(50) UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category    VARCHAR(30) NOT NULL
                CHECK (category IN ('cognitive','interpersonal','execution','domain','character')),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS jd_templates (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_type                   VARCHAR(100) UNIQUE NOT NULL,
    base_description            TEXT NOT NULL,
    competency_weightings       JSONB NOT NULL,
    min_experience_years        INTEGER DEFAULT 10,
    typical_compensation_range  JSONB,
    typical_time_to_fill_days   INTEGER DEFAULT 90,
    created_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               VARCHAR(200) NOT NULL,
    role_level          VARCHAR(30) NOT NULL
                        CHECK (role_level IN ('c_suite','svp','vp','director','senior_manager')),
    org_unit_id         UUID NOT NULL REFERENCES org_units(id) ON DELETE CASCADE,
    jd_template_id      UUID REFERENCES jd_templates(id),
    is_filled           BOOLEAN DEFAULT TRUE,
    current_holder_id   UUID,   -- FK added in migration 003
    reports_to_role_id  UUID REFERENCES roles(id) ON DELETE SET NULL,
    criticality         VARCHAR(20) DEFAULT 'high'
                        CHECK (criticality IN ('critical','high','medium')),
    vacancy_date        DATE,
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_roles_org_unit ON roles(org_unit_id);
CREATE INDEX IF NOT EXISTS idx_roles_filled ON roles(is_filled);
