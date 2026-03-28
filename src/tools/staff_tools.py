"""Semantic search tools for the STAFF agent cluster.

Provides RAG-powered retrieval tools for the Genome Agent and
Team Chemistry Engine to find relevant feedback and similar leaders
by meaning rather than keyword matching.
"""

from src.embeddings import embed_query
from src.supabase_client import (
    fetch_one,
    semantic_search_feedback,
    semantic_search_leaders,
)


def search_feedback_by_trait(
    trait_query: str, leader_id: str = "", top_k: int = 5
) -> list[dict]:
    """Semantically search 360 feedback for passages relevant to a specific trait.

    Unlike exact keyword matching, this finds feedback by MEANING. For example,
    searching "crisis leadership under pressure" will find feedback like
    "she stayed calm when the supplier defaulted and rallied the team in 48 hours"
    even though none of the search keywords appear.

    Use this to:
    - Find evidence for specific genome dimensions across candidates
    - Discover contradictions between numeric ratings and qualitative feedback
    - Compare how different leaders handle similar challenges

    Args:
        trait_query: Natural language description of the trait or capability to
            search for. Examples: "crisis leadership under pressure",
            "poor delegation and micromanagement".
        leader_id: Optional UUID to restrict search to one leader's feedback.
            Leave empty to search across ALL leaders.
        top_k: Number of results to return (default 5).

    Returns:
        List of matching feedback entries with: leader_id, feedback_text,
        feedback_type, sentiment_score, and similarity score (0.0-1.0).
    """
    query_vector = embed_query(trait_query)
    results = semantic_search_feedback(
        query_embedding=query_vector,
        top_k=top_k,
        threshold=0.45,
        leader_id=leader_id if leader_id else None,
    )

    # Enrich with leader names
    for r in results:
        leader = fetch_one("leaders", r["leader_id"])
        r["leader_name"] = leader["full_name"] if leader else "Unknown"

    return results


def find_similar_leaders(leader_id: str, top_k: int = 5) -> list[dict]:
    """Find leaders with similar experience profiles based on bio narrative similarity.

    Uses semantic embedding similarity on leader bio_summary fields. This captures
    experience patterns that structured dimension scores might miss — for example,
    two leaders who both led factory ramp-ups in different industries would surface
    as similar even if their genome scores differ.

    Use this to:
    - Discover non-obvious internal candidates with analogous experience
    - Find external candidates whose background narrative matches an internal benchmark
    - Identify leaders who could mentor or shadow for development

    Args:
        leader_id: UUID of the reference leader to find similar profiles for.
        top_k: Number of similar leaders to return (default 5).

    Returns:
        List of similar leaders with: full_name, leader_type, bio_summary,
        and similarity score (0.0-1.0).
    """
    leader = fetch_one("leaders", leader_id)
    if not leader or not leader.get("bio_summary"):
        return [{"error": f"Leader {leader_id} has no bio summary to compare."}]

    query_vector = embed_query(leader["bio_summary"])
    return semantic_search_leaders(
        query_embedding=query_vector,
        top_k=top_k,
        threshold=0.35,
        exclude_id=leader_id,
    )
