"""
Interview Simulator — generates questions and runs mock interviews.
Supports standard mode and company-specific mode.
"""
from __future__ import annotations
import json
import random
from typing import Dict, Any, List, Optional

from groq import Groq

from interview.company_profiles import get_company_profile, get_weighted_topic, COMPANY_PROFILES
from interview.evaluator import InterviewEvaluator
from utils.config import settings
from utils.logger import logger

QUESTION_PROMPT = """\
You are a senior technical interviewer{company_context}.

Generate ONE interview question with the following specifications:
- Topic: {topic}
- Difficulty: {difficulty}
- Interview type: {interview_type}

Return ONLY a JSON object:
{{
  "question": "<the interview question>",
  "type": "{topic}",
  "difficulty": "{difficulty}",
  "expected_points": ["<key point 1>", "<key point 2>", "<key point 3>", "<key point 4>"],
  "follow_ups": ["<follow-up question 1>", "<follow-up question 2>"],
  "company_specific_tip": "<actionable tip for this company's interview style>"
}}

{style_instruction}

Make the question specific, technically accurate, and representative of real interviews.
Return ONLY the JSON object.\
"""


class InterviewSimulator:
    """
    Generates interview questions and coordinates evaluation.
    """

    DIFFICULTIES = ["Easy", "Medium", "Hard"]
    DIFFICULTY_WEIGHTS = [0.2, 0.5, 0.3]

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.evaluator = InterviewEvaluator()

    # ------------------------------------------------------------------ #
    #  Question generation                                                 #
    # ------------------------------------------------------------------ #

    def generate_question(
        self,
        company: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        previous_questions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a single interview question.

        Args:
            company:            Optional company name for company mode.
            topic:              Topic override (uses weighted random if None).
            difficulty:         Difficulty override.
            previous_questions: Already asked questions (to avoid duplicates).
        """
        profile = get_company_profile(company) if company else {}

        # Determine topic
        if topic is None:
            topic = get_weighted_topic(company) if company else random.choice([
                "DSA", "System Design", "Behavioral", "CS Fundamentals", "OOP"
            ])

        # Determine difficulty
        if difficulty is None:
            difficulty = profile.get("difficulty", "Medium")
            if difficulty == "Very Hard":
                difficulty = "Hard"

        # Build context
        company_context = f" at {company}" if company else ""
        style_instruction = ""
        if profile:
            style_instruction = (
                f"Interview style note: {profile.get('interview_style', '')[:300]}"
            )

        # Avoid repeats
        avoid_note = ""
        if previous_questions:
            avoid_note = f"\nAvoid these already-asked questions: {'; '.join(previous_questions[-3:])}"

        interview_type = topic

        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": QUESTION_PROMPT.format(
                        company_context=company_context,
                        topic=topic,
                        difficulty=difficulty,
                        interview_type=interview_type,
                        style_instruction=style_instruction + avoid_note,
                    ),
                }],
                max_tokens=600,
                temperature=0.7,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:-1])
            result = json.loads(raw)

            # Inject company
            result["company"] = company or "Generic"
            result.setdefault("company_specific_tip", "")
            result.setdefault("follow_ups", [])
            result.setdefault("expected_points", [])

            logger.info(f"Generated question: company={company}, topic={topic}, difficulty={difficulty}")
            return result

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return {
                "question": f"Explain the concept of {topic} with an example.",
                "type": topic,
                "difficulty": difficulty,
                "company": company or "Generic",
                "expected_points": ["Conceptual understanding", "Example", "Edge cases"],
                "follow_ups": ["What are the trade-offs?"],
                "company_specific_tip": "",
            }

    # ------------------------------------------------------------------ #
    #  Answer evaluation                                                   #
    # ------------------------------------------------------------------ #

    def evaluate_answer(
        self,
        company: str,
        question: str,
        answer: str,
        interview_type: str = "DSA",
        expected_points: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Evaluate a candidate's answer using the InterviewEvaluator."""
        return self.evaluator.evaluate(
            company=company,
            question=question,
            answer=answer,
            interview_type=interview_type,
            expected_points=expected_points,
        )

    # ------------------------------------------------------------------ #
    #  Session management                                                  #
    # ------------------------------------------------------------------ #

    def get_all_company_profiles(self) -> Dict[str, Any]:
        """Return all company profiles (safe subset for API)."""
        result = {}
        for company, profile in COMPANY_PROFILES.items():
            result[company] = {
                "name":            profile["name"],
                "logo_emoji":      profile["logo_emoji"],
                "difficulty":      profile["difficulty"],
                "focus_areas":     profile["focus_areas"],
                "topic_weights":   profile["topic_weights"],
                "interview_style": profile["interview_style"],
                "typical_rounds":  profile["typical_rounds"],
                "tips":            profile["tips"],
                "question_patterns": profile["question_patterns"],
                "known_for":       profile["known_for"],
            }
        return result
