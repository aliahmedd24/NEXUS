# NEXUS Architecture

This document describes the system architecture of NEXUS, a multi-agent decision intelligence platform built on Google ADK, FastAPI, and Supabase.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Frontend (React SPA)                         │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ ChatPanel   │  │ ArtifactsPanel│  │ Visualizations│  │ Exports   │ │
│  │ (SSE stream)│  │ (report cards)│  │ (Recharts)    │  │ (Excel/   │ │
│  │             │  │              │  │              │  │  Word)    │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └───────────┘ │
│         │                │                │                          │
│         │         Supabase JS (direct reads)                        │
└─────────┼────────────────┼────────────────┼──────────────────────────┘
          │                │                │
          │ SSE            │ REST           │ Realtime
          ▼                ▼                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Python 3.12)                    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    API Layer (src/api/)                          │ │
│  │  /api/chat/message   POST  Core SSE streaming endpoint          │ │
│  │  /api/diagnose       POST  Standalone vulnerability scan        │ │
│  │  /api/staff/:id      POST  Candidate ranking                    │ │
│  │  /api/learn          POST  Bias detection + calibration         │ │
│  │  /api/what-if        POST  Chained pipeline execution           │ │
│  │  /api/scenarios      GET   Scenario library                     │ │
│  └─────────────────────────┬───────────────────────────────────────┘ │
│                            │                                         │
│  ┌─────────────────────────▼───────────────────────────────────────┐ │
│  │                 Agent Layer (Google ADK)                         │ │
│  │                                                                  │ │
│  │                  ┌──────────────────┐                            │ │
│  │                  │   Orchestrator   │                            │ │
│  │                  │  (Auto-Router)   │                            │ │
│  │                  └───┬──────┬───┬───┘                            │ │
│  │                ┌─────┘      │   └──────┐                        │ │
│  │                ▼            ▼          ▼                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │ │
│  │  │   DIAGNOSE   │  │    STAFF     │  │    LEARN     │           │ │
│  │  │  Sequential  │  │  Sequential  │  │  Sequential  │           │ │
│  │  │   Pipeline   │  │   Pipeline   │  │   Pipeline   │           │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘           │ │
│  │          │                │                │                     │ │
│  │          └────────────────┼────────────────┘                     │ │
│  │                           ▼                                      │ │
│  │                  ┌──────────────────┐                            │ │
│  │                  │ Brief Generator  │                            │ │
│  │                  │  (Gemini Pro)    │                            │ │
│  │                  └──────────────────┘                            │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐ │
│  │   Tools Layer    │  │  Services Layer  │  │  Schemas Layer     │ │
│  │  (35+ functions) │  │ (pure compute)   │  │ (Pydantic models)  │ │
│  └────────┬─────────┘  └──────────────────┘  └────────────────────┘ │
│           │                                                          │
│  ┌────────▼─────────────────────────────────────────────────────────┐│
│  │              Supabase Client (src/supabase_client.py)            ││
│  │              + Semantic Search (pgvector RPC calls)              ││
│  └─────────────────────────┬───────────────────────────────────────┘│
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  Supabase (Managed PostgreSQL)                       │
│                                                                      │
│  18 tables  |  pgvector (768-dim)  |  4 IVFFlat indexes             │
│  3 RPC functions (match_feedback, match_leaders, match_decisions)    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Agent Architecture

NEXUS uses the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) to orchestrate 10 specialized LLM agents across three pipelines. The ADK provides session state management, structured output enforcement, and agent composition primitives.

### Design Principles

1. **Agent-Tool Separation** --- Agents reason and decide; tools fetch and compute. Tools are pure functions with no LLM logic.
2. **Structured Outputs** --- Every agent produces a Pydantic-validated `output_schema`. This guarantees downstream agents and the frontend receive predictable data.
3. **Session State Chaining** --- Each agent writes its output to an `output_key` in ADK session state. Downstream agents read upstream results via `callback_context.state.get()`.
4. **LLM-Reasoned Outputs** --- Agents generate their own assessments (gap analyses, demand vectors, EUR estimates) rather than copying tool outputs verbatim. Tools provide data; agents provide judgment.

