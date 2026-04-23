"""Recursive character text chunking with overlap."""

from ilin.core.parser import TextChunk


def chunk_text(
    chunks: list[TextChunk], chunk_size: int = 500, chunk_overlap: int = 50
) -> list[TextChunk]:
    """Split text chunks into smaller overlapping pieces using recursive character splitting."""
    result = []
    for chunk in chunks:
        sub_chunks = _split_text(chunk.text, chunk_size, chunk_overlap)
        for i, sub_text in enumerate(sub_chunks):
            if sub_text.strip():
                result.append(
                    TextChunk(
                        text=sub_text,
                        metadata={**chunk.metadata, "chunk_index": i},
                        page_number=chunk.page_number,
                        source_file=chunk.source_file,
                    )
                )
    return result


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Recursively split text by decreasing separator priority (Markdown aware)."""
    if len(text) <= chunk_size:
        return [text]

    # CHANGED: Added Markdown headers to retain semantic structure
    separators = ["\n# ", "\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " ", ""]
    
    for separator in separators:
        if separator == "":
            return _hard_split(text, chunk_size, overlap)

        parts = text.split(separator)
        if len(parts) <= 1:
            continue

        if max(len(p) for p in parts) > chunk_size:
            continue

        return _merge_parts(parts, separator, chunk_size, overlap)

    return [text]


def _hard_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text by character count when no natural separator works."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def _merge_parts(
    parts: list[str], separator: str, chunk_size: int, overlap: int
) -> list[str]:
    """Merge list of parts into chunks of approximately chunk_size."""
    chunks = []
    current = ""
    for part in parts:
        if not part.strip():
            continue
        candidate = current + separator + part if current else part
        if len(candidate) > chunk_size and current:
            chunks.append(current)
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = overlap_text + separator + part if overlap_text.strip() else part
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
