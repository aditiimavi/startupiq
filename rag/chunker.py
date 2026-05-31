"""Chunking — delegates to production ingestion module."""

from langchain_core.documents import Document

from rag.ingestion.chunking import chunk_text
from rag.ingestion.models import PageContent

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def chunk_documents(
    raw_docs: dict[str, str],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    """
    Legacy API: chunk filename → text mappings.

    Prefer rag.ingestion.pipeline.ingest_document for full metadata.
    """
    _ = chunk_size, chunk_overlap  # sizing handled in ingestion.chunking

    all_chunks: list[Document] = []
    for filename, text in raw_docs.items():
        if not text.strip():
            continue
        pages = [PageContent(page_number=1, text=text, method="native")]
        file_hash = compute_file_hash_from_name(filename)
        all_chunks.extend(chunk_text(pages, filename, file_hash))
    return all_chunks


def compute_file_hash_from_name(filename: str) -> str:
    """Fallback hash when only filename is known (legacy path)."""
    import hashlib

    return hashlib.sha256(filename.encode()).hexdigest()[:16]
