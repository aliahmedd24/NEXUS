# NEXUS — Neural EXecutive Understanding System

> Multi-agent decision intelligence platform for leadership hiring at BMW Group.
> BMW Digital Excellence Hub Hackathon 2026.

## Overview

NEXUS stress-tests organizational leadership structures, produces portfolio-optimized staffing recommendations, and learns from past hiring decisions. It operates in four modes:

- **DIAGNOSE** — Stress-test leadership against crisis scenarios. Identify vulnerabilities and model cascade impacts. Auto-suggests the most relevant scenarios based on industry context.
- **STAFF** — Fill leadership gaps with scenario-adaptive, team-chemistry-aware, portfolio-optimized recommendations. Includes development pathways for internal upskilling candidates.
- **LEARN** — Replay past hiring decisions, discover systematic biases, and calibrate future recommendations.
- **WHAT-IF** — Ask natural-language questions ("What happens if our VP leaves during the battery crisis?") and get a chained DIAGNOSE → STAFF → Brief response in one shot.

## Architecture

- **Backend:** Python 3.11+, FastAPI, Google ADK (Agent Development Kit)
- **Database:** Supabase (managed PostgreSQL + pgvector for RAG)
- **LLM:** Gemini 2.5 Flash (agents) + Gemini 2.5 Pro (executive briefs)
- **Frontend:** React / Recharts / Supabase JS client
- **Key Features:** Conversational what-if, bias mirror toggle, scenario auto-suggest, development pathways
- **Data:** 100% synthetic. GDPR-compliant by design.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Fill in SUPABASE_URL, SUPABASE_SECRET_KEY, SUPABASE_PUBLISHABLE_KEY, GOOGLE_API_KEY

# 3. Run database migrations
# Paste each file in supabase/migrations/ into the Supabase SQL Editor

# 4. Seed synthetic data
python -m db.seed.seed_all

# 5. Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 6. Verify
curl http://localhost:8000/health
```

## Project Structure

```
src/
├── agents/          # 10 ADK agents (Orchestrator + 3 pipelines)
├── tools/           # Tool functions called by agents
├── schemas/         # Pydantic models for API I/O and agent outputs
├── services/        # Pure computation (genome, cascade, portfolio, etc.)
├── api/             # FastAPI routes
├── config.py        # Environment-based configuration
└── supabase_client.py  # Database access singleton
db/seed/             # Synthetic data seed scripts
supabase/migrations/ # SQL migration files
tests/               # Unit and integration tests
```

## Agents

| Agent | Pipeline | Role |
|---|---|---|
| Orchestrator | root | Auto-Flow routing to pipelines |
| Scenario Architect | DIAGNOSE | Design crisis scenarios |
| Vulnerability Scanner | DIAGNOSE | Identify leadership gaps |
| Cascade Modeler | DIAGNOSE | Model failure propagation |
| JD Generator | STAFF | Adapt job descriptions to scenarios |
| Genome Agent | STAFF | 12-dimension leadership genome analysis |
| Team Chemistry | STAFF | Pairwise compatibility assessment |
| Portfolio Optimizer | STAFF | Efficient frontier staffing plans |
| Decision Replay | LEARN | Replay and analyze past decisions |
| Pattern Intelligence | LEARN | Detect systematic biases |

## License

Hackathon project — BMW Digital Excellence Hub 2026.
