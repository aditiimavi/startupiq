"""Vector store — FAISS-based production implementation."""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

__all__ = [
    "index_documents",
]


# simple in-memory/global store (Streamlit-safe approach)
_VECTORSTORE = None


def index_documents(
    chunks: list[Document],
    embeddings: Embeddings,
    reset: bool = False,
):
    """
    FAISS-based indexing (production-safe, Streamlit-friendly)
    """

    global _VECTORSTORE

    if not chunks:
        return _VECTORSTORE

    texts = [doc.page_content for doc in chunks]

    if reset or _VECTORSTORE is None:
        _VECTORSTORE = FAISS.from_documents(chunks, embeddings)
    else:
        _VECTORSTORE.add_documents(chunks)

    return _VECTORSTORE