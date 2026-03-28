"""FastAPI application entry point."""

import logging

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

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
