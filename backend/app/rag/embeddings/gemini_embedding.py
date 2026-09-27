"""
app/rag/embeddings/gemini_embedding.py

Real embedding provider using Google Gemini's text-embedding model.
Replaces the FakeEmbeddingProvider for production RAG use.

Model used: models/text-embedding-004
  - 768-dimensional output
  - Supports task types: RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, etc.
"""
import logging
from typing import List

import google.generativeai as genai

from app.core.config import settings
from app.rag.embeddings.base import EmbeddingProvider

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider(EmbeddingProvider):
    """
    Embedding provider that calls the Gemini text-embedding-004 model.

    Requires GEMINI_API_KEY to be set in environment / .env.
    Falls back to a zero-vector on error so the app stays functional
    but logs a warning — prevents hard crashes during content generation.
    """

    MODEL_NAME = "models/text-embedding-004"
    DIMENSION = 768  # text-embedding-004 output dimension

    def __init__(self, api_key: str | None = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError(
                "GeminiEmbeddingProvider requires GEMINI_API_KEY to be set. "
                "Set USE_MOCK_AI=true to use FakeEmbeddingProvider instead."
            )
        genai.configure(api_key=key)

    async def embed_text(self, text: str) -> List[float]:
        """
        Embed a single piece of text using Gemini's text-embedding model.

        Args:
            text: The text to embed (e.g., a user query or document chunk).

        Returns:
            A list of 768 floats representing the embedding vector.
        """
        try:
            result = genai.embed_content(
                model=self.MODEL_NAME,
                content=text,
                task_type="RETRIEVAL_QUERY",
            )
            return result["embedding"]
        except Exception as exc:
            logger.warning(
                f"GeminiEmbeddingProvider: failed to embed text ({len(text)} chars): {exc}. "
                "Returning zero vector."
            )
            return [0.0] * self.DIMENSION

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple document chunks using RETRIEVAL_DOCUMENT task type.

        Args:
            texts: List of text chunks to embed.

        Returns:
            A list of embedding vectors, one per input text.
        """
        embeddings: List[List[float]] = []
        for text in texts:
            try:
                result = genai.embed_content(
                    model=self.MODEL_NAME,
                    content=text,
                    task_type="RETRIEVAL_DOCUMENT",
                )
                embeddings.append(result["embedding"])
            except Exception as exc:
                logger.warning(
                    f"GeminiEmbeddingProvider: failed to embed document chunk: {exc}. "
                    "Appending zero vector for this chunk."
                )
                embeddings.append([0.0] * self.DIMENSION)
        return embeddings
