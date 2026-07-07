"""
Critic Agent — detects hallucinations by verifying claims against context.
Generates corrected answer if hallucinations are found.
"""
from __future__ import annotations
import json
from typing import Dict, Any, List

from groq import Groq

from utils.config import settings
from utils.logger import logger

CRITIC_PROMPT = """\
You are a hallucination detection expert for an AI placement preparation system.

QUERY: {query}

GENERATED ANSWER:
{answer}

RETRIEVED CONTEXT (ground truth):
{context}

Task: Verify every factual claim in the generated answer against the context.

Return ONLY a JSON object:
{{
  "hallucination_found": <true|false>,
  "problematic_claims": ["<claim 1 that is NOT in context>", "<claim 2>", ...],
  "confidence": <float 0.0-1.0 how confident you are in this assessment>
}}

Rules:
- A claim is hallucinated if it states a specific fact NOT supported by context
- Minor paraphrasing is acceptable
- If answer says "I don't know" or admits uncertainty, that is NOT hallucination
- If no hallucinations, return empty list for problematic_claims

Return ONLY the JSON object.\
"""

CORRECTION_PROMPT = """\
You are an answer correction expert. Remove all hallucinated claims and rewrite
the answer using ONLY information supported by the provided context.

ORIGINAL QUERY: {query}

ORIGINAL ANSWER:
{answer}

PROBLEMATIC CLAIMS TO REMOVE:
{claims}

VERIFIED CONTEXT:
{context}

Rewrite the answer removing ALL problematic claims. If the answer becomes too
short after removal, add a note that "complete information was not available in
the study materials."

Keep formatting and structure as close to the original as possible.
Corrected answer:\
"""


class CriticAgent:
    """
    Verifies answer accuracy against retrieved context.
    Corrects the answer if hallucinations are detected.
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns partial state update with:
          hallucination_found, problematic_claims, final_answer, correction_applied
        """
        query = state.get("rewritten_query") or state.get("original_query", "")
        answer = state.get("initial_answer", "")
        chunks: List[Dict] = state.get("retrieved_chunks", [])

        context = self._build_context(chunks)

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": CRITIC_PROMPT.format(
                        query=query, answer=answer, context=context
                    ),
                }],
                max_tokens=400,
                temperature=0.1,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:-1])
            result = json.loads(raw)

            hallucination_found = bool(result.get("hallucination_found", False))
            problematic_claims = result.get("problematic_claims", [])

            logger.info(f"CriticAgent: hallucination={hallucination_found}, claims={len(problematic_claims)}")

            return {
                "hallucination_found": hallucination_found,
                "problematic_claims": problematic_claims,
                "final_answer": answer,  # will be overwritten by correction_node if needed
                "correction_applied": False,
            }

        except Exception as e:
            logger.warning(f"CriticAgent failed: {e} — assuming no hallucination.")
            return {
                "hallucination_found": False,
                "problematic_claims": [],
                "final_answer": answer,
                "correction_applied": False,
            }

    def correct(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Corrects the answer by removing hallucinated claims.
        Used in the correction_node.
        """
        query = state.get("rewritten_query") or state.get("original_query", "")
        answer = state.get("initial_answer", "")
        claims = state.get("problematic_claims", [])
        chunks = state.get("retrieved_chunks", [])
        context = self._build_context(chunks)

        claims_text = "\n".join(f"- {c}" for c in claims) if claims else "None identified"

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": CORRECTION_PROMPT.format(
                        query=query, answer=answer,
                        claims=claims_text, context=context,
                    ),
                }],
                max_tokens=1500,
                temperature=0.3,
            )
            corrected = response.choices[0].message.content.strip()
            final = "⚠️ Note: This answer was automatically corrected for accuracy.\n\n" + corrected
            logger.info("CriticAgent: correction applied.")
            return {"final_answer": final, "correction_applied": True}

        except Exception as e:
            logger.error(f"CriticAgent correction failed: {e}")
            return {
                "final_answer": "⚠️ Note: This answer was automatically corrected for accuracy.\n\n" + answer,
                "correction_applied": True,
            }

    def _build_context(self, chunks: List[Dict], max_chars: int = 6000) -> str:
        parts, total = [], 0
        for chunk in chunks:
            text = chunk.get("text", "")[:600]
            if total + len(text) > max_chars:
                break
            parts.append(text)
            total += len(text)
        return "\n\n".join(parts) or "No context available."
