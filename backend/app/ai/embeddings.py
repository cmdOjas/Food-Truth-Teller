"""
Sentence embedding utility.

Uses a lightweight sentence-transformers model to convert text into
dense vectors for semantic similarity search in the FAISS index.

Model: all-MiniLM-L6-v2  (~80 MB, runs fully on CPU)
  — fast enough for real-time RAG retrieval
  — good semantic accuracy for nutrition/health text
"""
from __future__ import annotations

import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

_MODEL = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def _load_model():
    """Lazy-load the embedding model (singleton)."""
    global _MODEL
    if _MODEL is None:
        logger.info("Loading sentence-transformer model: %s", _MODEL_NAME)
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(_MODEL_NAME)
        logger.info("Embedding model loaded.")
    return _MODEL


def embed(texts: List[str]) -> np.ndarray:
    """
    Encode a list of strings into a float32 numpy array of shape (N, D).

    Parameters
    ----------
    texts : list of strings to embed

    Returns
    -------
    np.ndarray of shape (len(texts), embedding_dim)
    """
    model = _load_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,   # cosine similarity via inner product
        convert_to_numpy=True,
    )
    return embeddings.astype(np.float32)


def embed_single(text: str) -> np.ndarray:
    """Convenience wrapper — embed a single string, return shape (1, D)."""
    return embed([text])


def embedding_dim() -> int:
    """Return the vector dimension of the loaded model."""
    return _load_model().get_sentence_embedding_dimension()
