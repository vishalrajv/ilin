"""FAISS retrieval logic with embedding and result formatting."""

# Developer: Vishal Raj V, Senior Engineer

from ilin.config import settings
from ilin.core.embedder import Embedder
from ilin.storage.vector_store import VectorStore


class Retriever:
    """Retrieves relevant chunks from a topic's vector index."""

    def __init__(self, embedder: Embedder | None = None):
        """Initialize retriever with optional shared embedder."""
        self.embedder = embedder or Embedder()

    def retrieve(self, topic_id: int, query: str, top_k: int | None = None) -> list[dict]:
        """Embed query and retrieve top-k matching chunks from topic index."""
        store = VectorStore(topic_id)
        query_embedding = self.embedder.embed_query(query)
        results = store.search(query_embedding, top_k=top_k)
        return results
