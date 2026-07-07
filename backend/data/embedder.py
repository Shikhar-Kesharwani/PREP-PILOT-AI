"""Embedding generation using sentence-transformers (local, free)."""
from __future__ import annotations
from typing import List, Union
import numpy as np

from utils.logger import logger

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None


def _get_model():
    """Lazy-load the embedding model (singleton)."""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {_MODEL_NAME}")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(_MODEL_NAME)
        logger.info("Embedding model loaded.")
    return _model


class Embedder:
    """Wraps sentence-transformers for text embedding generation."""

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = _get_model()
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Embed a single string. Returns a list of floats."""
        vec = self.model.encode(text, normalize_embeddings=True)
        return vec.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        """Embed a list of strings in batches."""
        logger.debug(f"Embedding {len(texts)} texts in batch size {batch_size}")
        vecs = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 100,
        )
        return vecs.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Alias for embed_text, used for query-time embedding."""
        return self.embed_text(query)

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)


# Module-level singleton
embedder = Embedder()
