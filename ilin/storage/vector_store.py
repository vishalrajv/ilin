"""FAISS vector index management per topic."""

# Developer: Vishal Raj V, Senior Engineer

import json
from pathlib import Path

import faiss
import numpy as np

from ilin.config import settings


class VectorStore:
    """Manages a FAISS index for a single topic with metadata storage."""

    def __init__(self, topic_id: int):
        """Initialize vector store for a topic. Creates index dir if needed."""
        self.topic_id = topic_id
        self.index_dir = settings.data_dir / "indexes" / str(topic_id)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.index_dir / "faiss.index"
        self.metadata_path = self.index_dir / "metadata.jsonl"
        self.bm25_path = self.index_dir / "bm25_corpus.json"
        self.index = None
        self.metadata = []
        self.bm25_corpus = []
        self.bm25 = None
        self._load()

    def _load(self):
        """Load existing FAISS index and metadata from disk."""
        if self.index_path.exists() and self.metadata_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, encoding="utf-8") as f:
                self.metadata = [json.loads(line) for line in f]
        
        if self.bm25_path.exists():
            with open(self.bm25_path, encoding="utf-8") as f:
                self.bm25_corpus = json.load(f)
            if self.bm25_corpus:
                from rank_bm25 import BM25Okapi
                self.bm25 = BM25Okapi(self.bm25_corpus)

    def _save(self):
        """Persist FAISS index and metadata to disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            for entry in self.metadata:
                f.write(json.dumps(entry) + "\n")
        with open(self.bm25_path, "w", encoding="utf-8") as f:
            json.dump(self.bm25_corpus, f)

    def add(self, embeddings: np.ndarray, metadatas: list[dict]):
        """Add embedding vectors and their metadata to the index."""
        if self.index is None:
            dim = embeddings.shape[1] if embeddings.ndim == 2 else len(embeddings)
            self.index = faiss.IndexFlatIP(dim)
            self.metadata = []
            self.bm25_corpus = []

        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        # CHANGED: Verify document_id exists in metadata
        for meta in metadatas:
            if "document_id" not in meta:
                raise ValueError("Every metadata dictionary must include 'document_id'")

        self.index.add(np.ascontiguousarray(embeddings, dtype=np.float32))
        self.metadata.extend(metadatas)
        
        for meta in metadatas:
            text = meta.get("text", "")
            self.bm25_corpus.append(text.lower().split())
            
        if self.bm25_corpus:
            from rank_bm25 import BM25Okapi
            self.bm25 = BM25Okapi(self.bm25_corpus)
            
        self._save()

    def delete_document(self, document_id: int):
        """Remove all chunks belonging to a specific document and rebuild index."""
        if self.index is None or not self.metadata:
            return

        # 1. Identify indices to keep
        keep_indices = [
            i for i, meta in enumerate(self.metadata) 
            if meta.get("document_id") != document_id
        ]

        if len(keep_indices) == len(self.metadata):
            return  # Nothing to delete

        # 2. Extract vectors and metadata to keep
        new_metadata = [self.metadata[i] for i in keep_indices]
        new_bm25_corpus = [self.bm25_corpus[i] for i in keep_indices]
        
        if not keep_indices:
            # Everything was deleted
            self.index = None
            self.metadata = []
            self.bm25_corpus = []
            self.bm25 = None
        else:
            # Reconstruct keep vectors
            keep_vectors = np.array([self.index.reconstruct(i) for i in keep_indices])
            
            # 3. Rebuild FAISS index (IndexFlatIP doesn't support easy removals)
            dim = keep_vectors.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(np.ascontiguousarray(keep_vectors, dtype=np.float32))
            
            self.metadata = new_metadata
            self.bm25_corpus = new_bm25_corpus
            
            # 4. Re-initialize BM25
            from rank_bm25 import BM25Okapi
            self.bm25 = BM25Okapi(self.bm25_corpus)

        self._save()

    def search(
        self, query_embedding: np.ndarray, top_k: int | None = None, return_vectors: bool = False
    ) -> list[dict]:
        """Search for similar vectors. Returns list of {score, metadata, id, [vector]}."""
        if self.index is None or self.index.ntotal == 0:
            return []

        k = top_k or settings.retrieval_top_k
        k = min(k, self.index.ntotal)

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(
            np.ascontiguousarray(query_embedding, dtype=np.float32), k
        )

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            item = {"score": float(score), "metadata": self.metadata[idx], "id": int(idx)}
            if return_vectors:
                item["vector"] = self.index.reconstruct(int(idx))
            results.append(item)
        return results

    def search_bm25(self, query: str, top_k: int | None = None) -> list[dict]:
        """Search using BM25 sparse index."""
        if self.bm25 is None or not self.bm25_corpus:
            return []
            
        k = top_k or settings.retrieval_top_k
        k = min(k, len(self.bm25_corpus))
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        top_n = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_n:
            if scores[idx] > 0:
                results.append({
                    "score": float(scores[idx]), 
                    "metadata": self.metadata[idx],
                    "id": int(idx)
                })
        return results

    def delete(self):
        """Delete the entire topic index from disk."""
        import shutil

        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)
        self.index = None
        self.metadata = []
        self.bm25_corpus = []
        self.bm25 = None
