-- NEXUS Migration 003: Leaders, Capability Scores (Genome), Feedback, Performance Reviews

CREATE TABLE IF NOT EXISTS leaders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name           VARCHAR(200) NOT NULL,
    current_role_id     UUID REFERENCES roles(id) ON DELETE SET NULL,
    leader_type         VARCHAR(30) NOT NULL
                        CHECK (leader_type IN ('internal_current','internal_candidate','external_candidate')),
    years_experience    INTEGER NOT NULL DEFAULT 0,
    years_at_bmw        INTEGER DEFAULT 0,
    education_level     VARCHAR(50)
                        CHECK (education_level IN ('bachelors','masters','phd','mba','dual_degree')),
    education_field     VARCHAR(100),
    industry_background TEXT[] DEFAULT '{}',
    location_current    VARCHAR(100),
    location_preference TEXT[] DEFAULT '{}',
    flight_risk         FLOAT DEFAULT 0.1 CHECK (flight_risk BETWEEN 0.0 AND 1.0),
    bio_summary         TEXT,
    metadata            JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE roles ADD CONSTRAINT fk_roles_current_holder
    FOREIGN KEY (current_holder_id) REFERENCES leaders(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_leaders_type ON leaders(leader_type);

CREATE TABLE IF NOT EXISTS leader_capability_scores (
    id                          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leader_id                   UUID NOT NULL REFERENCES leaders(id) ON DELETE CASCADE,
    dimension                   VARCHAR(50) NOT NULL,
    raw_score                   FLOAT NOT NULL CHECK (raw_score BETWEEN 0.0 AND 1.0),
    corrected_score             FLOAT NOT NULL CHECK (corrected_score BETWEEN 0.0 AND 1.0),
    confidence_low              FLOAT NOT NULL CHECK (confidence_low BETWEEN 0.0 AND 1.0),
    confidence_high             FLOAT NOT NULL CHECK (confidence_high BETWEEN 0.0 AND 1.0),
    evidence_sources            TEXT[] DEFAULT '{}',
    bias_corrections_applied    JSONB DEFAULT '{}',
    assessed_at                 TIMESTAMPTZ DEFAULT NOW(),
    assessor_type               VARCHAR(30) DEFAULT 'composite'
                                CHECK (assessor_type IN (
                                    'self','manager','peer','direct_report',
                                    'assessment_center','ai_extracted','composite'
                                )),
    UNIQUE(leader_id, dimension, assessor_type)
);

CREATE INDEX IF NOT EXISTS idx_cap_leader ON leader_capability_scores(leader_id);
CREATE INDEX IF NOT EXISTS idx_cap_dimension ON leader_capability_scores(dimension);

CREATE TABLE IF NOT EXISTS feedback_360 (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leader_id       UUID NOT NULL REFERENCES leaders(id) ON DELETE CASCADE,
    feedback_text   TEXT NOT NULL,
    feedback_type   VARCHAR(30) NOT NULL
                    CHECK (feedback_type IN (
                        'peer_review','direct_report','manager',
                        'self','interview_note','reference_check'
                    )),
    feedback_period VARCHAR(20),
    sentiment_score FLOAT CHECK (sentiment_score BETWEEN -1.0 AND 1.0),
    extracted_traits JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_leader ON feedback_360(leader_id);

CREATE TABLE IF NOT EXISTS performance_reviews (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    leader_id               UUID NOT NULL REFERENCES leaders(id) ON DELETE CASCADE,
    review_period           VARCHAR(20) NOT NULL,
    overall_rating          FLOAT NOT NULL CHECK (overall_rating BETWEEN 1.0 AND 10.0),
    goal_completion_pct     FLOAT CHECK (goal_completion_pct BETWEEN 0 AND 100),
    reviewer_id             UUID REFERENCES leaders(id),
    review_narrative        TEXT,
    team_engagement_score   FLOAT CHECK (team_engagement_score BETWEEN 0.0 AND 1.0),
    team_attrition_rate     FLOAT CHECK (team_attrition_rate BETWEEN 0.0 AND 1.0),
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(leader_id, review_period)
);

CREATE INDEX IF NOT EXISTS idx_reviews_leader ON performance_reviews(leader_id);
