"""
LangGraph CRAG workflow builder.

Graph flow:
  START
   → query_rewriter
   → planner
   → retriever
   → grader
   → [CORRECT/AMBIGUOUS] → answer → critic → [PASS] → END
                                           → [FAIL] → correction → END
   → [INCORRECT] → web_fallback → answer → critic → [PASS] → END
                                                   → [FAIL] → correction → END
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from graph.state import GraphState
from graph.nodes import (
    query_rewriter_node,
    planner_node,
    retriever_node,
    grader_node,
    answer_node,
    critic_node,
    correction_node,
    web_fallback_node,
)
from utils.logger import logger


def route_after_grading(state: GraphState) -> str:
    """Route based on retrieval quality."""
    quality = state.get("retrieval_quality", "AMBIGUOUS")
    logger.debug(f"Routing after grading: {quality}")
    if quality == "INCORRECT":
        return "web_fallback"
    return "answer"  # CORRECT and AMBIGUOUS both go to answer


def route_after_critic(state: GraphState) -> str:
    """Route based on hallucination detection."""
    if state.get("hallucination_found", False):
        logger.debug("Critic routing: FAIL → correction")
        return "correction"
    logger.debug("Critic routing: PASS → END")
    return "END"


def build_crag_graph() -> StateGraph:
    """Build and compile the CRAG LangGraph state machine."""
    graph = StateGraph(GraphState)

    # ── Register nodes ──────────────────────────────────────────────────
    graph.add_node("query_rewriter", query_rewriter_node)
    graph.add_node("planner",        planner_node)
    graph.add_node("retriever",      retriever_node)
    graph.add_node("grader",         grader_node)
    graph.add_node("answer",         answer_node)
    graph.add_node("critic",         critic_node)
    graph.add_node("correction",     correction_node)
    graph.add_node("web_fallback",   web_fallback_node)

    # ── Entry point ─────────────────────────────────────────────────────
    graph.set_entry_point("query_rewriter")

    # ── Fixed edges ─────────────────────────────────────────────────────
    graph.add_edge("query_rewriter", "planner")
    graph.add_edge("planner",        "retriever")
    graph.add_edge("retriever",      "grader")
    graph.add_edge("web_fallback",   "answer")
    graph.add_edge("answer",         "critic")
    graph.add_edge("correction",     END)

    # ── Conditional: grader → answer or web_fallback ────────────────────
    graph.add_conditional_edges(
        "grader",
        route_after_grading,
        {
            "answer":      "answer",
            "web_fallback": "web_fallback",
        }
    )

    # ── Conditional: critic → END or correction ─────────────────────────
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "END":        END,
            "correction": "correction",
        }
    )

    compiled = graph.compile()
    logger.info("CRAG graph compiled successfully.")
    return compiled


# ── Module-level singleton — import this everywhere ─────────────────────────
CRAG_GRAPH = build_crag_graph()


def run_crag(query: str, session_id: str = "") -> dict:
    """
    Convenience function to run the full CRAG pipeline.

    Args:
        query:      The user's question.
        session_id: Optional session identifier for logging.

    Returns:
        Final GraphState dict.
    """
    initial_state: GraphState = {
        "original_query":      query,
        "rewritten_query":     "",
        "query_type":          "",
        "retrieval_strategy":  "balanced",
        "answer_format":       "explanation with examples",
        "retrieved_chunks":    [],
        "retrieval_quality":   "AMBIGUOUS",
        "relevance_scores":    [],
        "initial_answer":      "",
        "final_answer":        "",
        "hallucination_found": False,
        "problematic_claims":  [],
        "correction_applied":  False,
        "citations":           [],
        "steps_taken":         [],
        "confidence_score":    0.0,
    }

    logger.info(f"Running CRAG for session={session_id}: {query[:80]}…")
    result = CRAG_GRAPH.invoke(initial_state)

    # Compute a rough confidence score from relevance scores
    scores = result.get("relevance_scores", [0.5])
    result["confidence_score"] = round(sum(scores) / len(scores), 4) if scores else 0.5

    return result
