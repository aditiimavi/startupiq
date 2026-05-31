"""Production-grade document ingestion for StartupIQ RAG."""

from rag.ingestion.chunking import chunk_text
from rag.ingestion.models import IngestionReport, IngestionResult
from rag.ingestion.pdf_extraction import extract_pdf_text
from rag.ingestion.pipeline import ingest_document, ingest_documents, load_document
from rag.ingestion.storage import store_in_chroma
from rag.ingestion.text_cleaning import clean_text

__all__ = [
    "IngestionReport",
    "IngestionResult",
    "load_document",
    "extract_pdf_text",
    "clean_text",
    "chunk_text",
    "store_in_chroma",
    "ingest_document",
    "ingest_documents",
]
