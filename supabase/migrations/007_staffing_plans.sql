-- NEXUS Migration 007: Staffing Plans, Plan Items, Audit Log

CREATE TABLE IF NOT EXISTS staffing_plans (
    id                                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                                VARCHAR(200) NOT NULL,
    scenario_id                         UUID REFERENCES scenarios(id),
    total_budget_eur                    FLOAT,
    roles_count                         INTEGER DEFAULT 0,
    aggregate_resilience_improvement    FLOAT DEFAULT 0,
    roi_estimate                        JSONB DEFAULT '{}',
    plan_status                         VARCHAR(20) DEFAULT 'draft'
                                        CHECK (plan_status IN ('draft','recommended','approved','executing')),
    efficient_frontier_data             JSONB DEFAULT '[]',
    created_at                          TIMESTAMPTZ DEFAULT NOW(),
    updated_at                          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staffing_plan_items (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id                 UUID NOT NULL REFERENCES staffing_plans(id) ON DELETE CASCADE,
    role_id                 UUID NOT NULL REFERENCES roles(id),
    priority_rank           INTEGER NOT NULL,
    sourcing_strategy       VARCHAR(30) NOT NULL
                            CHECK (sourcing_strategy IN (
                                'internal_promote','external_hire','interim_bridge',
                                'develop_internal','accept_risk','restructure_role'
                            )),
    recommended_candidate_id UUID REFERENCES leaders(id),
    alternative_candidate_id UUID REFERENCES leaders(id),
    estimated_cost_eur      FLOAT DEFAULT 0,
    estimated_time_days     INTEGER DEFAULT 90,
    sequence_dependency     UUID REFERENCES staffing_plan_items(id),
    confidence              FLOAT DEFAULT 0.5 CHECK (confidence BETWEEN 0.0 AND 1.0),
    risk_factors            TEXT[] DEFAULT '{}',
    rationale               TEXT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_plan_items_plan ON staffing_plan_items(plan_id);

CREATE TABLE IF NOT EXISTS decision_audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL,
    agent_name      VARCHAR(100) NOT NULL,
    action_type     VARCHAR(50) NOT NULL,
    input_summary   TEXT,
    output_summary  TEXT,
    user_override   BOOLEAN DEFAULT FALSE,
    override_detail TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_session ON decision_audit_log(session_id);
