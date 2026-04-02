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
        self.index = None
        self.metadata = []
        self._load()

    def _load(self):
        """Load existing FAISS index and metadata from disk."""
        if self.index_path.exists() and self.metadata_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, encoding="utf-8") as f:
                self.metadata = [json.loads(line) for line in f]

    def _save(self):
        """Persist FAISS index and metadata to disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            for entry in self.metadata:
                f.write(json.dumps(entry) + "\n")

    def add(self, embeddings: np.ndarray, metadatas: list[dict]):
        """Add embedding vectors and their metadata to the index."""
        if self.index is None:
            dim = embeddings.shape[1] if embeddings.ndim == 2 else len(embeddings)
            self.index = faiss.IndexFlatIP(dim)
            self.metadata = []

        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        self.index.add(np.ascontiguousarray(embeddings, dtype=np.float32))
        self.metadata.extend(metadatas)
        self._save()

    def search(
        self, query_embedding: np.ndarray, top_k: int | None = None
    ) -> list[dict]:
        """Search for similar vectors. Returns list of {score, metadata}."""
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
            results.append({"score": float(score), "metadata": self.metadata[idx]})
        return results

    def delete(self):
        """Delete the entire topic index from disk."""
        import shutil

        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)
        self.index = None
        self.metadata = []
