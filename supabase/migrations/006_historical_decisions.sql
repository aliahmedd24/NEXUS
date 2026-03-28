-- NEXUS Migration 006: Historical Decisions, Outcomes, Counterfactuals, Calibration

CREATE TABLE IF NOT EXISTS historical_decisions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id                 UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    decision_date           DATE NOT NULL,
    scenario_at_decision    VARCHAR(200),
    selected_candidate_id   UUID NOT NULL REFERENCES leaders(id),
    runner_up_candidate_id  UUID REFERENCES leaders(id),
    decision_criteria_used  JSONB DEFAULT '{}',
    decision_reasoning      TEXT,
    decision_maker_id       UUID,
    time_to_fill_days       INTEGER,
    cost_of_hire_eur        FLOAT,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS decision_outcomes (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id             UUID NOT NULL REFERENCES historical_decisions(id) ON DELETE CASCADE,
    months_elapsed          INTEGER NOT NULL CHECK (months_elapsed IN (6,12,18,24)),
    performance_rating      FLOAT CHECK (performance_rating BETWEEN 1.0 AND 10.0),
    goal_completion_pct     FLOAT CHECK (goal_completion_pct BETWEEN 0 AND 100),
    team_engagement_delta   FLOAT,
    team_attrition_delta    FLOAT,
    project_delivery_score  FLOAT CHECK (project_delivery_score BETWEEN 0.0 AND 1.0),
    still_in_role           BOOLEAN NOT NULL DEFAULT TRUE,
    departure_reason        VARCHAR(100),
    assessed_at             TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(decision_id, months_elapsed)
);

CREATE TABLE IF NOT EXISTS counterfactual_results (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id                 UUID NOT NULL REFERENCES historical_decisions(id) ON DELETE CASCADE,
    alternative_candidate_id    UUID NOT NULL REFERENCES leaders(id),
    simulated_outcome           JSONB NOT NULL,
    divergence_score            FLOAT NOT NULL CHECK (divergence_score BETWEEN 0.0 AND 1.0),
    divergence_category         VARCHAR(20) NOT NULL
                                CHECK (divergence_category IN ('optimal','suboptimal','costly_error','critical_miss')),
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(decision_id, alternative_candidate_id)
);

CREATE TABLE IF NOT EXISTS calibration_coefficients (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dimension           VARCHAR(50) UNIQUE NOT NULL,
    historical_overweight FLOAT DEFAULT 0,
    correction_factor   FLOAT NOT NULL DEFAULT 1.0,
    evidence_count      INTEGER DEFAULT 0,
    confidence          FLOAT DEFAULT 0.5 CHECK (confidence BETWEEN 0.0 AND 1.0),
    last_updated        TIMESTAMPTZ DEFAULT NOW()
);
