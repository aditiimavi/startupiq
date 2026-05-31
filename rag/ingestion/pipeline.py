"""End-to-end document ingestion pipeline."""

from __future__ import annotations

from pathlib import Path

from rag.embeddings import get_embedding_model
from rag.ingestion.chunking import chunk_text
from rag.ingestion.logger import get_ingestion_logger
from rag.ingestion.models import ExtractionResult, IngestionReport, IngestionResult
from rag.ingestion.pdf_extraction import (
    STATUS_FAILED_EXTRACTION,
    STATUS_OK,
    extract_pdf_text,
    has_meaningful_text,
    pages_to_text,
)
from rag.ingestion.registry import compute_file_hash, is_duplicate
from rag.ingestion.storage import reset_vector_store, store_in_chroma

logger = get_ingestion_logger(__name__)

SUPPORTED_EXTENSIONS = {".pdf"}


def load_document(file_path: str | Path) -> ExtractionResult:
    path = Path(file_path)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {path.suffix}. Supported: {SUPPORTED_EXTENSIONS}"
        )
    return extract_pdf_text(path)


def _final_text_from_extraction(extraction: ExtractionResult) -> str:
    from rag.ingestion.models import PageContent

    return pages_to_text(
        [
            PageContent(page_number=p.page_number, text=p.text, method=p.method)
            for p in extraction.pages
        ]
    )


def ingest_document(
    file_path: str | Path,
    *,
    skip_duplicates: bool = True,
    force_reindex: bool = False,
    embeddings=None,
) -> IngestionResult:
    path = Path(file_path)
    source_name = path.name
    warnings: list[str] = []

    try:
        file_hash = compute_file_hash(path)
    except OSError as exc:
        return IngestionResult(
            file_path=str(path),
            file_hash="",
            success=False,
            chunks_stored=0,
            skipped_duplicate=False,
            message=f"Could not read file: {exc}",
            errors=[str(exc)],
            extraction_status=STATUS_FAILED_EXTRACTION,
            failure_reason=str(exc),
        )

    if skip_duplicates and not force_reindex and is_duplicate(file_hash):
        logger.info("Skipping duplicate: %s", source_name)
        return IngestionResult(
            file_path=str(path),
            file_hash=file_hash,
            success=True,
            chunks_stored=0,
            skipped_duplicate=True,
            message=f"Already indexed (duplicate): {source_name}",
        )

    try:
        extraction = load_document(path)
        warnings.extend(extraction.warnings)

        final_text = _final_text_from_extraction(extraction)

        if not has_meaningful_text(final_text) or not extraction.pages:
            reason = (
                extraction.failure_reason
                or "PyPDF and pdfminer could not extract meaningful text"
            )
            logger.error(
                "[STATUS] FINAL_SOURCE = failed | document=%s | reason=%s",
                source_name,
                reason,
            )
            return IngestionResult(
                file_path=str(path),
                file_hash=file_hash,
                success=False,
                chunks_stored=0,
                skipped_duplicate=False,
                message=f"{source_name}: {reason}",
                warnings=warnings,
                extraction_status=STATUS_FAILED_EXTRACTION,
                failure_reason=reason,
                final_source=extraction.final_source or "failed",
            )

        chunks = chunk_text(extraction.pages, source_name, file_hash)
        if not chunks:
            reason = "chunking produced no content after extraction"
            return IngestionResult(
                file_path=str(path),
                file_hash=file_hash,
                success=False,
                chunks_stored=0,
                skipped_duplicate=False,
                message=f"{source_name}: {reason}",
                warnings=warnings,
                extraction_status=STATUS_FAILED_EXTRACTION,
                failure_reason=reason,
                final_source=extraction.final_source,
            )

        emb = embeddings or get_embedding_model()
        count = store_in_chroma(
            chunks,
            emb,
            file_hash,
            replace_existing=force_reindex,
        )

        for chunk in chunks:
            chunk.metadata["extraction_status"] = STATUS_OK
            chunk.metadata["final_source"] = extraction.final_source

        return IngestionResult(
            file_path=str(path),
            file_hash=file_hash,
            success=True,
            chunks_stored=count,
            skipped_duplicate=False,
            message=f"Ingested {count} chunks from {source_name}",
            warnings=warnings,
            extraction_status=STATUS_OK,
            final_source=extraction.final_source,
        )

    except Exception as exc:
        logger.exception("Ingestion failed for %s", source_name)
        return IngestionResult(
            file_path=str(path),
            file_hash=file_hash,
            success=False,
            chunks_stored=0,
            skipped_duplicate=False,
            message=f"Failed to ingest {source_name}: {exc}",
            errors=[str(exc)],
            warnings=warnings,
            extraction_status=STATUS_FAILED_EXTRACTION,
            failure_reason=str(exc),
        )


def ingest_documents(
    file_paths: list[str | Path],
    *,
    reset_collection: bool = False,
    skip_duplicates: bool = True,
) -> IngestionReport:
    if reset_collection:
        reset_vector_store()
        skip_duplicates = False

    embeddings = get_embedding_model()
    results: list[IngestionResult] = []
    total_chunks = 0
    successful = 0
    failed = 0
    skipped = 0

    for file_path in file_paths:
        result = ingest_document(
            file_path,
            skip_duplicates=skip_duplicates,
            force_reindex=reset_collection,
            embeddings=embeddings,
        )
        results.append(result)

        if result.skipped_duplicate:
            skipped += 1
        elif result.success:
            successful += 1
            total_chunks += result.chunks_stored
        else:
            failed += 1

    return IngestionReport(
        total_files=len(file_paths),
        successful=successful,
        failed=failed,
        skipped_duplicates=skipped,
        total_chunks=total_chunks,
        results=results,
    )


__all__ = ["load_document", "ingest_document", "ingest_documents"]
