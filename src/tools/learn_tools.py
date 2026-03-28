"""Semantic search tools for the LEARN agent cluster.

Provides RAG-powered retrieval for the Decision Replay Agent to find
past hiring decisions most analogous to a current vacancy context.
"""

from src.embeddings import embed_query
from src.supabase_client import fetch_one, semantic_search_decisions


def find_analogous_decisions(
    context_description: str, top_k: int = 3
) -> list[dict]:
    """Find past hiring decisions most similar to a current vacancy context.

    Instead of replaying ALL historical decisions sequentially, this tool
    retrieves only the most analogous past decisions based on semantic
    similarity of the decision reasoning and context.

    Use this to:
    - Find historical precedents for the current hiring decision
    - Learn from past decisions made in similar circumstances
    - Identify patterns: "the last 3 times we hired for a similar context,
      we overweighted X"

    Args:
        context_description: Natural language description of the current vacancy
            context. Example: "Hiring a VP Production for a plant transitioning
            from ICE to full EV manufacturing, with 6500 employees and active
            construction on site."
        top_k: Number of analogous decisions to return (default 3).

    Returns:
        List of similar past decisions with: role_title, decision_date,
        scenario_at_decision, decision_reasoning, selected_candidate_name,
        and similarity score.
    """
    query_vector = embed_query(context_description)
    results = semantic_search_decisions(
        query_embedding=query_vector,
        top_k=top_k,
        threshold=0.35,
    )

    # Enrich with role titles and candidate names
    for r in results:
        role = fetch_one("roles", r["role_id"])
        r["role_title"] = role["title"] if role else "Unknown"
        selected = fetch_one("leaders", r["selected_candidate_id"])
        r["selected_candidate_name"] = (
            selected["full_name"] if selected else "Unknown"
        )
        if r.get("runner_up_candidate_id"):
            runner = fetch_one("leaders", r["runner_up_candidate_id"])
            r["runner_up_name"] = runner["full_name"] if runner else "Unknown"

    return results
