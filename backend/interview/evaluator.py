"""Answer scoring and evaluation logic for the Interview Simulator."""
from __future__ import annotations
import json
from typing import Dict, Any, List

from groq import Groq

from utils.config import settings
from utils.logger import logger

EVALUATE_PROMPT = """\
You are an expert technical interviewer at {company}.

QUESTION ASKED: {question}

CANDIDATE'S ANSWER:
{answer}

EXPECTED KEY POINTS:
{expected_points}

COMPANY EVALUATION CRITERIA:
{evaluation_criteria}

INTERVIEW TYPE: {interview_type}

Evaluate this answer and return ONLY a JSON object:
{{
  "score": <integer 0-10>,
  "would_proceed": <true if score >= 6, else false>,
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "weaknesses": ["<weakness 1>", "<weakness 2>", ...],
  "missed_points": ["<key point not covered 1>", ...],
  "company_specific_feedback": "<1-2 sentences specific to {company} culture/criteria>",
  "ideal_answer_summary": "<concise 2-3 sentence summary of what a perfect answer looks like>",
  "follow_up_question": "<one follow-up question an interviewer would ask next>"
}}

Scoring rubric (0-10):
- 9-10: Exceptional — covers all points, clear structure, handles edge cases
- 7-8:  Strong — covers most points with minor gaps
- 5-6:  Average — covers basics but misses depth or key points
- 3-4:  Below average — fundamental gaps in understanding
- 0-2:  Poor — incorrect, off-topic, or very superficial

Return ONLY the JSON object.\
"""


class InterviewEvaluator:
    """Evaluates interview answers using Groq LLM with company-specific criteria."""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def evaluate(
        self,
        company: str,
        question: str,
        answer: str,
        interview_type: str = "DSA",
        expected_points: List[str] | None = None,
        evaluation_criteria: str = "",
    ) -> Dict[str, Any]:
        """
        Evaluate a candidate's answer.

        Returns dict with: score, would_proceed, strengths, weaknesses,
        missed_points, company_specific_feedback, ideal_answer_summary,
        follow_up_question
        """
        from interview.company_profiles import get_company_profile
        profile = get_company_profile(company)
        if not evaluation_criteria:
            evaluation_criteria = profile.get("evaluation_criteria", "Standard technical evaluation.")

        expected_str = "\n".join(f"- {p}" for p in (expected_points or []))
        if not expected_str:
            expected_str = "Not specified — use general best practices."

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": EVALUATE_PROMPT.format(
                        company=company,
                        question=question,
                        answer=answer,
                        expected_points=expected_str,
                        evaluation_criteria=evaluation_criteria,
                        interview_type=interview_type,
                    ),
                }],
                max_tokens=800,
                temperature=0.2,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:-1])
            result = json.loads(raw)

            # Normalize types
            result["score"] = max(0, min(10, int(result.get("score", 5))))
            result["would_proceed"] = result.get("would_proceed", result["score"] >= 6)
            result.setdefault("strengths", [])
            result.setdefault("weaknesses", [])
            result.setdefault("missed_points", [])
            result.setdefault("company_specific_feedback", "")
            result.setdefault("ideal_answer_summary", "")
            result.setdefault("follow_up_question", "")

            logger.info(f"Evaluation for {company}: score={result['score']}")
            return result

        except Exception as e:
            logger.error(f"InterviewEvaluator failed: {e}")
            return {
                "score": 5,
                "would_proceed": False,
                "strengths": [],
                "weaknesses": ["Evaluation could not be completed."],
                "missed_points": [],
                "company_specific_feedback": f"Evaluation error: {e}",
                "ideal_answer_summary": "",
                "follow_up_question": "",
            }