### Agent Composition

ADK provides three composition primitives used throughout NEXUS:

| Primitive | Usage in NEXUS |
|---|---|
| **LlmAgent** | Each individual agent (Scenario Architect, Genome Agent, etc.) |
| **SequentialAgent** | Pipelines --- agents execute in order, each reading the prior agent's output |
| **ParallelAgent** | STAFF pipeline runs Genome Agent and Team Chemistry concurrently |

### Pipeline Details

#### DIAGNOSE Pipeline (Sequential)

```
Scenario Architect ──► Vulnerability Scanner ──► Cascade Modeler
      │                        │                       │
      ▼                        ▼                       ▼
  scenario_id             heatmap (R/Y/G)        cascade chains
  demand_vector           resilience_score        EUR exposure
  narrative               gap_assessments         units_at_risk
```

**Flow:**
1. **Scenario Architect** selects or creates a crisis scenario, generating a capability demand vector (12 dimensions) and narrative summary.
2. **Vulnerability Scanner** compares the demand vector against current leadership capability scores. Produces a RED/YELLOW/GREEN heatmap and identifies single points of failure.
3. **Cascade Modeler** (Gemini Pro) traces failure propagation through the org dependency graph using BFS. Estimates operational cost exposure in EUR for each affected unit.

#### STAFF Pipeline (Sequential + Parallel)

```
JD Generator ──► ┌─ Genome Agent ────┐ ──► Portfolio Optimizer
                 │                    │
                 └─ Team Chemistry ──┘
                     (parallel)
```

**Flow:**
1. **JD Generator** adapts a job description template to the specific scenario demands identified by DIAGNOSE. Includes a self-critique loop.
2. **Genome Agent** + **Team Chemistry** run in parallel:
   - Genome Agent scores candidates across 12 dimensions using capability data + RAG-powered 360-feedback search. Applies bias correction (halo effect, central tendency).
   - Team Chemistry computes pairwise compatibility scores between each candidate and the existing team using interaction rules and feedback patterns.
3. **Portfolio Optimizer** combines genome fit scores, chemistry scores, and cost data to generate efficient frontier staffing plans. Produces development pathways for promising internal candidates.

#### LEARN Pipeline (Sequential)

```
Decision Replay ──► Pattern Intelligence
      │                     │
      ▼                     ▼
  decision analysis     bias patterns
  counterfactuals       calibration updates
  analogous cases       success DNA
```

**Flow:**
1. **Decision Replay** retrieves historical hiring decisions and analyzes outcomes. Simulates counterfactuals ("what if we hired the runner-up?") and finds analogous past decisions via semantic search.
2. **Pattern Intelligence** aggregates replay findings to detect systematic biases (tenure overweighting, rating compression). Updates calibration coefficients that feed back into STAFF pipeline scoring.

#### Brief Generator

The Brief Generator (Gemini Pro) synthesizes outputs from any pipeline into a board-ready executive summary. It surfaces dissenting data points, computes a confidence rating, and structures the output for executive consumption.

---

## Data Architecture

### Database Schema (18 Tables)

```
┌─────────────────────────────────────────────────────────┐
│                   Organizational Layer                   │
│  org_units (14)  ←──→  org_dependencies (22)            │
│  Types: group, division, brand, plant, dept, program    │
│  Dependencies: production_flow, quality_gate, supply    │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    People Layer                          │
│  competency_dimensions (12)                              │
│  jd_templates (8)  →  roles (10, 2 vacant)              │
│  leaders (23)  →  leader_capability_scores (276)         │
│                →  feedback_360 (31)                       │
│                →  performance_reviews (23)                │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                  Analysis Layer                          │
│  scenarios (8)  →  vulnerability_assessments             │
│                 →  cascade_impacts                        │
│  interaction_rules (32)  →  compatibility_assessments    │
│  historical_decisions (8)  →  decision_outcomes (17)     │
│                            →  counterfactual_results     │
│  calibration_coefficients                                │
│  staffing_plans  →  staffing_plan_items                  │
│  decision_audit_log                                      │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                   Vector Layer (pgvector)                 │
│  embeddings (768-dim, Gemini embedding-001)              │
│  Types: feedback (31), leader_bio (8), decision (8)      │
│  Indexes: 4 IVFFlat indexes                              │
│  RPC: match_feedback, match_leaders, match_decisions     │
└─────────────────────────────────────────────────────────┘
```

