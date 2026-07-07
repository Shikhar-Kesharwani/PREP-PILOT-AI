"""
Retriever Agent — executes hybrid retrieval using strategy from PlannerAgent.
"""
from __future__ import annotations
from typing import Dict, Any, List

from retrieval.hybrid_retriever import HybridRetriever
from utils.logger import logger

# Weight presets per strategy
STRATEGY_WEIGHTS = {
    "semantic-heavy": (0.8, 0.2),
    "keyword-heavy":  (0.2, 0.8),
    "balanced":       (0.6, 0.4),
}


class RetrieverAgent:
    """
    Executes hybrid retrieval (BM25 + ChromaDB + reranker).
    Uses retrieval_strategy from PlannerAgent to adjust weights.
    """

    def __init__(self):
        self.retriever = HybridRetriever()

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns partial state update with:
          retrieved_chunks, citations
        """
        query = state.get("rewritten_query") or state.get("original_query", "")
        strategy = state.get("retrieval_strategy", "balanced")

        sem_w, bm25_w = STRATEGY_WEIGHTS.get(strategy, (0.6, 0.4))
        logger.info(f"RetrieverAgent: strategy={strategy}, sem={sem_w}, bm25={bm25_w}")

        chunks, citations = self.retriever.retrieve(
            query,
            semantic_weight=sem_w,
            bm25_weight=bm25_w,
        )

        return {
            "retrieved_chunks": chunks,
            "citations": citations,
        }
