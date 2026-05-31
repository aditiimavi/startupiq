"""Vector store — delegates to production ingestion storage."""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from rag.ingestion.config import CHROMA_PERSIST_DIR, COLLECTION_NAME
from rag.ingestion.storage import get_vector_store, reset_vector_store, store_in_chroma

__all__ = [
    "CHROMA_PERSIST_DIR",
    "COLLECTION_NAME",
    "get_vector_store",
    "index_documents",
    "reset_vector_store",
    "store_in_chroma",
]


def index_documents(
    chunks: list[Document],
    embeddings: Embeddings,
    reset: bool = False,
) -> Chroma:
    """
    Legacy batch index API.

    For file-hash deduplication use rag.ingestion.pipeline.ingest_document.
    """
    if reset:
        reset_vector_store()

    if not chunks:
        return get_vector_store(embeddings)

    file_hash = chunks[0].metadata.get("file_hash", "legacy_batch")
    store_in_chroma(chunks, embeddings, file_hash, replace_existing=reset)
    return get_vector_store(embeddings)
