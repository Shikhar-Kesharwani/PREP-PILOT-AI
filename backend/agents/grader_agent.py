"""
Grader Agent — evaluates relevance of retrieved chunks to the query.
Returns CORRECT / AMBIGUOUS / INCORRECT.
"""
from __future__ import annotations
import json
from typing import Dict, Any, List

from groq import Groq

from utils.config import settings
from utils.logger import logger

GRADE_PROMPT = """\
You are a retrieval quality evaluator for a placement preparation AI.

USER QUERY: {query}

TOP RETRIEVED CHUNKS:
{chunks}

Evaluate how relevant these chunks are to answering the query.
Return ONLY a JSON object with this exact format:
{{
  "relevance_score": <float between 0.0 and 1.0>,
  "reasoning": "<one sentence explanation>",
  "quality": "<CORRECT|AMBIGUOUS|INCORRECT>"
}}

Scoring guide:
- CORRECT   (>0.7): Chunks directly answer the query with relevant information
- AMBIGUOUS (0.4-0.7): Chunks partially relate but lack key details
- INCORRECT (<0.4): Chunks are off-topic or don't address the query

Return ONLY the JSON object.\
"""


class GraderAgent:
    """
    Grades retrieval quality using Groq LLM.
    Inspects top 3 chunks and returns CORRECT / AMBIGUOUS / INCORRECT.
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns partial state update with:
          retrieval_quality, relevance_scores
        """
        query = state.get("rewritten_query") or state.get("original_query", "")
        chunks: List[Dict] = state.get("retrieved_chunks", [])

        if not chunks:
            logger.warning("GraderAgent: No chunks to grade — marking INCORRECT")
            return {"retrieval_quality": "INCORRECT", "relevance_scores": [0.0]}

        # Use top 3 chunks for grading
        top_chunks = chunks[:3]
        chunks_text = "\n\n".join(
            f"[Chunk {i+1}] {c.get('text', '')[:400]}"
            for i, c in enumerate(top_chunks)
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": GRADE_PROMPT.format(query=query, chunks=chunks_text),
                }],
                max_tokens=150,
                temperature=0.1,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:-1])
            result = json.loads(raw)

            score = float(result.get("relevance_score", 0.5))
            quality = result.get("quality", "AMBIGUOUS")

            # Validate quality label
            if quality not in ("CORRECT", "AMBIGUOUS", "INCORRECT"):
                if score >= settings.CORRECT_THRESHOLD:
                    quality = "CORRECT"
                elif score >= settings.AMBIGUOUS_THRESHOLD:
                    quality = "AMBIGUOUS"
                else:
                    quality = "INCORRECT"

            logger.info(f"GraderAgent: quality={quality}, score={score}")
            return {
                "retrieval_quality": quality,
                "relevance_scores": [score],
            }

        except Exception as e:
            logger.warning(f"GraderAgent failed: {e} — defaulting to AMBIGUOUS")
            return {"retrieval_quality": "AMBIGUOUS", "relevance_scores": [0.5]}
