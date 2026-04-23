# GEMINI.md - Agent Context & Continuity
# Project: ILIN Offline RAG Agent Suite
# Last Updated: 2026-04-23

---

## 🎯 Project Essence
ILIN is a privacy-first, **entirely offline**, air-gapped Retrieval-Augmented Generation (RAG) agent suite.
- **Backend:** FastAPI + SQLAlchemy (SQLite)
- **Frontend:** Alpine.js + Bootstrap (SSE Streaming)
- **Vector Engine:** FAISS (Dense) + rank_bm25 (Sparse)
- **Model:** Gemma 4 E4B (GGUF via llama-cpp-python)
- **Reranker:** BAAI/bge-reranker-base (CrossEncoder)

---

## 🏗️ Core Architecture (Hybrid Search)
The system uses a **Hybrid Search Pipeline** with **Reciprocal Rank Fusion (RRF)**:
1. **Dense Retrieval (FAISS):** Semantic matching using `all-MiniLM-L6-v2`.
2. **Sparse Retrieval (BM25):** Keyword matching using `rank_bm25`.
3. **Fusion (RRF):** Merges results (60% Dense / 40% Sparse).
4. **Hardened Ingestion:** Resilient parsers (PDF, TXT, MD) that drop garbled/null characters.
5. **Cross-Encoder Reranking:** Final relevance scoring and hallucination dropping (threshold: -2.0).

---

## 📍 Current State (Phase 4 Completed)
- [x] **Hybrid Retrieval:** Parallel FAISS + BM25 integrated into `Retriever`.
- [x] **Hardened ETL:** Resilient `ParserRegistry` and directory ingestion loop in `seed.py`.
- [x] **E2E Verified:** `verify_e2e.py` confirms SSE streaming, RRF fusion, and Cross-Encoder filtering.
- [x] **Mocks:** `llama_cpp` is currently mocked in `.venv` to bypass Windows build issues (nmake/cmake).

---

## 🧠 Lessons Learned & Technical Gotchas
- **Windows Compilers:** `llama-cpp-python` often fails to build on Windows without MSVC/NMake. If it fails, use the mock in `.venv/Lib/site-packages/llama_cpp/__init__.py` for testing API logic.
- **BM25 IDF Sensitivity:** BM25 scores are `0.0` if a term appears in half or more of the documents. Test cases must use at least 3-4 documents to ensure positive IDF scores for keywords.
- **RRF Fetch Size:** When using RRF, fetch `top_k * 4` from both indices to ensure enough overlap for meaningful fusion before slicing to the final `top_k`.
- **Port Conflict:** Default port is `8500`. If you see `[Errno 10048]`, check for existing `python.exe` processes on that port.

---

## 🛠️ Verified Commands
```powershell
# Always use the virtual environment
.venv\Scripts\python.exe run.py

# Initialize & Ingest (Processes data/source_docs/)
.venv\Scripts\python.exe seed.py

# Run Full Test Suite
.venv\Scripts\python.exe -m pytest tests/

# Run E2E RAG Verification
.venv\Scripts\python.exe verify_e2e.py
```

---

## 📜 Repository Structure
- `ilin/api/`: FastAPI routers and app entry (`main.py`).
- `ilin/core/`: RAG logic (parser, chunker, embedder, generator, retriever, engine).
- `ilin/storage/`: SQLite database models and FAISS/BM25 `VectorStore`.
- `data/models/`: Local GGUF and Cross-Encoder model storage.
- `data/source_docs/`: Source directory for `seed.py` ingestion.
