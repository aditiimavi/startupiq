from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


class RAGPipeline:

    def __init__(self, persist_dir: str = "vector_db"):

        self.persist_dir = persist_dir

        # embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # load FAISS index safely
        try:
            self.vectorstore = FAISS.load_local(
                self.persist_dir,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception:
            # if not exists → create empty index later
            self.vectorstore = None

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )

    # -------------------------
    # INGESTION
    # -------------------------
    def ingest_pdf_paths(self, paths: List[str]) -> int:
        all_chunks = []

        for path in paths:
            try:
                loader = PyPDFLoader(path)
                docs = loader.load()
            except Exception as e:
                print(f"PDF load failed: {path} → {e}")
                continue

            if not docs:
                continue

            chunks = self.splitter.split_documents(docs)
            chunks = [c for c in chunks if c.page_content.strip()]
            all_chunks.extend(chunks)

        if not all_chunks:
            return 0

        # create vectorstore if missing
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(
                all_chunks,
                self.embeddings
            )
        else:
            self.vectorstore.add_documents(all_chunks)

        # persist locally (safe for Streamlit)
        self.vectorstore.save_local(self.persist_dir)

        return len(all_chunks)

    # -------------------------
    # RETRIEVAL
    # -------------------------
    def retrieve(self, query: str, k: int = 4):
        if self.vectorstore is None:
            return "", []

        docs = self.vectorstore.similarity_search(query, k=k)

        context = "\n\n".join(d.page_content for d in docs)

        return context, docs

    # -------------------------
    # REPORT GENERATION
    # -------------------------
    def generate_report(self, query: str, k: int = 4):
        if self.vectorstore is None:
            return "No vector database found. Please upload PDFs first."

        docs = self.vectorstore.similarity_search(query, k=k)

        if not docs:
            return "No relevant information found in documents."

        context = "\n\n".join(d.page_content for d in docs)

        return f"""
StartupIQ Analysis Report

Query:
{query}

Relevant Insights:
{context}

Summary:
Based on the uploaded documents, these are the most relevant insights retrieved from the knowledge base.
"""