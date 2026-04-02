"""Tests for document parser pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from ilin.core.parser import (
    ParserRegistry,
    PDFParser,
    DOCXParser,
    TXTParser,
    TextChunk,
)


def test_txt_parser_parses_text(tmp_path: Path):
    """TXTParser reads plain text files."""
    file = tmp_path / "test.txt"
    file.write_text("Hello world\nSecond line")
    parser = TXTParser()
    chunks = parser.parse(file)
    assert len(chunks) == 1
    assert "Hello world" in chunks[0].text
    assert chunks[0].metadata["file_type"] == "txt"


def test_parser_registry_gets_txt_parser(tmp_path: Path):
    """ParserRegistry returns TXTParser for .txt files."""
    file = tmp_path / "test.txt"
    parser = ParserRegistry.get_parser(file)
    assert isinstance(parser, TXTParser)


def test_parser_registry_unsupported_extension(tmp_path: Path):
    """ParserRegistry raises ValueError for unsupported extensions."""
    file = tmp_path / "test.xyz"
    import pytest

    with pytest.raises(ValueError, match="Unsupported file type"):
        ParserRegistry.get_parser(file)


def test_text_chunk_has_metadata():
    """TextChunk contains expected fields."""
    chunk = TextChunk(
        text="test", metadata={"key": "value"}, page_number=1, source_file="test.pdf"
    )
    assert chunk.text == "test"
    assert chunk.metadata["key"] == "value"
    assert chunk.page_number == 1
    assert chunk.source_file == "test.pdf"
