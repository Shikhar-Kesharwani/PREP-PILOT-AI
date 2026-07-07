"""
Ingestion pipeline: PDFs → ChromaDB + BM25 index.

Usage:
    python -m data.ingestion              # ingest all PDFs from data/raw/
    python -m data.ingestion --reset      # wipe store and re-ingest
"""
from __future__ import annotations
import argparse
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from rank_bm25 import BM25Okapi

from data.chunker import PageAwareChunker
from data.embedder import embedder
from utils.config import settings
from utils.logger import logger

# Topic folder → topic label mapping
TOPIC_MAP: Dict[str, str] = {
    "DSA": "DSA",
    "System_Design": "System Design",
    "CS_Fundamentals": "CS Fundamentals",
    "Behavioral": "Behavioral",
}

BM25_INDEX_PATH = Path(settings.CHROMA_PERSIST_DIR) / "bm25_index.pkl"
BM25_DOCS_PATH  = Path(settings.CHROMA_PERSIST_DIR) / "bm25_docs.json"
COLLECTION_NAME = "placementprep_knowledge"


class DataIngestion:
    """Ingests PDF documents into ChromaDB and builds BM25 index."""

    def __init__(self):
        self.chunker = PageAwareChunker(chunk_size=512, chunk_overlap=64)
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        return self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest_all(self, raw_dir: str | None = None, reset: bool = False) -> int:
        """Ingest all PDFs found under raw_dir."""
        raw_path = Path(raw_dir or settings.RAW_DATA_DIR)
        if not raw_path.exists():
            logger.warning(f"Raw data directory not found: {raw_path}")
            return 0

        if reset:
            logger.info("Resetting ChromaDB collection…")
            self.chroma_client.delete_collection(COLLECTION_NAME)
            self.collection = self._get_or_create_collection()

        all_chunks: List[Dict[str, Any]] = []

        for topic_folder, topic_label in TOPIC_MAP.items():
            folder = raw_path / topic_folder
            if not folder.exists():
                continue
            for pdf_file in folder.glob("*.pdf"):
                chunks = self.chunker.chunk_pdf(pdf_file, topic=topic_label)
                all_chunks.extend(chunks)
                logger.info(f"  [{topic_label}] {pdf_file.name}: {len(chunks)} chunks")

        if not all_chunks:
            logger.warning("No chunks produced — add PDFs to data/raw/ folders.")
            return 0

        self._store_in_chroma(all_chunks)
        self._build_bm25(all_chunks)
        logger.info(f"Ingestion complete. Total chunks stored: {len(all_chunks)}")
        return len(all_chunks)

    def _store_in_chroma(self, chunks: List[Dict[str, Any]]):
        """Store chunks in ChromaDB with embeddings and metadata."""
        texts = [c["text"] for c in chunks]
        logger.info(f"Generating embeddings for {len(texts)} chunks…")
        embeddings = embedder.embed_batch(texts, batch_size=64)

        ids        = [f"chunk_{c['chunk_index']}_{c['file_name']}" for c in chunks]
        metadatas  = [
            {
                "page_number": c["page_number"],
                "file_name":   c["file_name"],
                "topic":       c["topic"],
                "chunk_index": c["chunk_index"],
                "token_count": c["token_count"],
            }
            for c in chunks
        ]

        # Upsert in batches of 500
        batch = 500
        for i in range(0, len(chunks), batch):
            self.collection.upsert(
                ids=ids[i:i+batch],
                embeddings=embeddings[i:i+batch],
                documents=texts[i:i+batch],
                metadatas=metadatas[i:i+batch],
            )
        logger.info(f"ChromaDB upsert complete: {len(chunks)} documents.")

    def _build_bm25(self, chunks: List[Dict[str, Any]]):
        """Build and persist a BM25 index from all chunk texts."""
        Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        tokenized = [c["text"].lower().split() for c in chunks]
        bm25 = BM25Okapi(tokenized)

        with open(BM25_INDEX_PATH, "wb") as f:
            pickle.dump(bm25, f)

        # Store docs for result mapping
        docs_meta = [
            {
                "text":        c["text"],
                "page_number": c["page_number"],
                "file_name":   c["file_name"],
                "topic":       c["topic"],
                "chunk_index": c["chunk_index"],
            }
            for c in chunks
        ]
        with open(BM25_DOCS_PATH, "w", encoding="utf-8") as f:
            json.dump(docs_meta, f, ensure_ascii=False, indent=2)

        logger.info(f"BM25 index built and saved to {BM25_INDEX_PATH}")


def load_bm25() -> tuple:
    """Load persisted BM25 index and document store."""
    with open(BM25_INDEX_PATH, "rb") as f:
        bm25 = pickle.load(f)
    with open(BM25_DOCS_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
    return bm25, docs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PlacementPrep AI — Data Ingestion")
    parser.add_argument("--reset", action="store_true", help="Wipe existing data and re-ingest")
    parser.add_argument("--dir",   default=None, help="Override raw data directory")
    args = parser.parse_args()

    ingestion = DataIngestion()
    total = ingestion.ingest_all(raw_dir=args.dir, reset=args.reset)
    print(f"\n✅ Ingestion done — {total} chunks stored.")
