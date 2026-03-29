"""Supabase client singleton.

All database access in NEXUS goes through this module.
Uses the secret key for full backend access.
"""

from supabase import Client, create_client

from src.config import settings

# Singleton client — reused across all requests
_client: Client | None = None


def get_supabase() -> Client:
    """Get or create the Supabase client singleton.

    Returns:
        Authenticated Supabase client with secret key permissions.
    """
    global _client
    if _client is None:
        _client = create_client(
            settings.supabase_url,
            settings.supabase_secret_key,
        )
    return _client


# ─── Convenience query helpers ───────────────────────────────────────────


def fetch_all(table: str, filters: dict | None = None) -> list[dict]:
    """Fetch all rows from a table with optional filters.

    Args:
        table: Table name.
        filters: Optional dict of {column: value} equality filters.

    Returns:
        List of row dicts.
    """
    sb = get_supabase()
    query = sb.table(table).select("*")
    if filters:
        for col, val in filters.items():
            query = query.eq(col, val)
    result = query.execute()
    return result.data


def fetch_one(table: str, id: str) -> dict | None:
    """Fetch a single row by UUID id.

    Args:
        table: Table name.
        id: UUID string.

    Returns:
        Row dict or None if not found.
    """
    sb = get_supabase()
    result = sb.table(table).select("*").eq("id", id).maybe_single().execute()
    if result is None:
        return None
    return result.data


def fetch_by_column(table: str, column: str, value: str) -> list[dict]:
    """Fetch rows matching a column value.

    Args:
        table: Table name.
        column: Column name to filter on.
        value: Value to match.

    Returns:
        List of matching row dicts.
    """
    sb = get_supabase()
    result = sb.table(table).select("*").eq(column, value).execute()
    return result.data


def fetch_ilike(table: str, column: str, pattern: str) -> list[dict]:
    """Fetch rows where column matches a case-insensitive pattern.

    Args:
        table: Table name.
        column: Column name.
        pattern: ILIKE pattern (use % for wildcards).

    Returns:
        List of matching row dicts.
    """
    sb = get_supabase()
    result = sb.table(table).select("*").ilike(column, pattern).execute()
    return result.data


def upsert(table: str, data: dict | list[dict]) -> list[dict]:
    """Insert or update rows (upsert on primary key).

    Args:
        table: Table name.
        data: Single dict or list of dicts to upsert.

    Returns:
        Upserted row(s).
    """
    sb = get_supabase()
    if isinstance(data, dict):
        data = [data]
    result = sb.table(table).upsert(data).execute()
    return result.data


def insert(table: str, data: dict | list[dict]) -> list[dict]:
    """Insert new rows.

    Args:
        table: Table name.
        data: Single dict or list of dicts.

    Returns:
        Inserted row(s).
    """
    sb = get_supabase()
    if isinstance(data, dict):
        data = [data]
    result = sb.table(table).insert(data).execute()
    return result.data


# ─── Semantic Search Helpers (pgvector) ─────────────────────────────────


def semantic_search_feedback(
    query_embedding: list[float],
    top_k: int = 5,
    threshold: float = 0.5,
    leader_id: str | None = None,
) -> list[dict]:
    """Search feedback_360 by semantic similarity.

    Uses the match_feedback RPC function in Supabase (pgvector cosine similarity).

    Args:
        query_embedding: 768-dim embedding vector of the search query.
        top_k: Maximum results to return.
        threshold: Minimum cosine similarity (0.0-1.0).
        leader_id: Optional — restrict search to one leader's feedback.

    Returns:
        List of matching feedback entries with similarity scores, sorted by relevance.
    """
    sb = get_supabase()
    params: dict = {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": top_k,
    }
    if leader_id:
        params["filter_leader_id"] = leader_id

    result = sb.rpc("match_feedback", params).execute()
    return result.data


def semantic_search_leaders(
    query_embedding: list[float],
    top_k: int = 5,
    threshold: float = 0.4,
    exclude_id: str | None = None,
) -> list[dict]:
    """Search leaders by bio_summary semantic similarity.

    Args:
        query_embedding: 768-dim embedding vector.
        top_k: Maximum results.
        threshold: Minimum similarity.
        exclude_id: Optional leader ID to exclude (e.g., the query leader themselves).

    Returns:
        List of similar leaders with similarity scores.
    """
    sb = get_supabase()
    params: dict = {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": top_k,
    }
    if exclude_id:
        params["exclude_leader_id"] = exclude_id

    result = sb.rpc("match_leaders", params).execute()
    return result.data


def semantic_search_decisions(
    query_embedding: list[float],
    top_k: int = 3,
    threshold: float = 0.4,
) -> list[dict]:
    """Search historical decisions by reasoning similarity.

    Args:
        query_embedding: 768-dim embedding vector.
        top_k: Maximum results.
        threshold: Minimum similarity.

    Returns:
        List of analogous past decisions with similarity scores.
    """
    sb = get_supabase()
    result = sb.rpc("match_decisions", {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": top_k,
    }).execute()
    return result.data
