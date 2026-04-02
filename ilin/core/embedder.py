"""sentence-transformers embedding wrapper with batch support."""

# Developer: Vishal Raj V, Senior Engineer

import numpy as np
from sentence_transformers import SentenceTransformer

from ilin.config import settings
from ilin.core.parser import TextChunk


class Embedder:
    """Manages sentence-transformers model and batch embedding."""

    def __init__(self, model_name: str | None = None):
        """Load the embedding model. Downloads on first use if not cached."""
        self.model = SentenceTransformer(model_name or settings.embedding_model)

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Encode a list of strings into normalized embedding vectors."""
        embeddings = self.model.encode(
            texts, batch_size=settings.embedding_batch_size, show_progress_bar=False
        )
        # L2 normalize for inner product similarity in FAISS
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norms

    def embed_query(self, text: str) -> np.ndarray:
        """Encode a single query string into a normalized embedding vector."""
        return self.embed_texts([text])[0]
