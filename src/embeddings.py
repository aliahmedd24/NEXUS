"""Embedding generation using Gemini text-embedding-004.

Used for:
1. Seeding: Embed all existing unstructured text (feedback, bios, decision reasoning)
2. Runtime: Embed search queries for semantic retrieval tools

Model: text-embedding-004 (768 dimensions, best quality/cost ratio)
"""

import logging
from typing import Optional

from google import genai
from google.genai import types

from src.config import settings

logger = logging.getLogger(__name__)

# Initialize the Gemini client
_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    """Get or create the Gemini client singleton."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Generate an embedding vector for a single text.

    Args:
        text: The text to embed. Max ~2048 tokens for best quality.
        task_type: One of:
            - "RETRIEVAL_DOCUMENT" — for texts being stored (feedback, bios)
            - "RETRIEVAL_QUERY" — for search queries at runtime
            - "SEMANTIC_SIMILARITY" — for comparing two texts

    Returns:
        List of 768 floats (the embedding vector).
    """
    client = _get_client()
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )
    return result.embeddings[0].values


def embed_batch(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Generate embeddings for a batch of texts.

    More efficient than calling embed_text() in a loop — uses a single API call.

    Args:
        texts: List of texts to embed. Max ~100 per batch.
        task_type: Same as embed_text.

    Returns:
        List of embedding vectors, one per input text.
    """
    if not texts:
        return []

    client = _get_client()

    # Gemini embed_content supports batching via list of contents
    # Process in chunks of 100 to stay within API limits
    all_embeddings: list[list[float]] = []
    chunk_size = 100

    for i in range(0, len(texts), chunk_size):
        chunk = texts[i : i + chunk_size]
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=chunk,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )
        all_embeddings.extend([e.values for e in result.embeddings])
        logger.info("Embedded batch %d (%d texts)", i // chunk_size + 1, len(chunk))

    return all_embeddings


def embed_query(query: str) -> list[float]:
    """Embed a search query for retrieval.

    Uses RETRIEVAL_QUERY task type, which is optimized for
    matching against RETRIEVAL_DOCUMENT embeddings.

    Args:
        query: The search query string.

    Returns:
        768-dimensional embedding vector.
    """
    return embed_text(query, task_type="RETRIEVAL_QUERY")
