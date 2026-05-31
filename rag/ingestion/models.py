"""Data models for ingestion inputs and outputs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PageContent:
    """Text extracted from a single PDF page."""

    page_number: int
    text: str
    method: str = "native"


@dataclass
class ExtractionResult:
    """Result of PDF text extraction."""

    file_path: str
    pages: list[PageContent]
    native_char_count: int
    warnings: list[str] = field(default_factory=list)
    final_source: str = "failed"  # pypdf | pdfminer | failed
    extraction_status: str = "OK"  # OK | FAILED_EXTRACTION
    failure_reason: str = ""

    @property
    def full_text(self) -> str:
        return "\n\n".join(
            (p.text or "").strip() for p in self.pages if (p.text or "").strip()
        )


@dataclass
class IngestionResult:
    """Outcome of ingesting a single document."""

    file_path: str
    file_hash: str
    success: bool
    chunks_stored: int
    skipped_duplicate: bool
    message: str
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    extraction_status: str = "OK"
    failure_reason: str = ""
    final_source: str = ""

    @property
    def document_metadata(self) -> dict:
        return {
            "extraction_status": self.extraction_status,
            "failure_reason": self.failure_reason,
            "final_source": self.final_source,
        }


@dataclass
class IngestionReport:
    """Batch ingestion summary."""

    total_files: int
    successful: int
    failed: int
    skipped_duplicates: int
    total_chunks: int
    results: list[IngestionResult] = field(default_factory=list)
