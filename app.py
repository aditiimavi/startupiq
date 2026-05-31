"""
StartupIQ — Multi-Agent Startup Intelligence Platform
Stable production-safe Streamlit version (HuggingFace + Chroma RAG FIXED)
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agents.orchestrator import StartupIQOrchestrator
from rag.retriever import RAGPipeline
from ui.components import (
    NAV_ANALYSIS,
    NAV_DASHBOARD,
    NAV_DOCUMENTS,
    NAV_REPORT,
    init_agent_states,
    render_sidebar_nav,
    render_brand_hero,
    render_metric_card,
    render_health_score,
)
from ui.health import compute_health_score
from ui.styles import inject_custom_css

# -----------------------------
# CONFIG
# -----------------------------
load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

VECTOR_DB_PATH = BASE_DIR / "vector_db"


# -----------------------------
# FILE HANDLING
# -----------------------------
def _save_uploaded_files(uploaded_files) -> list[Path]:
    saved = []

    if not uploaded_files:
        return saved

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for f in uploaded_files:
        path = UPLOAD_DIR / f.name

        with open(path, "wb") as out:
            out.write(f.getbuffer())

        saved.append(path.resolve())

    return saved


# -----------------------------
# HUGGING FACE EMBEDDINGS + CHROMA
# -----------------------------
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=str(VECTOR_DB_PATH),
    embedding_function=embeddings
)


# -----------------------------
# SESSION STATE
# -----------------------------
def _init_session_state():
    defaults = {
        "siq_nav_page": NAV_DASHBOARD,
        "indexed": False,
        "chunk_count": 0,
        "uploaded_count": 0,
        "workflow_result": None,
        "specialist_outputs": None,
        "final_report": None,
        "last_question": "",
        "agent_states": init_agent_states(),
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# -----------------------------
# HEALTH SCORE
# -----------------------------
def _get_health():
    return compute_health_score(
        indexed=st.session_state.indexed,
        chunk_count=st.session_state.chunk_count,
        has_report=st.session_state.final_report is not None,
        specialist_outputs=st.session_state.specialist_outputs,
        uploaded_file_count=st.session_state.uploaded_count,
    )


# -----------------------------
# DASHBOARD
# -----------------------------
def _page_dashboard():
    render_brand_hero("Startup Intelligence Command Center")

    health = _get_health()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric_card("Health Score", str(health.score), health.tier)

    with c2:
        render_metric_card("Documents", str(st.session_state.uploaded_count), "Uploaded")

    with c3:
        render_metric_card("Chunks", str(st.session_state.chunk_count), "Indexed")

    with c4:
        score = "—"
        label = "Run analysis"

        if st.session_state.workflow_result:
            try:
                v = st.session_state.workflow_result.viability
                score = str(v.overall_score)
                label = "Viability Score"
            except Exception:
                pass

        render_metric_card("Score", score, label)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        render_health_score(health)

    with col2:
        st.subheader("System Status")
        st.write("HuggingFace Embeddings: OK")
        st.write("ChromaDB: OK" if vectorstore else "Not Ready")
        st.write("Index:", "Ready" if st.session_state.indexed else "Not Ready")
        st.write("Report:", "Available" if st.session_state.final_report else "None")


# -----------------------------
# DOCUMENTS PAGE (RAG FIXED)
# -----------------------------
def _page_documents():
    render_brand_hero("Upload & Index Startup PDFs")

    files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Index Documents", type="primary"):
        if not files:
            st.warning("Upload at least one file")
            return

        paths = _save_uploaded_files(files)

        # FIXED: PASS vectorstore into RAGPipeline
        pipeline = RAGPipeline()

        st.write("Indexed files:", [p.name for p in paths])

        count = pipeline.ingest_pdf_paths([str(p) for p in paths])

        if count == 0:
            st.error("No text extracted from PDFs")
            return

        st.session_state.indexed = True  
        st.session_state.chunk_count = count
        st.session_state.uploaded_count = len(files)

        st.success(f"Indexed {count} chunks successfully")


# -----------------------------
# ANALYSIS PAGE
# -----------------------------

def _page_analysis():
    render_brand_hero("AI Startup Analysis Engine")

    # ---- session state safety ----
    if "workflow_result" not in st.session_state:
        st.session_state.workflow_result = None

    if "final_report" not in st.session_state:
        st.session_state.final_report = None

    if "indexed" not in st.session_state:
        st.session_state.indexed = False

    # ---- input ----
    question = st.text_area("Ask a question")

    # ---- button ----
    if st.button("Run Analysis"):

        st.write("BUTTON CLICKED")

        if not question.strip():
            st.warning("Enter a question")
            return

        if not st.session_state.indexed:
            st.warning("Please index documents first")
            return

        try:
            st.write("Creating orchestrator...")
            orchestrator = StartupIQOrchestrator()

            st.write("Running analysis pipeline...")
            result = orchestrator.run(question)

            st.write("Pipeline finished successfully")

            # ---- safety checks ----
            if not result:
                st.error("No result returned from orchestrator")
                return

            st.write("DEBUG: result received")

            if not hasattr(result, "final_report") or result.final_report is None:
                st.error("final_report is missing")
                return

            st.write("DEBUG REPORT OBJECT:")
            st.write(result.final_report)

            content = getattr(result.final_report, "content", "")

            st.write("DEBUG REPORT CONTENT (preview):")
            st.write(content[:500])

            # ---- store in session ----
            st.session_state.workflow_result = result
            st.session_state.final_report = result.final_report

            st.success("Analysis complete")

        except Exception as e:
             st.error(f"Error during analysis: {e}")


# -----------------------------
# REPORT PAGE
# -----------------------------
def _page_report():
    if not st.session_state.final_report:
        st.info("No report generated yet")
        return

    st.markdown("## Final Report")
    st.write(getattr(st.session_state.final_report, "content", ""))


# -----------------------------
# MAIN APP
# -----------------------------
def main():
    st.set_page_config(page_title="StartupIQ", layout="wide")

    inject_custom_css()
    _init_session_state()

    with st.sidebar:
        render_sidebar_nav()

    page = st.session_state.siq_nav_page

    if page == NAV_DASHBOARD:
        _page_dashboard()

    elif page == NAV_DOCUMENTS:
        _page_documents()

    elif page == NAV_ANALYSIS:
        _page_analysis()

    elif page == NAV_REPORT:
        _page_report()

    else:
        _page_dashboard()


if __name__ == "__main__":
    main()