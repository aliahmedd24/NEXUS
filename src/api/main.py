"""FastAPI application entry point."""

import logging
import os
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import settings

# Export API key to env BEFORE any agent/genai imports
os.environ.setdefault("GOOGLE_API_KEY", settings.google_api_key)

from src.api.routes import chat, diagnose, learn, scenarios, staff, what_if

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.getLevelNamesMapping().get(settings.log_level.upper(), logging.INFO)
    ),
)

app = FastAPI(
    title="NEXUS — Decision Intelligence for Leadership at Scale",
    description=(
        "Multi-agent AI platform for organizational stress-testing "
        "and leadership staffing at BMW Group."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Route Registration ────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(scenarios.router)
app.include_router(diagnose.router)
app.include_router(staff.router)
app.include_router(learn.router)
app.include_router(what_if.router)


@app.get("/health")
async def health_check():
    """Health check — also verifies Supabase connectivity."""
    from src.supabase_client import get_supabase

    try:
        sb = get_supabase()
        # Quick connectivity test
        sb.table("org_units").select("id").limit(1).execute()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "project": "NEXUS",
        "version": "0.1.0",
        "database": db_status,
    }


# ─── Static Frontend ─────────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React SPA for any non-API route."""
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
