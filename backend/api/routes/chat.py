"""Chat routes — CRAG pipeline endpoint."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from graph.workflow import run_crag
from database.connection import get_db
from database.models import ChatHistory
from utils.logger import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    citations: list
    topics: str
    hallucination_detected: bool
    correction_applied: bool
    confidence_score: float
    retrieval_quality: str
    steps_taken: list
    rewritten_query: str
    session_id: str


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Run the full CRAG pipeline on a user query and return the answer
    with citations, hallucination status, and metadata.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    session_id = request.session_id or str(uuid.uuid4())

    try:
        state = run_crag(query=request.query.strip(), session_id=session_id)
    except Exception as e:
        logger.error(f"CRAG pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")

    final_answer = state.get("final_answer") or state.get("initial_answer", "")
    hallucination = bool(state.get("hallucination_found", False))
    correction = bool(state.get("correction_applied", False))

    # Persist to database
    try:
        chat_record = ChatHistory(
            chat_session_id=session_id,
            user_id=request.user_id,
            original_query=request.query,
            rewritten_query=state.get("rewritten_query", ""),
            answer=final_answer,
            retrieval_quality=state.get("retrieval_quality", "AMBIGUOUS"),
            hallucination_detected=hallucination,
            correction_applied=correction,
            confidence_score=state.get("confidence_score", 0.0),
            citations=state.get("citations", []),
            steps_taken=state.get("steps_taken", []),
            topic=state.get("query_type", ""),
        )
        db.add(chat_record)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to save chat history: {e}")
        db.rollback()

    return ChatResponse(
        answer=final_answer,
        citations=state.get("citations", []),
        topics=state.get("query_type", "General"),
        hallucination_detected=hallucination,
        correction_applied=correction,
        confidence_score=state.get("confidence_score", 0.0),
        retrieval_quality=state.get("retrieval_quality", "AMBIGUOUS"),
        steps_taken=state.get("steps_taken", []),
        rewritten_query=state.get("rewritten_query", request.query),
        session_id=session_id,
    )
