"""Interview API routes."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from interview.simulator import InterviewSimulator
from database.connection import get_db
from database.models import InterviewSession, QuestionAttempt
from utils.logger import logger

router = APIRouter(prefix="/api/interview", tags=["interview"])

_simulator = InterviewSimulator()


# ── Request / Response models ──────────────────────────────────────────────

class CompanyQuestionRequest(BaseModel):
    company: str
    previous_questions: Optional[List[str]] = []
    topic: Optional[str] = None
    difficulty: Optional[str] = None


class CompanyEvaluateRequest(BaseModel):
    company: str
    question: str
    answer: str
    interview_type: Optional[str] = "DSA"
    expected_points: Optional[List[str]] = []
    session_id: Optional[str] = None
    user_id: Optional[int] = None


class SaveSessionRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    company: Optional[str] = None
    mode: Optional[str] = "standard"
    total_score: Optional[float] = 0.0
    total_questions: Optional[int] = 0
    duration_seconds: Optional[int] = 0


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("/companies")
async def get_companies():
    """Return all 6 company profiles."""
    return _simulator.get_all_company_profiles()


@router.post("/company/question")
async def get_company_question(request: CompanyQuestionRequest):
    """Generate a company-specific interview question."""
    question_data = _simulator.generate_question(
        company=request.company,
        topic=request.topic,
        difficulty=request.difficulty,
        previous_questions=request.previous_questions,
    )
    return question_data


@router.post("/company/evaluate")
async def evaluate_answer(
    request: CompanyEvaluateRequest,
    db: Session = Depends(get_db),
):
    """Evaluate a candidate's answer with company-specific criteria."""
    if not request.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty.")

    evaluation = _simulator.evaluate_answer(
        company=request.company,
        question=request.question,
        answer=request.answer,
        interview_type=request.interview_type or "DSA",
        expected_points=request.expected_points,
    )

    # Save attempt to database if session_id provided
    if request.session_id:
        try:
            session = (
                db.query(InterviewSession)
                .filter(InterviewSession.session_id == request.session_id)
                .first()
            )
            if not session:
                session = InterviewSession(
                    session_id=request.session_id,
                    user_id=request.user_id,
                    company=request.company,
                    mode="company",
                )
                db.add(session)
                db.flush()

            attempt = QuestionAttempt(
                session_id=session.id,
                question=request.question,
                user_answer=request.answer,
                question_type=request.interview_type or "DSA",
                difficulty="Medium",
                company=request.company,
                score=float(evaluation.get("score", 5)),
                would_proceed=bool(evaluation.get("would_proceed", False)),
                strengths=evaluation.get("strengths", []),
                weaknesses=evaluation.get("weaknesses", []),
                missed_points=evaluation.get("missed_points", []),
                ideal_answer_summary=evaluation.get("ideal_answer_summary", ""),
                company_specific_feedback=evaluation.get("company_specific_feedback", ""),
                follow_up_question=evaluation.get("follow_up_question", ""),
            )
            db.add(attempt)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to save interview attempt: {e}")
            db.rollback()

    return evaluation


@router.post("/session")
async def save_session(request: SaveSessionRequest, db: Session = Depends(get_db)):
    """Create or update an interview session."""
    session_id = request.session_id or str(uuid.uuid4())
    try:
        session = (
            db.query(InterviewSession)
            .filter(InterviewSession.session_id == session_id)
            .first()
        )
        if session:
            session.total_score = request.total_score
            session.total_questions = request.total_questions
            session.duration_seconds = request.duration_seconds
            session.is_completed = True
            session.completed_at = datetime.utcnow()
        else:
            session = InterviewSession(
                session_id=session_id,
                user_id=request.user_id,
                company=request.company,
                mode=request.mode,
                total_score=request.total_score,
                total_questions=request.total_questions,
                duration_seconds=request.duration_seconds,
                is_completed=True,
                completed_at=datetime.utcnow(),
            )
            db.add(session)
        db.commit()
        return {"session_id": session_id, "saved": True}
    except Exception as e:
        logger.error(f"Failed to save session: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
