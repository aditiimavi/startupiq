"""PDF text extraction: PyPDF → pdfminer fallback."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from rag.ingestion.config import (
    MIN_ALNUM_RATIO_NATIVE,
    MIN_ALNUM_RATIO_VALID,
    MIN_STRIPPED_LENGTH,
    MIN_TEXT_CHARS,
    MIN_WORDS_PER_PAGE,
)
from rag.ingestion.logger import get_ingestion_logger
from rag.ingestion.models import ExtractionResult, PageContent
from rag.ingestion.text_cleaning import clean_text

logger = get_ingestion_logger(__name__)

STATUS_OK = "OK"
STATUS_FAILED_EXTRACTION = "FAILED_EXTRACTION"

SOURCE_PYPDF = "pypdf"
SOURCE_PDFMINER = "pdfminer"
SOURCE_FAILED = "failed"


def _safe_strip(text: str | None) -> str:
    if text is None:
        return ""
    return str(text).strip()


def _alnum_count(text: str) -> int:
    return sum(1 for c in text if c.isalnum())


def _alnum_ratio(text: str) -> float:
    if not text:
        return 0.0
    return _alnum_count(text) / len(text)


def _is_only_punctuation_or_symbols(text: str) -> bool:
    import string

    if not text:
        return True
    allowed = set(string.punctuation + string.whitespace)
    return all(c in allowed for c in text)


def has_meaningful_text(text: str | None) -> bool:
    """True when text is valid for RAG after strip()."""
    stripped = _safe_strip(text)
    if not stripped:
        return False
    if len(stripped) < MIN_STRIPPED_LENGTH:
        return False
    if _is_only_punctuation_or_symbols(stripped):
        return False
    if _alnum_ratio(stripped) < MIN_ALNUM_RATIO_VALID:
        return False
    return True


def _log_stage(stage: str, detail: str) -> None:
    logger.info("[STAGE] %s → %s", stage, detail)


def _log_status(key: str, value: str) -> None:
    logger.info("[STATUS] %s = %s", key, value)


def extract_pdf_text(file_path: str | Path) -> ExtractionResult:
    """Extract text: PyPDF first, then pdfminer if native extraction fails."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    warnings: list[str] = []
    final_source = SOURCE_FAILED
    extraction_status = STATUS_OK
    failure_reason = ""

    pypdf_pages = _extract_native_pypdf(path)
    text = _pages_to_text(pypdf_pages)
    final_pages = pypdf_pages
    _log_stage("PyPDF", f"{len(text)} chars")

    if not has_meaningful_text(text):
        pdfminer_pages = _extract_native_pdfminer(path)
        pdfminer_text = _pages_to_text(pdfminer_pages)
        _log_stage("PDFMiner", f"{len(pdfminer_text)} chars")

        if has_meaningful_text(pdfminer_text):
            text = pdfminer_text
            final_pages = pdfminer_pages
            final_source = SOURCE_PDFMINER
        else:
            final_source = SOURCE_FAILED
            extraction_status = STATUS_FAILED_EXTRACTION
            failure_reason = "PyPDF and pdfminer could not extract meaningful text"
            warnings.append(failure_reason)
    else:
        final_source = SOURCE_PYPDF
        if _is_low_quality_native(text, len(final_pages)):
            warnings.append("Native text may be incomplete for image-heavy PDFs.")

    cleaned_pages = _to_cleaned_pages(final_pages)
    native_char_count = len(_pages_to_text(pypdf_pages))

    if not has_meaningful_text(text):
        extraction_status = STATUS_FAILED_EXTRACTION
        if not failure_reason:
            failure_reason = "all native extraction methods failed"

    _log_status("FINAL_SOURCE", final_source)

    return ExtractionResult(
        file_path=str(path),
        pages=cleaned_pages,
        native_char_count=native_char_count,
        warnings=warnings,
        final_source=final_source,
        extraction_status=extraction_status,
        failure_reason=failure_reason,
    )


def pages_to_text(pages: list[PageContent]) -> str:
    return _pages_to_text(pages)


def _pages_to_text(pages: list[PageContent]) -> str:
    parts: list[str] = []
    for page in pages:
        stripped = _safe_strip(page.text)
        if has_meaningful_text(stripped):
            parts.append(stripped)
    return "\n\n".join(parts).strip()


def _to_cleaned_pages(pages: list[PageContent]) -> list[PageContent]:
    cleaned: list[PageContent] = []
    for page in pages:
        text = clean_text(_safe_strip(page.text))
        if has_meaningful_text(text):
            cleaned.append(
                PageContent(
                    page_number=page.page_number,
                    text=text,
                    method="native",
                )
            )
    return cleaned


def _extract_native_pypdf(path: Path) -> list[PageContent]:
    pages: list[PageContent] = []
    try:
        reader = PdfReader(str(path), strict=False)
    except Exception as exc:
        logger.error("PyPDF could not read %s: %s", path.name, exc)
        raise ValueError(f"Corrupted or unreadable PDF: {path.name}") from exc

    for idx, page in enumerate(reader.pages, start=1):
        try:
            page_text = _safe_strip(page.extract_text())
        except Exception as exc:
            logger.warning("PyPDF page %s failed in %s: %s", idx, path.name, exc)
            page_text = ""
        pages.append(PageContent(page_number=idx, text=page_text, method="native"))
    return pages


def _extract_native_pdfminer(path: Path) -> list[PageContent]:
    try:
        from pdfminer.high_level import extract_text
    except ImportError:
        _log_stage("PDFMiner", "0 chars (not installed)")
        return []

    try:
        full_text = _safe_strip(extract_text(str(path)))
    except Exception as exc:
        logger.warning("pdfminer failed for %s: %s", path.name, exc)
        return []

    if not has_meaningful_text(full_text):
        return []

    raw_pages = full_text.split("\x0c") if "\x0c" in full_text else [full_text]
    return [
        PageContent(page_number=i, text=_safe_strip(t), method="native")
        for i, t in enumerate(raw_pages, start=1)
        if _safe_strip(t)
    ]


def _is_low_quality_native(text: str, page_count: int) -> bool:
    stripped = _safe_strip(text)
    if not has_meaningful_text(stripped):
        return False
    if len(stripped) < MIN_TEXT_CHARS:
        return True
    if _alnum_ratio(stripped) < MIN_ALNUM_RATIO_NATIVE:
        return True
    if page_count > 0 and len(stripped.split()) / page_count < MIN_WORDS_PER_PAGE:
        return True
    return False
