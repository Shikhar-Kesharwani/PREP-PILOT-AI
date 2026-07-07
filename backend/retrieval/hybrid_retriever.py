"""
Hybrid retrieval engine: BM25 + ChromaDB with Reciprocal Rank Fusion,
followed by cross-encoder reranking.
"""
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import numpy as np

import chromadb

from data.embedder import embedder
from retrieval.reranker import reranker
from retrieval.citation_builder import CitationBuilder
from utils.config import settings
from utils.logger import logger

COLLECTION_NAME = "placementprep_knowledge"


class HybridRetriever:
    """
    Combines BM25 (keyword) and ChromaDB (semantic) search via
    Reciprocal Rank Fusion, then reranks with a cross-encoder.

    Scoring formula:
        fusion_score = (semantic_weight * rrf_semantic) +
                       (bm25_weight * rrf_bm25)
    """

    def __init__(
        self,
        semantic_weight: float = settings.SEMANTIC_WEIGHT,
        bm25_weight: float = settings.BM25_WEIGHT,
        top_k_retrieval: int = settings.TOP_K_RETRIEVAL,
        top_k_final: int = settings.TOP_K_FINAL,
        rrf_k: int = 60,
    ):
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight
        self.top_k_retrieval = top_k_retrieval
        self.top_k_final = top_k_final
        self.rrf_k = rrf_k

        self.citation_builder = CitationBuilder()

        # Lazy-loaded
        self._chroma_client = None
        self._collection = None
        self._bm25 = None
        self._bm25_docs = None

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def retrieve(
        self,
        query: str,
        semantic_weight: float | None = None,
        bm25_weight: float | None = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Run hybrid retrieval and reranking.

        Returns:
            (chunks, citations)
            chunks   — top_k_final reranked chunk dicts
            citations — deduplicated Citation dicts
        """
        sem_w = semantic_weight if semantic_weight is not None else self.semantic_weight
        bm25_w = bm25_weight if bm25_weight is not None else self.bm25_weight

        # 1. Semantic retrieval from ChromaDB
        chroma_hits = self._chroma_search(query, n=self.top_k_retrieval)

        # 2. BM25 retrieval
        bm25_hits = self._bm25_search(query, n=self.top_k_retrieval)

        # 3. Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion(chroma_hits, bm25_hits, sem_w, bm25_w)

        # 4. Cross-encoder reranking on top candidates
        reranked = reranker.rerank(query, fused, top_k=self.top_k_final)

        # 5. Build citations
        citations = self.citation_builder.build(reranked)

        logger.debug(f"Retrieved {len(reranked)} chunks for query: {query[:60]}…")
        return reranked, citations

    # ------------------------------------------------------------------ #
    #  ChromaDB                                                            #
    # ------------------------------------------------------------------ #

    def _get_collection(self):
        if self._collection is None:
            self._chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )
            self._collection = self._chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def _chroma_search(self, query: str, n: int) -> List[Dict[str, Any]]:
        try:
            collection = self._get_collection()
            query_vec = embedder.embed_query(query)
            results = collection.query(
                query_embeddings=[query_vec],
                n_results=min(n, collection.count() or 1),
                include=["documents", "metadatas", "distances"],
            )
            hits = []
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                # Convert cosine distance → similarity score
                score = 1.0 - float(dist)
                hits.append({"text": doc, "metadata": meta, "semantic_score": score})
            return hits
        except Exception as e:
            logger.warning(f"ChromaDB search error: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  BM25                                                                #
    # ------------------------------------------------------------------ #

    def _load_bm25(self):
        if self._bm25 is None:
            try:
                from data.ingestion import load_bm25
                self._bm25, self._bm25_docs = load_bm25()
            except Exception as e:
                logger.warning(f"BM25 index not found — keyword search disabled: {e}")
                self._bm25, self._bm25_docs = None, []

    def _bm25_search(self, query: str, n: int) -> List[Dict[str, Any]]:
        self._load_bm25()
        if self._bm25 is None:
            return []

        tokenized_query = query.lower().split()
        scores = self._bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:n]

        # Normalize BM25 scores to [0, 1]
        max_score = scores[top_indices[0]] if len(top_indices) > 0 else 1.0
        hits = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            doc = self._bm25_docs[idx]
            hits.append({
                "text": doc["text"],
                "metadata": {
                    "file_name":   doc["file_name"],
                    "page_number": doc["page_number"],
                    "topic":       doc["topic"],
                    "chunk_index": doc["chunk_index"],
                },
                "bm25_score": float(scores[idx] / max_score) if max_score > 0 else 0.0,
            })
        return hits

    # ------------------------------------------------------------------ #
    #  Reciprocal Rank Fusion                                              #
    # ------------------------------------------------------------------ #

    def _reciprocal_rank_fusion(
        self,
        chroma_hits: List[Dict],
        bm25_hits: List[Dict],
        sem_w: float,
        bm25_w: float,
    ) -> List[Dict]:
        """
        Merge two ranked lists using Reciprocal Rank Fusion.
        Returns merged list sorted by fusion_score descending.
        """
        doc_scores: Dict[str, Dict] = {}

        def rrf_score(rank: int) -> float:
            return 1.0 / (self.rrf_k + rank + 1)

        for rank, hit in enumerate(chroma_hits):
            key = self._doc_key(hit)
            if key not in doc_scores:
                doc_scores[key] = {**hit, "fusion_score": 0.0}
            doc_scores[key]["fusion_score"] += sem_w * rrf_score(rank)

        for rank, hit in enumerate(bm25_hits):
            key = self._doc_key(hit)
            if key not in doc_scores:
                doc_scores[key] = {**hit, "fusion_score": 0.0}
            doc_scores[key]["fusion_score"] += bm25_w * rrf_score(rank)

        fused = sorted(doc_scores.values(), key=lambda x: x["fusion_score"], reverse=True)
        return fused[:self.top_k_retrieval]

    @staticmethod
    def _doc_key(hit: Dict) -> str:
        """Unique key for deduplication (file + page + first 50 chars)."""
        meta = hit.get("metadata", {})
        return f"{meta.get('file_name','')}__{meta.get('page_number',0)}__{hit.get('text','')[:50]}"


# Singleton
hybrid_retriever = HybridRetriever()
