"""
LangGraph node functions — each node corresponds to one step in the CRAG graph.
"""
from __future__ import annotations
from typing import Dict, Any

from groq import Groq

from agents.query_rewriter import QueryRewriter
from agents.planner_agent import PlannerAgent
from agents.retriever_agent import RetrieverAgent
from agents.grader_agent import GraderAgent
from agents.answer_agent import AnswerAgent
from agents.critic_agent import CriticAgent
from graph.state import GraphState
from utils.config import settings
from utils.logger import logger

# ── Singleton agents ───────────────────────────────────────────────────────
_query_rewriter  = QueryRewriter()
_planner_agent   = PlannerAgent()
_retriever_agent = RetrieverAgent()
_grader_agent    = GraderAgent()
_answer_agent    = AnswerAgent()
_critic_agent    = CriticAgent()


# ── Node 1: Query Rewriter ─────────────────────────────────────────────────
def query_rewriter_node(state: GraphState) -> Dict[str, Any]:
    logger.info("▶ Node: query_rewriter")
    original = state.get("original_query", "")
    rewritten = _query_rewriter.rewrite(original)
    return {
        "rewritten_query": rewritten,
        "steps_taken": ["query_rewriter"],
    }


# ── Node 2: Planner ────────────────────────────────────────────────────────
def planner_node(state: GraphState) -> Dict[str, Any]:
    logger.info("▶ Node: planner")
    plan = _planner_agent.run(state)
    return {**plan, "steps_taken": ["planner"]}


# ── Node 3: Retriever ──────────────────────────────────────────────────────
def retriever_node(state: GraphState) -> Dict[str, Any]:
    logger.info("▶ Node: retriever")
    result = _retriever_agent.run(state)
    return {**result, "steps_taken": ["retriever"]}


# ── Node 4: Grader ─────────────────────────────────────────────────────────
def grader_node(state: GraphState) -> Dict[str, Any]:
    logger.info("▶ Node: grader")
    result = _grader_agent.run(state)
    return {**result, "steps_taken": ["grader"]}


# ── Node 5: Answer ─────────────────────────────────────────────────────────
def answer_node(state: GraphState) -> Dict[str, Any]:
    logger.info("▶ Node: answer")
    result = _answer_agent.run(state)
    # Set final_answer = initial_answer (critic may override)
    answer = result.get("initial_answer", "")
    return {
        "initial_answer": answer,
        "final_answer":   answer,
        "steps_taken":    ["answer"],
    }


# ── Node 6: Critic ─────────────────────────────────────────────────────────
def critic_node(state: GraphState) -> Dict[str, Any]:
    logger.info("▶ Node: critic")
    result = _critic_agent.run(state)
    return {**result, "steps_taken": ["critic"]}


# ── Node 7: Correction ─────────────────────────────────────────────────────
def correction_node(state: GraphState) -> Dict[str, Any]:
    logger.info("▶ Node: correction")
    result = _critic_agent.correct(state)
    return {**result, "steps_taken": ["correction"]}


# ── Node 8: Web Fallback ───────────────────────────────────────────────────
def web_fallback_node(state: GraphState) -> Dict[str, Any]:
    """
    When retrieval quality is INCORRECT, answer from LLM general knowledge
    with a clear disclaimer. No web API needed.
    """
    logger.info("▶ Node: web_fallback")
    query = state.get("rewritten_query") or state.get("original_query", "")

    client = Groq(api_key=settings.GROQ_API_KEY)
    disclaimer = (
        "⚠️ **Disclaimer**: The study materials in our knowledge base didn't have "
        "sufficient information for this query. The following answer is based on "
        "general knowledge and may not reflect your specific study materials.\n\n"
    )

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{
                "role": "system",
                "content": (
                    "You are an expert placement preparation tutor. "
                    "Answer the question thoroughly with technical accuracy."
                ),
            }, {
                "role": "user",
                "content": query,
            }],
            max_tokens=1200,
            temperature=0.5,
        )
        answer = disclaimer + response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"web_fallback_node LLM call failed: {e}")
        answer = disclaimer + "Unable to generate an answer at this time. Please try rephrasing your question."

    return {
        "initial_answer": answer,
        "final_answer":   answer,
        "retrieved_chunks": state.get("retrieved_chunks", []),
        "citations": [],
        "steps_taken": ["web_fallback"],
    }
