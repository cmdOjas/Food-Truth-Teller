"""
RAG (Retrieval-Augmented Generation) retriever.

Builds and queries a FAISS flat inner-product index over the nutrition
knowledge base.  The index is built once at startup and held in memory.
Retrieval is O(n) but n <= ~200 entries so it is instant (<1 ms).

Usage
-----
from app.ai.rag import retriever
context = retriever.retrieve("diabetes high sugar risk", top_k=4)
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

_INDEX_PATH = Path(__file__).parent / "faiss_index.bin"
_DOCS_PATH  = Path(__file__).parent / "faiss_docs.txt"


class NutritionRetriever:
    """FAISS-backed semantic retriever for nutrition knowledge."""

    def __init__(self) -> None:
        self._index = None
        self._documents: list[str] = []
        self._built = False

    def build(self, force: bool = False) -> None:
        """Build (or load cached) FAISS index from the knowledge base."""
        if self._built and not force:
            return

        # Import here to avoid circular deps at module level
        import faiss
        from app.ai.embeddings import embed
        from app.ai.knowledge_base import KNOWLEDGE_ENTRIES

        if _INDEX_PATH.exists() and _DOCS_PATH.exists() and not force:
            logger.info("Loading cached FAISS index from %s", _INDEX_PATH)
            self._index = faiss.read_index(str(_INDEX_PATH))
            self._documents = _DOCS_PATH.read_text(encoding="utf-8").split("\n---\n")
            self._built = True
            logger.info("FAISS index loaded (%d entries).", len(self._documents))
            return

        logger.info("Building FAISS index from %d knowledge entries...", len(KNOWLEDGE_ENTRIES))
        vectors = embed(KNOWLEDGE_ENTRIES)  # shape (N, D)
        dim = vectors.shape[1]

        self._index = faiss.IndexFlatIP(dim)   # inner product = cosine (vecs are L2-normalised)
        self._index.add(vectors)
        self._documents = list(KNOWLEDGE_ENTRIES)

        # Persist for fast reload
        faiss.write_index(self._index, str(_INDEX_PATH))
        _DOCS_PATH.write_text("\n---\n".join(self._documents), encoding="utf-8")
        self._built = True
        logger.info("FAISS index built and saved (%d entries, dim=%d).", len(self._documents), dim)

    def retrieve(self, query: str, top_k: int = 4) -> List[str]:
        """
        Return the *top_k* most semantically relevant knowledge-base entries.

        Parameters
        ----------
        query  : The query string (e.g. product name + user conditions).
        top_k  : Number of results to retrieve.

        Returns
        -------
        List of matching knowledge-base strings.
        """
        if not self._built:
            self.build()

        from app.ai.embeddings import embed_single
        q_vec = embed_single(query)          # shape (1, D)

        distances, indices = self._index.search(q_vec, min(top_k, len(self._documents)))
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self._documents):
                results.append(self._documents[idx])
        return results


# Module-level singleton — imported by other modules
retriever = NutritionRetriever()
