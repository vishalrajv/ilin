"""Tests for text chunking."""

from ilin.core.chunker import chunk_text
from ilin.core.parser import TextChunk


def test_chunk_small_text_unchanged():
    """Text shorter than chunk_size returns as single chunk."""
    chunks = [TextChunk(text="Short text", metadata={}, source_file="test.txt")]
    result = chunk_text(chunks, chunk_size=500, chunk_overlap=50)
    assert len(result) == 1
    assert result[0].text == "Short text"


def test_chunk_large_text_splits():
    """Text larger than chunk_size splits into multiple chunks."""
    large_text = "word " * 200  # ~1000 chars
    chunks = [
        TextChunk(
            text=large_text, metadata={"source": "test.txt"}, source_file="test.txt"
        )
    ]
    result = chunk_text(chunks, chunk_size=200, chunk_overlap=20)
    assert len(result) > 1


def test_chunk_preserves_metadata():
    """Chunked results inherit original metadata."""
    chunk = TextChunk(
        text="line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10",
        metadata={"source": "doc.pdf", "file_type": "pdf"},
        page_number=3,
        source_file="doc.pdf",
    )
    result = chunk_text([chunk], chunk_size=30, chunk_overlap=5)
    for r in result:
        assert r.metadata["source"] == "doc.pdf"
        assert r.page_number == 3
        assert r.source_file == "doc.pdf"
