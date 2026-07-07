"""SQLAlchemy database models for PlacementPrep AI."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class TopicEnum(str, enum.Enum):
    DSA = "DSA"
    SYSTEM_DESIGN = "System Design"
    CS_FUNDAMENTALS = "CS Fundamentals"
    BEHAVIORAL = "Behavioral"
    OOP = "OOP"
    DBMS = "DBMS"
    OPERATING_SYSTEMS = "Operating Systems"
    COMPUTER_NETWORKS = "Computer Networks"
    MIXED = "Mixed"


class DifficultyEnum(str, enum.Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class CompanyEnum(str, enum.Enum):
    AMAZON = "Amazon"
    GOOGLE = "Google"
    MICROSOFT = "Microsoft"
    ADOBE = "Adobe"
    FLIPKART = "Flipkart"
    GOLDMAN_SACHS = "Goldman Sachs"
    GENERIC = "Generic"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interview_sessions = relationship("InterviewSession", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    company = Column(String(50), nullable=True)
    mode = Column(String(20), default="standard")  # standard / company
    total_score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    question_attempts = relationship("QuestionAttempt", back_populates="session")


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    question_type = Column(String(50), default="DSA")
    difficulty = Column(String(20), default="Medium")
    company = Column(String(50), nullable=True)
    score = Column(Float, default=0.0)  # 0-10
    would_proceed = Column(Boolean, default=False)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    missed_points = Column(JSON, default=list)
    ideal_answer_summary = Column(Text, nullable=True)
    company_specific_feedback = Column(Text, nullable=True)
    follow_up_question = Column(Text, nullable=True)
    attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("InterviewSession", back_populates="question_attempts")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(String(36), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    original_query = Column(Text, nullable=False)
    rewritten_query = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)
    retrieval_quality = Column(String(20), nullable=True)
    hallucination_detected = Column(Boolean, default=False)
    correction_applied = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)
    citations = Column(JSON, default=list)
    steps_taken = Column(JSON, default=list)
    topic = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_history")
