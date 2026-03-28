-- ============================================================================
-- NEXUS — Synthetic Data Schema
-- BMW Digital Excellence Hub Hackathon 2026
-- Run this FIRST to create all tables before seeding data
-- ============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 3.1 — ORGANIZATIONAL STRUCTURE
-- ============================================================================

CREATE TABLE IF NOT EXISTS org_units (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    unit_type       VARCHAR(50) NOT NULL,
    parent_id       UUID REFERENCES org_units(id),
    location_city   VARCHAR(100),
    location_country VARCHAR(3),
    employee_count  INTEGER,
    strategic_priority VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS org_dependencies (
    id              UUID PRIMARY KEY,
    upstream_unit_id UUID REFERENCES org_units(id) NOT NULL,
    downstream_unit_id UUID REFERENCES org_units(id) NOT NULL,
    dependency_type VARCHAR(50) NOT NULL,
    coupling_strength FLOAT NOT NULL,
    description     TEXT
);

-- ============================================================================
-- 3.2 — LEADERSHIP ROLES & POSITIONS
-- ============================================================================

-- Forward-declare leaders table for circular reference
CREATE TABLE IF NOT EXISTS leaders (
    id              UUID PRIMARY KEY,
    full_name       VARCHAR(200) NOT NULL,
    current_role_id UUID,
    leader_type     VARCHAR(20) NOT NULL,
    years_experience INTEGER,
    years_at_bmw    INTEGER,
    education_level VARCHAR(50),
    industry_background VARCHAR(100)[],
    location_preference VARCHAR(100)[],
    flight_risk     FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id              UUID PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    role_level      VARCHAR(30) NOT NULL,
    org_unit_id     UUID REFERENCES org_units(id) NOT NULL,
    is_filled       BOOLEAN DEFAULT TRUE,
    current_holder_id UUID REFERENCES leaders(id),
    reports_to_role_id UUID REFERENCES roles(id),
    criticality     VARCHAR(20) DEFAULT 'high',
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Add FK from leaders to roles after both exist
ALTER TABLE leaders ADD CONSTRAINT fk_leaders_current_role
    FOREIGN KEY (current_role_id) REFERENCES roles(id);

CREATE TABLE IF NOT EXISTS jd_templates (
    id              UUID PRIMARY KEY,
    role_type       VARCHAR(100) NOT NULL,
    base_description TEXT NOT NULL,
    competency_weightings JSONB NOT NULL,
    min_experience_years INTEGER,
    typical_compensation_range JSONB,
    typical_time_to_fill_days INTEGER,
    version         INTEGER DEFAULT 1
);

-- ============================================================================
-- 3.3 — LEADERS & CANDIDATES (Leadership Genome)
-- ============================================================================

CREATE TABLE IF NOT EXISTS leader_capability_scores (
    id              UUID PRIMARY KEY,
    leader_id       UUID REFERENCES leaders(id) NOT NULL,
    dimension       VARCHAR(50) NOT NULL,
    raw_score       FLOAT NOT NULL,
    corrected_score FLOAT NOT NULL,
    confidence_low  FLOAT NOT NULL,
    confidence_high FLOAT NOT NULL,
    evidence_sources TEXT[],
    bias_corrections_applied JSONB,
    assessed_at     TIMESTAMP NOT NULL,
    assessor_type   VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS feedback_360 (
    id              UUID PRIMARY KEY,
    leader_id       UUID REFERENCES leaders(id) NOT NULL,
    feedback_text   TEXT NOT NULL,
    feedback_type   VARCHAR(30) NOT NULL,
    feedback_period VARCHAR(20),
    sentiment_score FLOAT,
    extracted_traits JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_reviews (
    id              UUID PRIMARY KEY,
    leader_id       UUID REFERENCES leaders(id) NOT NULL,
    review_period   VARCHAR(20) NOT NULL,
    overall_rating  FLOAT NOT NULL,
    goal_completion_pct FLOAT,
    reviewer_id     UUID,
    review_narrative TEXT,
    team_engagement_score FLOAT,
    team_attrition_rate FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 3.4 — SCENARIOS & STRESS TESTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS scenarios (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    category        VARCHAR(50) NOT NULL,
    narrative       TEXT NOT NULL,
    probability     FLOAT NOT NULL,
    capability_demand_vector JSONB NOT NULL,
    affected_org_units UUID[],
    time_horizon_months INTEGER,
    compound_of     UUID[],
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vulnerability_assessments (
    id              UUID PRIMARY KEY,
    scenario_id     UUID REFERENCES scenarios(id) NOT NULL,
    role_id         UUID REFERENCES roles(id) NOT NULL,
    leader_id       UUID REFERENCES leaders(id),
    gap_score       FLOAT NOT NULL,
    status          VARCHAR(10) NOT NULL,
    gap_dimensions  JSONB,
    bench_strength  INTEGER,
    assessed_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cascade_impacts (
    id              UUID PRIMARY KEY,
    vulnerability_id UUID REFERENCES vulnerability_assessments(id) NOT NULL,
    cascade_chain   JSONB NOT NULL,
    total_impact_eur FLOAT,
    production_units_lost INTEGER,
    delay_days      INTEGER,
    attrition_risk_increase FLOAT,
    optimal_intervention_point JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 3.5 — TEAM CHEMISTRY & COMPATIBILITY
-- ============================================================================

CREATE TABLE IF NOT EXISTS interaction_rules (
    id              UUID PRIMARY KEY,
    dimension_a     VARCHAR(50) NOT NULL,
    dimension_b     VARCHAR(50) NOT NULL,
    relationship_type VARCHAR(20) NOT NULL,
    interaction_effect VARCHAR(20) NOT NULL,
    effect_magnitude FLOAT NOT NULL,
    description     TEXT
);

CREATE TABLE IF NOT EXISTS compatibility_assessments (
    id              UUID PRIMARY KEY,
    leader_a_id     UUID REFERENCES leaders(id) NOT NULL,
    leader_b_id     UUID REFERENCES leaders(id) NOT NULL,
    relationship_type VARCHAR(20) NOT NULL,
    synergy_score   FLOAT NOT NULL,
    friction_dimensions VARCHAR(50)[],
    synergy_dimensions VARCHAR(50)[],
    groupthink_risk FLOAT,
    assessed_at     TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 3.6 — HISTORICAL DECISIONS & LEARNING
-- ============================================================================

CREATE TABLE IF NOT EXISTS historical_decisions (
    id              UUID PRIMARY KEY,
    role_id         UUID REFERENCES roles(id) NOT NULL,
    decision_date   DATE NOT NULL,
    scenario_at_decision VARCHAR(200),
    selected_candidate_id UUID REFERENCES leaders(id) NOT NULL,
    runner_up_candidate_id UUID REFERENCES leaders(id),
    decision_criteria_used JSONB,
    decision_reasoning TEXT,
    decision_maker_id UUID,
    time_to_fill_days INTEGER,
    cost_of_hire_eur FLOAT,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS decision_outcomes (
    id              UUID PRIMARY KEY,
    decision_id     UUID REFERENCES historical_decisions(id) NOT NULL,
    months_elapsed  INTEGER NOT NULL,
    performance_rating FLOAT,
    goal_completion_pct FLOAT,
    team_engagement_delta FLOAT,
    team_attrition_delta FLOAT,
    project_delivery_score FLOAT,
    still_in_role   BOOLEAN NOT NULL,
    departure_reason VARCHAR(100),
    assessed_at     TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS counterfactual_results (
    id              UUID PRIMARY KEY,
    decision_id     UUID REFERENCES historical_decisions(id) NOT NULL,
    alternative_candidate_id UUID REFERENCES leaders(id) NOT NULL,
    simulated_outcome JSONB NOT NULL,
    divergence_score FLOAT NOT NULL,
    divergence_category VARCHAR(20) NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS calibration_coefficients (
    id              UUID PRIMARY KEY,
    dimension       VARCHAR(50) NOT NULL,
    historical_overweight FLOAT,
    correction_factor FLOAT NOT NULL,
    evidence_count  INTEGER,
    confidence      FLOAT,
    last_updated    TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 3.7 — STAFFING PLANS & PORTFOLIO OPTIMIZATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS staffing_plans (
    id              UUID PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    scenario_id     UUID REFERENCES scenarios(id),
    total_budget_eur FLOAT,
    roles_count     INTEGER,
    aggregate_resilience_improvement FLOAT,
    roi_estimate    JSONB,
    plan_status     VARCHAR(20) DEFAULT 'draft',
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staffing_plan_items (
    id              UUID PRIMARY KEY,
    plan_id         UUID REFERENCES staffing_plans(id) NOT NULL,
    role_id         UUID REFERENCES roles(id) NOT NULL,
    priority_rank   INTEGER NOT NULL,
    sourcing_strategy VARCHAR(30) NOT NULL,
    recommended_candidate_id UUID REFERENCES leaders(id),
    estimated_cost_eur FLOAT,
    estimated_time_days INTEGER,
    sequence_dependency UUID REFERENCES staffing_plan_items(id),
    confidence      FLOAT,
    risk_factors    TEXT[],
    created_at      TIMESTAMP DEFAULT NOW()
);
