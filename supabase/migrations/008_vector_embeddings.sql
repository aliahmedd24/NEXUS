-- NEXUS Migration 008: pgvector Extension + Embedding Columns
-- Enables semantic search across unstructured leadership data.

-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Add embedding columns to existing tables
-- Using 768 dimensions (Gemini text-embedding-004 output size)

ALTER TABLE feedback_360
    ADD COLUMN IF NOT EXISTS embedding VECTOR(768);

ALTER TABLE performance_reviews
    ADD COLUMN IF NOT EXISTS embedding VECTOR(768);

ALTER TABLE leaders
    ADD COLUMN IF NOT EXISTS bio_embedding VECTOR(768);

ALTER TABLE historical_decisions
    ADD COLUMN IF NOT EXISTS reasoning_embedding VECTOR(768);

-- Step 3: Create RPC functions for vector similarity search
-- Supabase JS/Python clients call these via .rpc()

-- Search feedback_360 by semantic similarity
CREATE OR REPLACE FUNCTION match_feedback(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.5,
    match_count INT DEFAULT 5,
    filter_leader_id UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    leader_id UUID,
    feedback_text TEXT,
    feedback_type VARCHAR(30),
    feedback_period VARCHAR(20),
    sentiment_score FLOAT,
    extracted_traits JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.leader_id,
        f.feedback_text,
        f.feedback_type,
        f.feedback_period,
        f.sentiment_score,
        f.extracted_traits,
        1 - (f.embedding <=> query_embedding) AS similarity
    FROM feedback_360 f
    WHERE f.embedding IS NOT NULL
        AND (filter_leader_id IS NULL OR f.leader_id = filter_leader_id)
        AND 1 - (f.embedding <=> query_embedding) > match_threshold
    ORDER BY f.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Search leaders by bio similarity
CREATE OR REPLACE FUNCTION match_leaders(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.4,
    match_count INT DEFAULT 5,
    exclude_leader_id UUID DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    full_name VARCHAR(200),
    leader_type VARCHAR(30),
    bio_summary TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.id,
        l.full_name,
        l.leader_type,
        l.bio_summary,
        1 - (l.bio_embedding <=> query_embedding) AS similarity
    FROM leaders l
    WHERE l.bio_embedding IS NOT NULL
        AND (exclude_leader_id IS NULL OR l.id != exclude_leader_id)
        AND 1 - (l.bio_embedding <=> query_embedding) > match_threshold
    ORDER BY l.bio_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Search historical decisions by reasoning similarity
CREATE OR REPLACE FUNCTION match_decisions(
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.4,
    match_count INT DEFAULT 3
)
RETURNS TABLE (
    id UUID,
    role_id UUID,
    decision_date DATE,
    scenario_at_decision VARCHAR(200),
    selected_candidate_id UUID,
    runner_up_candidate_id UUID,
    decision_reasoning TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.role_id,
        d.decision_date,
        d.scenario_at_decision,
        d.selected_candidate_id,
        d.runner_up_candidate_id,
        d.decision_reasoning,
        1 - (d.reasoning_embedding <=> query_embedding) AS similarity
    FROM historical_decisions d
    WHERE d.reasoning_embedding IS NOT NULL
        AND 1 - (d.reasoning_embedding <=> query_embedding) > match_threshold
    ORDER BY d.reasoning_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
