from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

class RAGPipeline:

    def __init__(self, persist_dir: str = "vector_db"):

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150
        )

    # -------------------------
    # REQUIRED FUNCTION (FIX)
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

        self.vectorstore.add_documents(all_chunks)

        return len(all_chunks)

        print("TOTAL CHUNKS:", len(all_chunks))

        # ----------------------------
    # RETRIEVAL
    # ----------------------------
    def retrieve(self, query: str, k: int = 4):
        docs = self.vectorstore.similarity_search(query, k=k)

        context = "\n\n".join(
            d.page_content for d in docs
        )

        return context, docs

    # ----------------------------
    # REPORT GENERATION
    # ----------------------------
    def generate_report(self, query: str, k: int = 4):
        docs = self.vectorstore.similarity_search(query, k=k)

        if not docs:
            return "No relevant information found in documents."

        context = "\n\n".join(
            d.page_content for d in docs
        )

        report = f"""
StartupIQ Analysis Report

Query:
{query}

Relevant Insights:
{context}

Summary:
Based on the uploaded documents, these are the most relevant insights retrieved from the knowledge base.
"""

        return report