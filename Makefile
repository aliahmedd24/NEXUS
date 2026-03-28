.PHONY: setup migrate seed test lint run

setup:
	uv sync --all-extras
	cp .env.example .env
	@echo "=== NEXUS Setup ==="
	@echo "1. Create a Supabase project at https://supabase.com/dashboard"
	@echo "2. Fill in .env with your Supabase URL and keys"
	@echo "3. Fill in .env with your GOOGLE_API_KEY"
	@echo "4. Run 'make migrate' to create tables"
	@echo "5. Run 'make seed' to populate synthetic data"
	@echo "6. Run 'make run' to start the API server"

migrate:
	@echo "Run each SQL file in supabase/migrations/ via Supabase Dashboard SQL Editor"
	@echo "Or use: supabase db push (if Supabase CLI is installed)"
	@for f in supabase/migrations/*.sql; do \
		echo "  → $$f"; \
	done

seed:
	uv run python -m db.seed.seed_all

embed:
	uv run python -m db.seed.seed_embeddings

test:
	uv run pytest tests/ -v

lint:
	uv run black src/ tests/ db/ --check
	uv run isort src/ tests/ db/ --check

run:
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
