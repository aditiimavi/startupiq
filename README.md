# StartupIQ

**Multi-Agent Startup Intelligence Platform** — upload startup PDFs, ask questions, and receive a unified intelligence report powered by RAG and specialized AI agents.

## Features

- **Streamlit UI** for PDF upload and interactive Q&A
- **Production RAG ingestion**: PDF extraction (PyPDF + pdfminer), smart chunking, deduplication, ChromaDB
- **Five specialist agents**: Market Research, Competitor Analysis, Funding Advisor, Business Strategy
- **Report Generator**: synthesizes all agent outputs into one executive report

## Project Structure

```
StartupIQ/
├── app.py                 # Streamlit frontend
├── agents/                # Multi-agent system
├── rag/
│   └── ingestion/         # Document processing (chunking, Chroma)
├── uploads/               # Saved PDF uploads
├── requirements.txt
└── .env.example
```

## Setup

1. **Clone / open the project** and create a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

2. **Configure Gemini API key**:

   ```bash
   copy .env.example .env
   ```

   Edit `.env` and set `GOOGLE_API_KEY` from [Google AI Studio](https://aistudio.google.com/apikey).

3. **Run the app**:

   ```bash
   streamlit run app.py
   ```

## Workflow

1. Upload startup-related PDFs on the **Documents** page and click **Index Documents**.
2. Enter a startup question on the **Analysis** page.
3. Click **Run Multi-Agent Analysis**.
4. RAG retrieves relevant chunks; each agent analyzes independently; the Report Generator produces the final report.

## Tech Stack

- [Streamlit](https://streamlit.io/) — frontend
- [LangChain](https://python.langchain.com/) — orchestration
- [ChromaDB](https://www.trychroma.com/) — vector store
- [PyPDF](https://pypdf.readthedocs.io/) / pdfminer.six — PDF text extraction
- [Google Gemini](https://ai.google.dev/) — LLM and embeddings
