"""Tests for FAISS vector store."""

# Developer: Vishal Raj V, Senior Engineer

import numpy as np
import pytest

from ilin.storage.vector_store import VectorStore


@pytest.fixture
def vector_store(tmp_path, monkeypatch):
    """Create a vector store in a temp directory."""
    monkeypatch.setattr("ilin.config.settings.data_dir", tmp_path)
    store = VectorStore(topic_id=1)
    yield store


def test_add_and_search(vector_store):
    """Add embeddings and search returns results with scores."""
    embeddings = np.random.rand(3, 384).astype(np.float32)
    metadatas = [
        {"text": "chunk 1", "source": "doc1.pdf"},
        {"text": "chunk 2", "source": "doc1.pdf"},
        {"text": "chunk 3", "source": "doc2.pdf"},
    ]
    vector_store.add(embeddings, metadatas)
    assert vector_store.index.ntotal == 3

    query = embeddings[0]
    results = vector_store.search(query, top_k=1)
    assert len(results) == 1
    assert results[0]["metadata"]["text"] == "chunk 1"


def test_search_empty_index(vector_store):
    """Search on empty index returns empty list."""
    results = vector_store.search(np.random.rand(384).astype(np.float32))
    assert results == []


def test_delete(vector_store):
    """Delete removes index and metadata."""
    embeddings = np.random.rand(2, 384).astype(np.float32)
    vector_store.add(embeddings, [{"text": "a"}, {"text": "b"}])
    vector_store.delete()
    assert vector_store.index is None
    assert vector_store.metadata == []
