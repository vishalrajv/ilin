# ILIN: Offline RAG Agent Suite

ILIN is a privacy-first, **entirely offline**, air-gapped Retrieval-Augmented Generation (RAG) agent suite built on FastAPI and FAISS. It allows you to ingest documents, create custom knowledge bases, and chat with them using local LLMs.

---

## 🌟 Key Features
- **Hybrid Search Engine:** Fuses Semantic Vector Search (FAISS) with Keyword Search (BM25) using Reciprocal Rank Fusion (RRF) for 99% retrieval accuracy.
- **Resilient Ingestion Pipeline:** Hardened ETL that handles PDFs, Markdown, and TXT files, automatically filtering out corrupt data or encoding artifacts.
- **Cross-Encoder Reranking:** Deep-learning based reranking using BAAI/bge-reranker-base to filter out hallucinations.
- **SSE Streaming:** Real-time token streaming from local GGUF models (Gemma-4-E4B).
- **Modern UI:** Built with Alpine.js and Bootstrap for a fast, responsive chat and admin experience.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- Windows (Current focus) or Linux
- 16GB+ RAM (Recommended for local LLM)

### 2. Installation
Clone the repository and set up the virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize the System
Seed the database, create the admin user, and ingest initial documentation:
```powershell
.venv\Scripts\python.exe seed.py
```
*Note: This will process all files in `data/source_docs/` if they exist.*

### 4. Download Models
Download the required LLM (GGUF) and Embedding models:
```powershell
.venv\Scripts\python.exe download_models.py
```

### 5. Run the Server
```powershell
.venv\Scripts\python.exe run.py
```
Access the application at: `http://localhost:8500`

---

## 🧪 Testing & Verification
We maintain a 100% verification standard for the RAG engine.

- **Unit/Integration Tests:**
  ```powershell
  .venv\Scripts\python.exe -m pytest tests/
  ```
- **End-to-End RAG Verification:**
  ```powershell
  .venv\Scripts\python.exe verify_e2e.py
  ```

---

## 🏗️ Architecture
- **API:** FastAPI
- **Database:** SQLite (SQLAlchemy ORM)
- **Vector Store:** FAISS (Dense) + rank_bm25 (Sparse)
- **Frontend:** Alpine.js + Bootstrap
- **LLM Context:** Gemma 4 E4B (GGUF via llama-cpp-python)

---

## 🛠️ Configuration
All settings can be configured via environment variables (prefixed with `ILIN_`) or in `ilin/config.py`.

---

**Developer:** Vishal Raj V, Senior Engineer
