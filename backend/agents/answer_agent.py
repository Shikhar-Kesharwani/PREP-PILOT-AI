"""
Answer Agent — generates the final answer using retrieved context.
Applies format guidelines from PlannerAgent's answer_format.
"""
from __future__ import annotations
from typing import Dict, Any, List

from groq import Groq

from utils.config import settings
from utils.logger import logger

ANSWER_PROMPT = """\
You are an expert placement preparation tutor.

QUESTION: {query}

CONTEXT (from knowledge base):
{context}

FORMAT REQUIREMENT: {answer_format}

Instructions:
- Answer ONLY using information from the provided context.
- If the context is insufficient, clearly state: "The available study materials
  don't cover this in detail. Here's what I can share based on the context:"
  then answer partially.
- Apply the format requirement strictly:
  * "step-by-step with code" → numbered steps + Python/Java/C++ code blocks
    with Time Complexity and Space Complexity at the end
  * "system architecture" → describe components, their interactions, data flow,
    scaling considerations, and trade-offs
  * "STAR format" → Situation / Task / Action / Result structure
  * "comparison table" → use a markdown table
  * "definition with examples" → clear definition then 2-3 concrete examples
  * "explanation with examples" → conceptual explanation then examples
- Be comprehensive but concise (target: 300-600 words).
- Use markdown formatting for readability.

Answer:\
"""


class AnswerAgent:
    """
    Generates answers from retrieved context using Groq LLM.
    Respects answer_format from PlannerAgent.
    """

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns partial state update with:
          initial_answer
        """
        query = state.get("rewritten_query") or state.get("original_query", "")
        chunks: List[Dict] = state.get("retrieved_chunks", [])
        answer_format = state.get("answer_format", "explanation with examples")

        # Build context from top chunks
        context = self._build_context(chunks)

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": ANSWER_PROMPT.format(
                        query=query,
                        context=context,
                        answer_format=answer_format,
                    ),
                }],
                max_tokens=1500,
                temperature=0.4,
            )
            answer = response.choices[0].message.content.strip()
            logger.info(f"AnswerAgent generated answer ({len(answer)} chars)")
            return {"initial_answer": answer}

        except Exception as e:
            logger.error(f"AnswerAgent failed: {e}")
            return {"initial_answer": f"I encountered an error while generating the answer: {e}"}

    def _build_context(self, chunks: List[Dict], max_tokens: int = 3000) -> str:
        """Build context string from chunks, respecting token budget."""
        context_parts = []
        total_chars = 0
        char_budget = max_tokens * 4  # ~4 chars per token

        for i, chunk in enumerate(chunks):
            text = chunk.get("text", "")
            meta = chunk.get("metadata", chunk)
            source = f"[{meta.get('file_name', 'Source')} p.{meta.get('page_number', '?')}]"
            part = f"{source}\n{text}"

            if total_chars + len(part) > char_budget:
                break
            context_parts.append(part)
            total_chars += len(part)

        return "\n\n---\n\n".join(context_parts) if context_parts else "No context available."
