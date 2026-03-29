# NEXUS — Neural EXecutive Understanding System

<p align="center">
  <strong>Multi-agent decision intelligence platform for leadership hiring</strong><br>
  Built for the BMW Digital Excellence Hub Hackathon 2026
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white" alt="Python 3.12">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Google%20ADK-1.0-4285F4?logo=google&logoColor=white" alt="Google ADK">
  <img src="https://img.shields.io/badge/Gemini-2.5-8E75B2?logo=google&logoColor=white" alt="Gemini">
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white" alt="Supabase">
  <img src="https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Deploy-Railway-0B0D0E?logo=railway&logoColor=white" alt="Railway">
</p>

---

## The Problem

Filling C-suite and VP-level positions is one of the highest-stakes decisions any organization makes. Traditional hiring relies on gut instinct, static competency checklists, and siloed evaluations. The result: **leadership gaps go undetected until a crisis hits**, biases compound invisibly, and there is no feedback loop to learn from past decisions.

## The Solution

NEXUS stress-tests organizational leadership structures, produces portfolio-optimized staffing recommendations, and learns from past hiring decisions. It coordinates **10 specialized AI agents** across four operational modes:

| Mode | What It Does |
|---|---|
| **DIAGNOSE** | Stress-test leadership against crisis scenarios. Identify vulnerabilities, model cascade failures, and quantify exposure in EUR. Auto-suggests the most relevant scenarios based on industry context. |
| **STAFF** | Fill leadership gaps with scenario-adaptive, team-chemistry-aware, portfolio-optimized recommendations. Includes development pathways for internal upskilling candidates. |
| **LEARN** | Replay past hiring decisions, discover systematic biases (tenure overweighting, rating compression), and calibrate future recommendations. |
| **WHAT-IF** | Ask natural-language questions ("What happens if our VP leaves during the battery crisis?") and get a chained DIAGNOSE -> STAFF -> Brief response in one shot. |

---

## Key Features

- **Conversational What-If** --- Natural-language queries chain multi-agent pipelines automatically
- **12-Dimension Leadership Genome** --- Radar-chart visualization of candidate capabilities across strategic, operational, and interpersonal dimensions
- **Bias Mirror Toggle** --- Side-by-side raw vs. bias-corrected genome radar; exposes halo effect, central tendency, and rating-feedback divergence
- **Cascade Impact Modeling** --- BFS-based failure propagation across org dependency graph; EUR exposure quantification
- **Efficient Frontier Staffing** --- Portfolio theory applied to hiring: budget vs. resilience tradeoff curves
- **Scenario Auto-Suggest** --- Industry-context-aware scenario recommendations
- **Development Pathways** --- Internal candidates get upskilling roadmaps, not just rankings
- **RAG-Powered Search** --- Semantic search over 360-feedback, leader bios, and historical decisions via pgvector embeddings
- **Board-Ready Briefs** --- Gemini Pro generates executive summaries with confidence ratings and dissent reports

---

## Architecture at a Glance

```
                          User (React SPA)
                               |
                        FastAPI (SSE Stream)
                               |
                     Orchestrator Agent (ADK)
                    /          |           \
              DIAGNOSE       STAFF         LEARN
              Pipeline      Pipeline      Pipeline
             (3 agents)   (4 agents)    (2 agents)
                    \          |           /
                     Brief Generator (Pro)
                               |
                    Supabase (PostgreSQL + pgvector)
```

> For the full architecture breakdown, see **[ARCHITECTURE.md](ARCHITECTURE.md)**.

---

## Agents

| Agent | Pipeline | Role | Model |
|---|---|---|---|
| **Orchestrator** | root | Auto-routes user intent to pipelines | Flash |
| Scenario Architect | DIAGNOSE | Design and parameterize crisis scenarios | Flash |
| Vulnerability Scanner | DIAGNOSE | Identify leadership capability gaps | Flash |
| Cascade Modeler | DIAGNOSE | Model failure propagation and EUR exposure | Pro |
| JD Generator | STAFF | Adapt job descriptions to scenario demands | Flash |
| Genome Agent | STAFF | 12-dimension candidate fit analysis (RAG) | Flash |
| Team Chemistry | STAFF | Pairwise compatibility assessment (RAG) | Flash |
| Portfolio Optimizer | STAFF | Efficient frontier staffing plans with ROI | Flash |
| Decision Replay | LEARN | Replay and analyze past hiring decisions | Flash |
| Pattern Intelligence | LEARN | Detect biases and update calibration | Flash |
| **Brief Generator** | output | Board-ready executive summaries | Pro |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, FastAPI, uvicorn |
| **Agent Framework** | Google ADK (Agent Development Kit) |
| **LLM** | Gemini 2.5 Flash (agents) + Gemini 2.5 Pro (briefs, cascade reasoning) |
| **Database** | Supabase (managed PostgreSQL) + pgvector (768-dim embeddings) |
| **Frontend** | React, TypeScript, Vite, Recharts, Supabase JS client |
| **Computation** | NumPy, SciPy (portfolio math, bias correction) |
| **Deployment** | Docker, Railway |
| **Data** | 100% synthetic. GDPR-compliant by design. |

---

## Project Structure

