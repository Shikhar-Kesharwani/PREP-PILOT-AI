"""Cross-encoder reranker using ms-marco-MiniLM-L-6-v2 (local, free)."""
from __future__ import annotations
from typing import List, Dict, Any, Tuple

from utils.logger import logger

_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        logger.info(f"Loading cross-encoder reranker: {_RERANKER_MODEL}")
        from sentence_transformers import CrossEncoder
        _reranker = CrossEncoder(_RERANKER_MODEL)
        logger.info("Reranker loaded.")
    return _reranker


class CrossEncoderReranker:
    """Reranks a list of (query, document) pairs using a cross-encoder."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = _get_reranker()
        return self._model

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidate chunks using cross-encoder scores.

        Each candidate must have a 'text' key.
        Returns candidates sorted by reranker score (descending), capped at top_k.
        """
        if not candidates:
            return []

        pairs: List[Tuple[str, str]] = [(query, c["text"]) for c in candidates]
        scores = self.model.predict(pairs)

        scored = [
            {**c, "reranker_score": float(score)}
            for c, score in zip(candidates, scores)
        ]
        scored.sort(key=lambda x: x["reranker_score"], reverse=True)
        return scored[:top_k]


# Module-level singleton
reranker = CrossEncoderReranker()
