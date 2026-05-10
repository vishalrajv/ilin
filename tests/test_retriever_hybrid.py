"""Tests for hybrid search in Retriever."""

import numpy as np
import pytest

from ilin.core.retriever import Retriever
from ilin.storage.vector_store import VectorStore


class DummyEmbedder:
    def embed_query(self, query):
        return np.random.rand(384).astype(np.float32)


@pytest.fixture
def test_retriever(tmp_path, monkeypatch):
    """Retriever fixture."""
    monkeypatch.setattr("ilin.config.settings.data_dir", tmp_path)
    monkeypatch.setattr("ilin.config.settings.retrieval_use_reranker", False)
    monkeypatch.setattr("ilin.config.settings.retrieval_use_mmr", False)
    return Retriever(embedder=DummyEmbedder())


def test_hybrid_search(test_retriever, tmp_path, monkeypatch):
    """Test that BM25 catches exact keyword matches when Dense vectors are random."""
    monkeypatch.setattr("ilin.config.settings.data_dir", tmp_path)
    store = VectorStore(topic_id=1)

    # Create chunks
    metadatas = [
        {"text": "The HTTP protocol is widely used.", "source": "doc1", "document_id": 1},
        {"text": "HTTPS is secure HTTP.", "source": "doc1", "document_id": 1},
        {"text": "TCP IP stack handles transport.", "source": "doc1", "document_id": 1},
        {"text": "XYZACRONYM is a completely random acronym for testing.", "source": "doc2", "document_id": 2},
    ]
    # Dense embeddings that completely fail (random noise)
    embeddings = np.random.rand(4, 384).astype(np.float32)
    store.add(embeddings, metadatas)

    # query
    results = test_retriever.retrieve(topic_id=1, query="XYZACRONYM", top_k=4)

    # BM25 should pick up XYZACRONYM and rank it highly via RRF
    found = False
    for res in results:
        if "XYZACRONYM" in res["metadata"]["text"]:
            found = True
            break

    assert found, "Hybrid search failed to find exact acronym match via BM25."
