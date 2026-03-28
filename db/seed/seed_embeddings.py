"""Seed embeddings for all unstructured text data.

Reads from Supabase, generates embeddings via Gemini, writes vectors back.
Idempotent: skips rows that already have embeddings.
"""

import logging

from src.embeddings import embed_batch
from src.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def seed_feedback_embeddings() -> None:
    """Embed all feedback_360 entries that don't yet have embeddings."""
    sb = get_supabase()

    result = (
        sb.table("feedback_360")
        .select("id, feedback_text")
        .is_("embedding", "null")
        .execute()
    )
    rows = result.data
    if not rows:
        logger.info("All feedback_360 rows already have embeddings, skipping.")
        return

    logger.info("Embedding %d feedback_360 entries...", len(rows))
    texts = [r["feedback_text"] for r in rows]
    embeddings = embed_batch(texts)

    for row, embedding in zip(rows, embeddings):
        sb.table("feedback_360").update({"embedding": embedding}).eq(
            "id", row["id"]
        ).execute()

    logger.info("Embedded %d feedback entries.", len(rows))


def seed_review_embeddings() -> None:
    """Embed all performance_reviews narratives that don't yet have embeddings."""
    sb = get_supabase()

    result = (
        sb.table("performance_reviews")
        .select("id, review_narrative")
        .is_("embedding", "null")
        .not_.is_("review_narrative", "null")
        .execute()
    )
    rows = result.data
    if not rows:
        logger.info("All performance_reviews already have embeddings, skipping.")
        return

    logger.info("Embedding %d performance review narratives...", len(rows))
    texts = [r["review_narrative"] for r in rows]
    embeddings = embed_batch(texts)

    for row, embedding in zip(rows, embeddings):
        sb.table("performance_reviews").update({"embedding": embedding}).eq(
            "id", row["id"]
        ).execute()

    logger.info("Embedded %d review narratives.", len(rows))


def seed_leader_bio_embeddings() -> None:
    """Embed all leader bio_summary fields."""
    sb = get_supabase()

    result = (
        sb.table("leaders")
        .select("id, bio_summary")
        .is_("bio_embedding", "null")
        .not_.is_("bio_summary", "null")
        .execute()
    )
    rows = result.data
    if not rows:
        logger.info("All leader bios already have embeddings, skipping.")
        return

    logger.info("Embedding %d leader bios...", len(rows))
    texts = [r["bio_summary"] for r in rows]
    embeddings = embed_batch(texts)

    for row, embedding in zip(rows, embeddings):
        sb.table("leaders").update({"bio_embedding": embedding}).eq(
            "id", row["id"]
        ).execute()

    logger.info("Embedded %d leader bios.", len(rows))


def seed_decision_reasoning_embeddings() -> None:
    """Embed all historical decision reasoning texts."""
    sb = get_supabase()

    result = (
        sb.table("historical_decisions")
        .select("id, decision_reasoning")
        .is_("reasoning_embedding", "null")
        .not_.is_("decision_reasoning", "null")
        .execute()
    )
    rows = result.data
    if not rows:
        logger.info("All decision reasonings already have embeddings, skipping.")
        return

    logger.info("Embedding %d decision reasoning texts...", len(rows))
    texts = [r["decision_reasoning"] for r in rows]
    embeddings = embed_batch(texts)

    for row, embedding in zip(rows, embeddings):
        sb.table("historical_decisions").update(
            {"reasoning_embedding": embedding}
        ).eq("id", row["id"]).execute()

    logger.info("Embedded %d decision reasonings.", len(rows))


def seed_all_embeddings() -> None:
    """Seed all embedding columns. Idempotent."""
    logger.info("═══ Embedding Generation ═══")
    seed_feedback_embeddings()
    seed_review_embeddings()
    seed_leader_bio_embeddings()
    seed_decision_reasoning_embeddings()
    logger.info("═══ Embedding Generation Complete ═══")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    seed_all_embeddings()