### Data Conventions

- All tables use `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` and `created_at TIMESTAMPTZ DEFAULT NOW()`
- JSONB fields store flexible structures (capability vectors, genome dimensions); validated by Pydantic before insert
- All database access goes through `src/supabase_client.py` (singleton pattern) --- no raw SQL in application code
- Seed data uses fixed UUIDs for idempotent upserts

### Semantic Search (RAG)

NEXUS uses pgvector for retrieval-augmented generation across three domains:

| RPC Function | Searches Over | Used By |
|---|---|---|
| `match_feedback` | 360-feedback entries | Genome Agent (trait-based search) |
| `match_leaders` | Leader bios/profiles | Genome Agent (find similar leaders) |
| `match_decisions` | Historical decision reasoning | Decision Replay (analogous cases) |

Embeddings are generated using `Gemini embedding-001` (768 dimensions) and stored with content type metadata for filtered retrieval.

---

## Computation Layer

The `src/services/` directory contains pure computation functions with no database or LLM dependencies. These are called by tools and are independently testable.

| Service | Purpose | Key Algorithm |
|---|---|---|
| `genome_computation.py` | Weighted fit scoring, bias correction | Halo effect detection (dimension range < 0.5), central tendency expansion (stdev < 0.5 -> 1.3x spread) |
| `cascade_engine.py` | Failure propagation modeling | BFS traversal of org dependency graph with depth-limited cascade chains |
| `compatibility_engine.py` | Pairwise team chemistry | Interaction rule matching with weighted scoring across collaboration dimensions |
| `portfolio_math.py` | Efficient frontier computation | Greedy knapsack: rank (role, candidate) pairs by resilience/cost, compute frontier across budget levels |
| `bias_correction.py` | Systematic bias detection | Rating-feedback sentiment divergence, coefficient drift analysis |
| `scenario_engine.py` | Scenario parameterization | Demand vector generation, probability estimation |

---

## Frontend Architecture

The frontend is a React SPA built with Vite and TypeScript, communicating with both FastAPI (agent pipelines) and Supabase (direct reads for sub-500ms loads).

### Data Channels

| Channel | Purpose | Latency Profile |
|---|---|---|
| **FastAPI SSE** | Agent pipeline execution, streaming results | Seconds (LLM inference) |
| **Supabase JS** | Static data reads (scenarios, candidates, leaders) | < 500ms |
| **Supabase Realtime** | Live updates when agents write results | Real-time push |

### Visualizations

| Component | Library | Data Source |
|---|---|---|
| Vulnerability Heatmap | Recharts | Vulnerability Scanner output |
| Cascade Impact Chain | Custom SVG | Cascade Modeler output |
| Genome Radar Chart | Recharts (RadarChart) | Genome Agent output (raw + bias-corrected toggle) |
| Team Chemistry Matrix | Recharts (custom) | Team Chemistry output |
| Portfolio Efficient Frontier | Recharts (ScatterChart) | Portfolio Optimizer output |
| Decision Timeline | Custom | Decision Replay output |

### Export Capabilities

- **Excel** --- Multi-sheet workbooks with all pipeline outputs (`lib/reportGenerators/excelGenerator.ts`)
- **Word** --- Formatted executive briefs (`lib/reportGenerators/wordGenerator.ts`)

---

## Deployment Architecture

### Docker

