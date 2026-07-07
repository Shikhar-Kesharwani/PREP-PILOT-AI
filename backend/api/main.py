"""
FastAPI application entry point for PlacementPrep AI.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chat, interview, progress
from database.connection import create_tables
from utils.config import settings
from utils.logger import logger

# ── App creation ────────────────────────────────────────────────────────────
app = FastAPI(
    title="PlacementPrep AI",
    description=(
        "An AI-powered placement preparation assistant with CRAG pipeline, "
        "hybrid retrieval, hallucination detection, and interview simulation."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(interview.router)
app.include_router(progress.router)


# ── Lifecycle ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 PlacementPrep AI starting up…")
    try:
        create_tables()
        logger.info("✅ Database tables ready.")
    except Exception as e:
        logger.warning(f"Database not available: {e}. Running without persistence.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 PlacementPrep AI shutting down.")


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "PlacementPrep AI API",
        "docs": "/docs",
        "version": "2.0.0",
    }


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
