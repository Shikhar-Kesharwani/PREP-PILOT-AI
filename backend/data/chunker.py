"""Page-aware PDF chunking using pypdf and tiktoken."""
from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Any

import tiktoken
from pypdf import PdfReader

from utils.logger import logger


class PageAwareChunker:
    """
    Splits PDFs into overlapping text chunks while preserving page metadata.
    Each chunk carries: text, page_number, file_name, topic, chunk_index.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        encoding_name: str = "cl100k_base",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def chunk_pdf(self, pdf_path: str | Path, topic: str = "General") -> List[Dict[str, Any]]:
        """
        Parse a PDF and return a list of chunk dicts.

        Each dict has:
          text, page_number, file_name, topic, chunk_index, token_count
        """
        pdf_path = Path(pdf_path)
        file_name = pdf_path.name
        logger.info(f"Chunking PDF: {file_name} | topic={topic}")

        try:
            reader = PdfReader(str(pdf_path))
        except Exception as e:
            logger.error(f"Cannot read PDF {file_name}: {e}")
            return []

        all_chunks: List[Dict[str, Any]] = []
        chunk_index = 0

        for page_num, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            cleaned = self._clean_text(raw_text)
            if not cleaned:
                continue

            page_chunks = self._split_text(cleaned)
            for chunk_text in page_chunks:
                tokens = self.encoding.encode(chunk_text)
                all_chunks.append({
                    "text": chunk_text,
                    "page_number": page_num,
                    "file_name": file_name,
                    "topic": topic,
                    "chunk_index": chunk_index,
                    "token_count": len(tokens),
                })
                chunk_index += 1

        logger.info(f"Produced {len(all_chunks)} chunks from {file_name}")
        return all_chunks

    def chunk_text(self, text: str, file_name: str = "inline", topic: str = "General") -> List[Dict[str, Any]]:
        """Chunk a raw text string (no PDF)."""
        chunks = self._split_text(self._clean_text(text))
        return [
            {
                "text": c,
                "page_number": 1,
                "file_name": file_name,
                "topic": topic,
                "chunk_index": i,
                "token_count": len(self.encoding.encode(c)),
            }
            for i, c in enumerate(chunks)
        ]

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _clean_text(self, text: str) -> str:
        """Normalize whitespace and remove junk characters."""
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\x20-\x7E\n]", "", text)
        return text.strip()

    def _split_text(self, text: str) -> List[str]:
        """Split text into token-bounded chunks with overlap."""
        tokens = self.encoding.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            if end == len(tokens):
                break
            start += self.chunk_size - self.chunk_overlap
        return chunks