```dockerfile
FROM python:3.12-slim
# Single-stage build: requirements.txt -> pip install -> copy src + frontend dist
# Serves both API and SPA from the same container
CMD uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

### Railway

Railway hosts the Docker container with environment variables injected at runtime. Configuration in `railway.json`:

- Builder: Dockerfile
- Restart policy: on-failure (max 3 retries)
- Port: set via `$PORT` environment variable

### Infrastructure Dependencies

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Railway    │     │    Supabase      │     │   Google AI      │
│  (compute)   │────▶│  (PostgreSQL +   │     │  (Gemini API)    │
│              │     │   pgvector +     │     │                  │
│  FastAPI +   │     │   Auth +         │     │  Flash (agents)  │
│  React SPA   │     │   Realtime)      │     │  Pro (briefs)    │
│              │     │                  │     │  Embeddings      │
└──────────────┘     └──────────────────┘     └──────────────────┘
```

---

## Request Flow

A typical WHAT-IF query flows through the system as follows:

```
1. User types: "What if our VP Engineering leaves during the battery crisis?"
   │
2. Frontend POST /api/chat/message (SSE stream opens)
   │
3. Orchestrator classifies intent → routes to DIAGNOSE pipeline
   │
4. Scenario Architect
   ├── Tool: get_scenario_library() → finds "EV Battery Supply Crisis"
   ├── Tool: get_scenario_by_name("ev_battery_supply_crisis")
   ├── LLM reasons: generates demand vector [strategic: 0.9, crisis: 0.95, ...]
   └── Output → session_state["scenario_analysis"]
   │
5. Vulnerability Scanner
   ├── Reads: session_state["scenario_analysis"]
   ├── Tool: scan_vulnerabilities(scenario_id, demand_vector)
   ├── LLM reasons: assesses each gap as RED/YELLOW/GREEN
   └── Output → session_state["vulnerability_report"]
   │
6. Cascade Modeler
   ├── Reads: session_state["vulnerability_report"]
   ├── Tool: compute_cascade_impact(vulnerable_units)
   ├── LLM reasons: estimates EUR exposure per cascade node
   └── Output → session_state["cascade_report"]
   │
7. Orchestrator chains to STAFF pipeline (auto-flow)
   │
8. STAFF agents execute (JD → Genome||Chemistry → Portfolio)
   │
9. Brief Generator synthesizes all outputs into executive summary
   │
10. SSE stream delivers structured events to frontend
    ├── Visualization data (heatmaps, radar charts, frontier)
    ├── Agent reasoning (narrative explanations)
    └── Final brief (board-ready summary)
```

---

## Security Considerations

| Aspect | Current (Hackathon) | Production Recommendation |
|---|---|---|
| **Data** | 100% synthetic | Enable RLS, anonymize real data pipelines |
| **Auth** | None | Supabase Auth + JWT verification |
| **RLS** | Disabled | Enable per-table policies (secret key backend, publishable key frontend) |
| **API Keys** | `.env` file | Secret manager (Railway encrypted vars, Supabase vault) |
| **CORS** | Open | Restrict to known frontend origins |
| **Rate Limiting** | None | Add per-user rate limits on agent endpoints |

---

## File Reference

| Path | Purpose |
|---|---|
| `src/agents/agent.py` | Root orchestrator definition |
| `src/agents/prompts.py` | All agent instruction prompts (78 KB) |
| `src/agents/callbacks.py` | ADK callbacks (validation, logging, output formatting) |
| `src/agents/{diagnose,staff,learn,brief}/agent.py` | Pipeline agent definitions |
| `src/tools/*.py` | Tool functions organized by pipeline |
| `src/services/*.py` | Pure computation (no DB/LLM dependencies) |
| `src/schemas/*.py` | Pydantic models for agent I/O |
| `src/api/routes/chat.py` | Core SSE streaming endpoint (ADK runner) |
| `src/api/routes/what_if.py` | Chained DIAGNOSE -> STAFF -> Brief |
| `src/config.py` | Environment configuration (Pydantic Settings) |
| `src/supabase_client.py` | Database client singleton + semantic search |
| `db/seed/*.py` | Synthetic data generation (idempotent) |
| `supabase/migrations/*.sql` | Database schema migrations |
