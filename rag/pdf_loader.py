"""PDF loading — delegates to ingestion module."""

from pathlib import Path

from rag.ingestion.pdf_extraction import extract_pdf_text


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract and clean full text from a PDF (PyPDF + pdfminer)."""
    result = extract_pdf_text(pdf_path)
    return result.full_text


def extract_text_from_pdfs(pdf_paths: list[str | Path]) -> dict[str, str]:
    documents: dict[str, str] = {}
    for pdf_path in pdf_paths:
        path = Path(pdf_path)
        try:
            documents[path.name] = extract_text_from_pdf(path)
        except Exception:
            documents[path.name] = ""
    return documents
