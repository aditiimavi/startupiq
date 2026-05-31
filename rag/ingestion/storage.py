"""ChromaDB storage with deduplication support."""

from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from rag.ingestion.config import CHROMA_PERSIST_DIR, COLLECTION_NAME
from rag.ingestion.logger import get_ingestion_logger
from rag.ingestion.registry import clear_registry, register_file, remove_file_hash

logger = get_ingestion_logger(__name__)


def get_vector_store(embeddings: Embeddings) -> Chroma:
    """Return persistent Chroma collection."""
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PERSIST_DIR),
    )


def store_in_chroma(
    chunks: list[Document],
    embeddings: Embeddings,
    file_hash: str,
    *,
    replace_existing: bool = False,
) -> int:
    """
    Persist chunks in ChromaDB.

    If replace_existing, deletes prior vectors for this file_hash before insert.
    Returns number of chunks stored.
    """
    if not chunks:
        return 0

    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    store = get_vector_store(embeddings)

    if replace_existing:
        _delete_by_file_hash(store, file_hash)
        remove_file_hash(file_hash)

    # Stable ids prevent duplicate rows on re-ingest of same chunk content
    ids = [
        f"{file_hash}_{doc.metadata.get('chunk_index', i)}"
        for i, doc in enumerate(chunks)
    ]

    store.add_documents(documents=chunks, ids=ids)

    source = chunks[0].metadata.get("source", "unknown")
    register_file(file_hash, source, len(chunks))
    logger.info("Stored %s chunks for %s", len(chunks), source)
    return len(chunks)


def _delete_by_file_hash(store: Chroma, file_hash: str) -> None:
    """Remove all vectors matching file_hash metadata."""
    try:
        collection = store._collection
        collection.delete(where={"file_hash": file_hash})
        logger.info("Deleted existing vectors for hash %s…", file_hash[:12])
    except Exception as exc:
        logger.warning("Could not delete by file_hash: %s", exc)


def reset_vector_store() -> None:
    """Delete Chroma data directory and ingestion registry."""
    if CHROMA_PERSIST_DIR.exists():
        shutil.rmtree(CHROMA_PERSIST_DIR)
    clear_registry()
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
