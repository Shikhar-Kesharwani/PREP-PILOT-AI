"""Citation builder — constructs and deduplicates source citations."""
from __future__ import annotations
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Citation:
    file_name: str
    page_number: int
    topic: str
    relevance_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CitationBuilder:
    """
    Builds deduplicated Citation objects from retrieved chunks.

    Deduplication key: (file_name, page_number)
    Final sort: descending by relevance_score.
    """

    def build(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build citations from a list of chunks.

        Each chunk must have:
          metadata.file_name, metadata.page_number, metadata.topic
          reranker_score (or fusion_score as fallback)
        """
        seen: Dict[tuple, Citation] = {}

        for chunk in chunks:
            meta = chunk.get("metadata", chunk)  # support both styles
            file_name  = meta.get("file_name", "Unknown")
            page_number = int(meta.get("page_number", 0))
            topic      = meta.get("topic", "General")
            score      = float(
                chunk.get("reranker_score",
                chunk.get("fusion_score", 0.0))
            )

            key = (file_name, page_number)
            if key not in seen or seen[key].relevance_score < score:
                seen[key] = Citation(
                    file_name=file_name,
                    page_number=page_number,
                    topic=topic,
                    relevance_score=round(score, 4),
                )

        sorted_citations = sorted(
            seen.values(),
            key=lambda c: c.relevance_score,
            reverse=True,
        )
        return [c.to_dict() for c in sorted_citations]
