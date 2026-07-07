"""
Planner Agent — classifies query type and decides retrieval strategy and
answer format.
"""
from __future__ import annotations
import json
from typing import Dict, Any

from groq import Groq

from utils.config import settings
from utils.logger import logger

PLAN_PROMPT = """\
You are a query planning agent for a placement preparation AI system.

Analyze the following query and return a JSON object with exactly these keys:
{{
  "query_type": "<one of: DSA, System Design, Behavioral, CS Fundamentals, OOP, DBMS, Operating Systems, Computer Networks, Mixed>",
  "retrieval_strategy": "<one of: semantic-heavy, keyword-heavy, balanced>",
  "answer_format": "<one of: step-by-step with code, explanation with examples, comparison table, STAR format, definition with examples, system architecture>"
}}

QUERY: {query}

Rules:
- DSA questions → keyword-heavy retrieval, step-by-step with code
- System Design → balanced retrieval, system architecture
- Behavioral → semantic-heavy retrieval, STAR format
- OS/Networks/DBMS → balanced retrieval, definition with examples
- OOP/Design Patterns → keyword-heavy, explanation with examples
- Mixed → balanced retrieval, explanation with examples

Return ONLY the JSON object, nothing else.\
"""


class PlannerAgent:
    """
    Analyzes the user's query to determine:
      - query_type: the topic domain
      - retrieval_strategy: how to weight semantic vs keyword search
      - answer_format: how to structure the answer
    """

    DEFAULTS = {
        "query_type": "Mixed",
        "retrieval_strategy": "balanced",
        "answer_format": "explanation with examples",
    }

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the rewritten query from state and returns plan metadata.

        Returns partial state update with:
          query_type, retrieval_strategy, answer_format
        """
        query = state.get("rewritten_query") or state.get("original_query", "")

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": PLAN_PROMPT.format(query=query)}],
                max_tokens=120,
                temperature=0.1,
            )
            raw = response.choices[0].message.content.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:-1])
            plan = json.loads(raw)

            # Validate fields
            result = {
                "query_type": plan.get("query_type", self.DEFAULTS["query_type"]),
                "retrieval_strategy": plan.get("retrieval_strategy", self.DEFAULTS["retrieval_strategy"]),
                "answer_format": plan.get("answer_format", self.DEFAULTS["answer_format"]),
            }
            logger.info(f"Plan: {result}")
            return result

        except Exception as e:
            logger.warning(f"PlannerAgent failed: {e} — using defaults.")
            return dict(self.DEFAULTS)