```
NEXUS/
├── src/
│   ├── agents/              # 10 ADK agents organized by pipeline
│   │   ├── agent.py          # Root orchestrator
│   │   ├── prompts.py        # All agent instructions (extracted)
│   │   ├── callbacks.py      # Tool/model callbacks
│   │   ├── diagnose/         # Scenario Architect, Vulnerability Scanner, Cascade Modeler
│   │   ├── staff/            # JD Generator, Genome, Chemistry, Portfolio
│   │   ├── learn/            # Decision Replay, Pattern Intelligence
│   │   └── brief/            # Brief Generator
│   ├── tools/               # 35+ tool functions (pure, typed, documented)
│   │   ├── orchestrator_tools.py
│   │   ├── diagnose_tools.py
│   │   ├── staff_tools.py
│   │   ├── learn_tools.py
│   │   └── brief_tools.py
│   ├── schemas/             # Pydantic models for structured agent outputs
│   ├── services/            # Pure computation (genome, cascade, portfolio, bias)
│   ├── api/                 # FastAPI routes + SSE streaming
│   │   ├── main.py
│   │   └── routes/          # chat, diagnose, staff, learn, what_if, scenarios
│   ├── config.py            # Pydantic Settings (env-based config)
│   ├── supabase_client.py   # Database singleton + semantic search helpers
│   └── embeddings.py        # Gemini embedding generation
├── db/seed/                 # Idempotent synthetic data scripts
├── supabase/migrations/     # 8 numbered SQL migrations (18 tables)
├── frontend/                # React SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── pages/           # DiagnosePage, StaffPage, LearnPage
│   │   ├── components/      # ChatPanel, ArtifactsPanel, ScenarioInjector
│   │   └── lib/             # API client, report generators (Excel/Word)
│   └── dist/                # Production build
├── tests/                   # Unit and integration tests
├── Dockerfile               # Python 3.12-slim + uvicorn
├── railway.json             # Railway deployment config
├── Makefile                 # seed, embed, test, format, lint
└── requirements.txt         # Pinned dependencies
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- A [Supabase](https://supabase.com) project (free tier works)
- A [Google AI](https://ai.google.dev) API key with Gemini access

### Setup

```bash
# 1. Clone and enter
git clone <repo-url> && cd NEXUS

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Supabase URL, keys, and Google API key

# 5. Run database migrations
# Paste each file in supabase/migrations/ into the Supabase SQL Editor
# (or use `supabase db push` if you have the Supabase CLI)

# 6. Seed synthetic data
python -m db.seed.seed_all

# 7. Generate vector embeddings (optional, enables RAG)
python -m db.seed.seed_embeddings

# 8. Start the API server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# 9. Verify
curl http://localhost:8000/health
```

### Docker

```bash
docker build -t nexus .
docker run -p 8000:8000 --env-file .env nexus
```

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check + database connectivity |
| `/api/chat/message` | POST | Core agent execution (SSE streaming) |
| `/api/chat/sessions/{id}` | GET/POST | Session management |
| `/api/scenarios` | GET | Scenario library |
| `/api/scenarios/suggest` | POST | Auto-suggest scenarios by industry context |
| `/api/diagnose` | POST | Standalone vulnerability scan |
| `/api/staff/{role_id}` | POST | Candidate ranking for a specific role |
| `/api/learn` | POST | Bias detection + calibration update |
| `/api/what-if` | POST | Chained DIAGNOSE -> STAFF -> Brief |

---

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_SECRET_KEY` | Supabase secret key (full access, backend) | Yes |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase publishable key (frontend reads) | Yes |
| `GOOGLE_API_KEY` | Google AI / Gemini API key | Yes |
| `GEMINI_MODEL_FAST` | Model for agent calls (default: `gemini-2.0-flash`) | No |
| `GEMINI_MODEL_PRO` | Model for brief generation (default: `gemini-2.0-pro`) | No |
| `LOG_LEVEL` | Logging level (default: `INFO`) | No |

---

## Demo Scenarios

NEXUS ships with 8 pre-built crisis scenarios for BMW:

1. **EV Battery Supply Crisis** --- Critical supplier failure during Neue Klasse ramp-up
2. **Autonomous Driving Regulatory Shift** --- Sudden EU regulation changes
3. **Digital Transformation Acceleration** --- Compressed timeline for software-defined vehicle
4. **Cybersecurity Breach** --- Connected vehicle infrastructure compromise
5. **Market Disruption** --- Chinese EV competitor enters European market
6. **Sustainability Compliance** --- New EU carbon border adjustment mechanism
7. **Talent War** --- Key engineering talent poached by tech companies
8. **Compound Crisis** --- Multiple simultaneous events stress-testing leadership

---

## Planted Biases (for LEARN Pipeline Demo)

The synthetic historical decisions contain intentionally planted biases for NEXUS to discover:

| Bias | What It Looks Like | Detection Method |
|---|---|---|
| **Industry tenure overweighting** | +35% weight on years-in-automotive | Coefficient analysis vs. outcome correlation |
| **Change management underweighting** | -28% weight on transformation skills | Gap between demand and evaluation weight |
| **Rating compression** | All ratings cluster in 7.0--8.2 range | Standard deviation analysis; sentiment divergence |

The **Bias Mirror** toggle in the frontend shows raw vs. corrected genome radar charts side-by-side.

---

## License

Hackathon project --- BMW Digital Excellence Hub 2026.
