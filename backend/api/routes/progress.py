"""Progress and dashboard analytics routes."""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.connection import get_db
from database.models import InterviewSession, QuestionAttempt, ChatHistory, User
from utils.logger import logger

router = APIRouter(prefix="/api/progress", tags=["progress"])


def _get_or_create_guest_user(db: Session) -> int:
    """Return the guest user id (create if not exists)."""
    guest = db.query(User).filter(User.username == "guest").first()
    if not guest:
        guest = User(username="guest", email="guest@placementprep.ai")
        db.add(guest)
        db.commit()
        db.refresh(guest)
    return guest.id


@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    Return full performance dashboard analytics for a user.
    """
    # ── All attempts ────────────────────────────────────────────────────
    attempts = (
        db.query(QuestionAttempt)
        .join(InterviewSession, QuestionAttempt.session_id == InterviewSession.id)
        .filter(InterviewSession.user_id == user_id)
        .all()
    )

    # ── All sessions ────────────────────────────────────────────────────
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id, InterviewSession.is_completed == True)
        .order_by(InterviewSession.completed_at)
        .all()
    )

    # ── Overview ────────────────────────────────────────────────────────
    total_questions = len(attempts)
    total_sessions  = len(sessions)
    avg_score = round(sum(a.score for a in attempts) / total_questions, 2) if total_questions > 0 else 0.0
    overall_score = round(avg_score * 10, 1)  # scale 0-100

    # Streak — consecutive days with activity
    streak_days = _compute_streak(sessions)

    # ── Topic performance ────────────────────────────────────────────────
    topic_scores: dict = defaultdict(list)
    for a in attempts:
        topic_scores[a.question_type].append(a.score)

    all_topics = {
        topic: round(sum(scores) / len(scores) * 10, 1)
        for topic, scores in topic_scores.items()
    }
    strong = {k: v for k, v in all_topics.items() if v >= 70}
    weak   = {k: v for k, v in all_topics.items() if v < 60}

    # ── Score trend (last 14 sessions) ──────────────────────────────────
    recent_sessions = sessions[-14:]
    score_trend = [
        {
            "date": s.completed_at.strftime("%Y-%m-%d") if s.completed_at else "",
            "score": round(s.total_score * 10, 1) if s.total_questions > 0 else 0,
        }
        for s in recent_sessions
    ]

    # ── Company stats ────────────────────────────────────────────────────
    company_scores: dict = defaultdict(list)
    for a in attempts:
        if a.company:
            company_scores[a.company].append(a.score)

    company_stats = {
        company: round(sum(scores) / len(scores) * 10, 1)
        for company, scores in company_scores.items()
    }

    # ── Recommendations (top 3 weakest topics) ───────────────────────────
    sorted_weak = sorted(all_topics.items(), key=lambda x: x[1])[:3]
    recommendations = [
        {
            "topic": topic,
            "current_score": score,
            "suggestion": f"Focus on {topic} — your score is {score}/100. Practice more problems.",
        }
        for topic, score in sorted_weak
    ]

    return {
        "user_id": user_id,
        "overview": {
            "overall_score":    overall_score,
            "total_questions":  total_questions,
            "total_sessions":   total_sessions,
            "streak_days":      streak_days,
        },
        "topic_performance": {
            "strong": strong,
            "weak":   weak,
            "all":    dict(sorted(all_topics.items(), key=lambda x: x[1], reverse=True)),
        },
        "score_trend":    score_trend,
        "company_stats":  company_stats,
        "recommendations": recommendations,
    }


@router.get("/chat-stats/{user_id}")
async def get_chat_stats(user_id: int, db: Session = Depends(get_db)):
    """Return chat history statistics for a user."""
    chats = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).all()
    total = len(chats)
    hallucinations = sum(1 for c in chats if c.hallucination_detected)
    corrections = sum(1 for c in chats if c.correction_applied)

    topic_counts: dict = defaultdict(int)
    for c in chats:
        if c.topic:
            topic_counts[c.topic] += 1

    return {
        "total_queries": total,
        "hallucinations_detected": hallucinations,
        "corrections_applied": corrections,
        "top_topics": dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
    }


def _compute_streak(sessions: list) -> int:
    """Compute the number of consecutive days with activity."""
    if not sessions:
        return 0
    dates = set()
    for s in sessions:
        if s.completed_at:
            dates.add(s.completed_at.date())

    today = datetime.utcnow().date()
    streak = 0
    current = today
    while current in dates:
        streak += 1
        current -= timedelta(days=1)
    return streak
