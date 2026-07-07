"""Configuration management for PlacementPrep AI."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3-70b-8192")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://placementprep:placementprep123@localhost:5432/placementprep"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(BASE_DIR / "data" / "vectorstore")
    )

    # App
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "change-me-in-production")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Retrieval
    TOP_K_RETRIEVAL: int = 20       # retrieve top 20 before reranking
    TOP_K_FINAL: int = 10           # return top 10 after reranking
    SEMANTIC_WEIGHT: float = 0.6
    BM25_WEIGHT: float = 0.4

    # Grading thresholds
    CORRECT_THRESHOLD: float = 0.7
    AMBIGUOUS_THRESHOLD: float = 0.4

    # Data paths
    RAW_DATA_DIR: str = str(BASE_DIR / "data" / "raw")
    PROCESSED_DATA_DIR: str = str(BASE_DIR / "data" / "processed")


settings = Settings()
