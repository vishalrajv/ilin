# Comprehensive Agentic Orchestration Plan: ILIN Offline RAG

## Context Anchor (Do Not Delete)
This is an entirely offline, air-gapped Retrieval-Augmented Generation (RAG) agent suite built on FastAPI and FAISS.
- **LLM Context:** Gemma 4 E4B (`gemma-4-E4B-it-Q4_K_M.gguf` running via `llama.cpp` streaming).
- **Embedder:** `all-MiniLM-L6-v2` via `sentence-transformers`.
- **Reranker:** `BAAI/bge-reranker-base` via CrossEncoder.
- **Frontend State:** Alpine.js + Bootstrap (Fully functional, streaming API integrated).

---

## Phase 1: Environment & Foundational RAG Mechanics (COMPLETED)
- [x] Hardened `rag_engine.py` with custom Gemma instruct template (`<start_of_turn>user`).
- [x] Configured offline model fetcher scripts targeting HuggingFace infrastructure.
- [x] Implemented Maximal Marginal Relevance (MMR) in `retriever.py`.
- [x] Deployed structural Markdown-aware Semantic Chunking in `chunker.py`.
- [x] Hooked Cross-Encoder Re-Ranking into the tail-end of the retrieval pipeline.

---

## Phase 2: Hybrid Search Integration (COMPLETED)
**Suggested Subagent:** `rag-implementation` | **Scope:** `requirements.txt`, `vector_store.py`, `retriever.py`
*Objective: Vector search fails on exact keyword matching. We must fuse Sparse Lexical Search (BM25) with our existing Dense Vector pipeline (FAISS).*
- [x] **Task 2.1:** Inject `rank_bm25` library into `requirements.txt` and verify virtual environment.
- [x] **Task 2.2:** Update `vector_store.py` to maintain a dual-index system. It must construct and disk-persist a `BM25Okapi` sparse corpus synchronized with the FAISS dense indices.
- [x] **Task 2.3:** Rewrite `retriever.py` `retrieve()` logic to run parallel searches.
- [x] **Task 2.4:** Implement Reciprocal Rank Fusion (RRF) on the resulting Dense and Sparse arrays (e.g., 60% Dense / 40% Sparse weighting) before passing the aggregate pool into the Cross-Encoder pipeline.

---

## Phase 3: Knowledge Base Ingestion Engine (COMPLETED)
**Suggested Subagent:** Python Platform Engineer | **Scope:** `parser.py`, `seed.py`, `rag_engine.py`
*Objective: The pipeline is built, but cannot accept raw data resiliently. We need an unbreakable ETL loop.*
- [x] **Task 3.1:** Hardened Parsing: Upgrade `parser.py` (ParserRegistry) to process raw PDFs, TXT, and Markdown files safely, handling encoding errors or unprintable control characters without crashing.
- [x] **Task 3.2:** Write the unified ingestion loop within `seed.py` that recursively steps through `data/source_docs/`, invoking `rag_engine.index_document()`.
- [x] **Task 3.3:** Link the updated `add_to_topic_index` to properly insert chunks into both FAISS and the new BM25 index seamlessly without race conditions.

---

## Phase 4: Full Stack Evaluation & Observability (COMPLETED)
**Suggested Subagent:** Validation Agent | **Scope:** `tests/`, `api/main.py`, UI
*Objective: We do not mark the pipeline complete without mathematical and visual proof that it works.*
- [x] **Task 4.1:** Write test hooks checking if `retriever.py` successfully executes Hybrid Search returning targeted, exact-matching acronyms.
- [x] **Task 4.2:** Boot the FastAPI server. Perform an end-to-end question on the Alpine.js frontend. Verify that `gemma-4-E4B-it-Q4_K_M.gguf` actually streams responses back over Server-Sent Events.
- [x] **Task 4.3:** Verify the Cross-Encoder properly drops hallucinations by inspecting terminal logging vectors during generation.

---

### Agentic Directives for Context Retrieval
If the primary agent's context is reset, immediately read this document and invoke a single Subagent targeting the first un-checked Task. Subagents must never bleed out of their assigned scope. All completed logic must pass local unit-verification before modifying checkboxes.
.
