# NEXUS — Claude Code Governance

## Project Identity
NEXUS (Neural EXecutive Understanding System) — A multi-agent decision intelligence
platform for leadership hiring at BMW Group. Built for the BMW Digital Excellence Hub
Hackathon 2026.

## Architecture
- **Backend:** Python 3.11+, FastAPI, Google ADK (Agent Development Kit)
- **Database:** Supabase (managed PostgreSQL + Auth + Realtime + REST API)
- **LLM:** Gemini 2.5 Flash (agent calls) + Gemini 2.5 Pro (brief generation)
- **Frontend:** Lovable (prototype) + React/Recharts (visualizations) + Supabase JS client
- **Data:** 100% synthetic. No real personal data. GDPR-compliant by design.

## Phase Rules
- **Never skip phases.** Each phase has acceptance criteria. Do not begin Phase N+1
  until Phase N passes all criteria.
- **Phase containment:** Only modify files listed in the current phase spec.
  Cross-phase edits require explicit approval.
- **Append-only LOG.md:** After completing each phase, append a summary to LOG.md
  with: phase number, completion timestamp, files created/modified, any deviations.

## Code Conventions
- **Python style:** Black formatter, 88-char line width, isort for imports.
- **Type hints:** Required on all function signatures. Use Pydantic for data validation.
- **Docstrings:** Google-style. Required on all public functions and classes.
- **Naming:** snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants.
- **No print statements:** Use structlog for all logging.
- **Error handling:** Never bare `except:`. Always catch specific exceptions.

## Database Rules (Supabase)
- **Migrations are numbered SQL files** in `supabase/migrations/`. Run via Supabase Dashboard
  SQL Editor or `supabase db push` (if using Supabase CLI).
- **All tables have `id UUID PRIMARY KEY DEFAULT gen_random_uuid()` and
  `created_at TIMESTAMPTZ DEFAULT NOW()`.**
- **JSONB fields** are used for flexible data (capability vectors, genome dimensions).
  Always validate JSONB structure via Pydantic before insert.
- **Database access** uses the `supabase-py` client — never raw SQL in application code.
  All queries go through `src/supabase_client.py`.
- **Seed data** is Python scripts in `db/seed/`. They must be idempotent (use upsert).
- **Row Level Security (RLS)** is disabled for this hackathon prototype. In production,
  enable RLS with secret key for backend and publishable key for frontend read-only access.

## Agent Development Rules
- **Each agent is a Google ADK `LlmAgent`** with:
  - A precise `instruction` string (the agent's identity/persona).
  - A list of registered `tools` (Python functions with docstrings + type hints).
  - A defined `output_key` to store results in ADK session state.
- **Tools are pure functions.** They query Supabase, compute scores, or call services.
  Tools do NOT contain LLM logic — that belongs in the agent's instruction.
- **Agent <-> Tool separation is strict.** Agents reason and decide. Tools fetch and compute.
- **Every tool function MUST have a docstring** — ADK uses it as the tool description.
- **Every tool function MUST have type-hinted parameters** — ADK uses them for schemas.

## Testing Rules
- **Every service function must have unit tests.**
- **Agent tests use mocked LLM responses** — never call the real Gemini API in tests.
- **Supabase tests use the same Supabase instance** with test-specific data prefixes.

## Environment Variables (required in .env)
- `SUPABASE_URL` — Supabase project URL (https://xxxx.supabase.co)
- `SUPABASE_SECRET_KEY` — Supabase secret key (full access, backend only)
- `SUPABASE_PUBLISHABLE_KEY` — Supabase publishable key (read-only, used by frontend)
- `GOOGLE_API_KEY` — Gemini API key
- `GEMINI_MODEL_FAST` — Model for agent calls (default: gemini-2.0-flash)
- `GEMINI_MODEL_PRO` — Model for brief generation (default: gemini-2.0-pro)
- `LOG_LEVEL` — Logging level (default: INFO)
