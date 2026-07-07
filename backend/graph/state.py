"""LangGraph state definition for the CRAG workflow."""
from __future__ import annotations
from typing import TypedDict, List, Optional, Literal, Annotated
import operator


class GraphState(TypedDict, total=False):
    # ── Input ──────────────────────────────────────────────
    original_query:       str
    rewritten_query:      str

    # ── Planning ───────────────────────────────────────────
    query_type:           str          # DSA / System Design / Behavioral / …
    retrieval_strategy:   str          # semantic-heavy / keyword-heavy / balanced
    answer_format:        str          # step-by-step with code / STAR / …

    # ── Retrieval ──────────────────────────────────────────
    retrieved_chunks:     List[dict]
    retrieval_quality:    Literal["CORRECT", "AMBIGUOUS", "INCORRECT"]
    relevance_scores:     List[float]

    # ── Generation ─────────────────────────────────────────
    initial_answer:       str
    final_answer:         str

    # ── Hallucination ──────────────────────────────────────
    hallucination_found:  bool
    problematic_claims:   List[str]
    correction_applied:   bool

    # ── Citations ──────────────────────────────────────────
    citations:            List[dict]

    # ── Metadata ───────────────────────────────────────────
    steps_taken:          Annotated[List[str], operator.add]
    confidence_score:     float
