"""Ingestion pipeline configuration constants."""

from pathlib import Path

# has_meaningful_text() thresholds
MIN_STRIPPED_LENGTH = 30
MIN_ALNUM_RATIO_VALID = 0.20

# Low-quality native text warning
MIN_TEXT_CHARS = 500
MIN_ALNUM_RATIO_NATIVE = 0.55
MIN_WORDS_PER_PAGE = 8

# Chunking
CHUNK_SIZE_TOKENS = 1000
CHUNK_OVERLAP_TOKENS = 120
CHUNK_SIZE_CHARS = 1000
CHUNK_OVERLAP_CHARS = 150

# Storage
CHROMA_PERSIST_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"
COLLECTION_NAME = "startupiq_documents"
REGISTRY_PATH = CHROMA_PERSIST_DIR / "ingestion_registry.json"
