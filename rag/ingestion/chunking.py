"""Smart chunking with rich metadata for ChromaDB retrieval."""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.ingestion.config import (
    CHUNK_OVERLAP_CHARS,
    CHUNK_OVERLAP_TOKENS,
    CHUNK_SIZE_CHARS,
    CHUNK_SIZE_TOKENS,
)
from rag.ingestion.models import PageContent
from rag.ingestion.text_cleaning import clean_text

# Prefer token-based lengths when tiktoken is available
try:
    import tiktoken

    _ENCODING = tiktoken.get_encoding("cl100k_base")

    def _token_length(text: str) -> int:
        return len(_ENCODING.encode(text))

    _CHUNK_SIZE = CHUNK_SIZE_TOKENS
    _CHUNK_OVERLAP = CHUNK_OVERLAP_TOKENS
    _LENGTH_FN = _token_length
except ImportError:
    _CHUNK_SIZE = CHUNK_SIZE_CHARS
    _CHUNK_OVERLAP = CHUNK_OVERLAP_CHARS
    _LENGTH_FN = len


def chunk_text(
    pages: list[PageContent],
    source_filename: str,
    file_hash: str,
) -> list[Document]:
    """
    Split page-level text into semantic chunks with metadata.

    Metadata per chunk:
        - source: file name
        - page: page number
        - chunk_index: global index within file
        - file_hash: deduplication id
        - extraction_method: native
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        length_function=_LENGTH_FN,
        separators=["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " ", ""],
        is_separator_regex=False,
    )

    documents: list[Document] = []
    chunk_index = 0

    for page in pages:
        text = clean_text(page.text)
        if not text:
            continue

        page_doc = Document(
            page_content=text,
            metadata={
                "source": source_filename,
                "page": page.page_number,
                "file_hash": file_hash,
                "extraction_method": page.method,
            },
        )
        page_chunks = splitter.split_documents([page_doc])

        for chunk in page_chunks:
            chunk.metadata["chunk_index"] = chunk_index
            documents.append(chunk)
            chunk_index += 1

    return documents
