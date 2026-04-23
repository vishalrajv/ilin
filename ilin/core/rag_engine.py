"""RAG pipeline orchestration: parse, chunk, embed, index, retrieve, generate."""

# Developer: Vishal Raj V, Senior Engineer

from pathlib import Path
from typing import AsyncGenerator

from ilin.config import settings
from ilin.core.chunker import chunk_text
from ilin.core.embedder import Embedder
from ilin.core.generator import LLMBackend, get_llm_backend
from ilin.core.parser import ParserRegistry, TextChunk
from ilin.core.retriever import Retriever


class RAGEngine:
    """Orchestrates the full RAG pipeline."""

    def __init__(self):
        """Initialize RAG engine with shared components."""
        self.embedder = Embedder()
        self.retriever = Retriever(self.embedder)
        self.llm: LLMBackend | None = None

    def _get_llm(self) -> LLMBackend:
        """Get or create the LLM backend."""
        if self.llm is None:
            self.llm = get_llm_backend()
        return self.llm

    def index_document(self, file_path: Path) -> tuple[list[dict], any]:
        """Parse, chunk, and embed a document. Returns (metadatas, embeddings)."""
        # Parse
        text_chunks = ParserRegistry.parse_file(file_path)

        # Chunk
        split_chunks = chunk_text(text_chunks, settings.chunk_size, settings.chunk_overlap)

        # Embed
        texts = [c.text for c in split_chunks]
        embeddings = self.embedder.embed_texts(texts)

        # Build metadata
        metadatas = [
            {
                "text": c.text,
                "source_file": c.source_file,
                "page_number": c.page_number,
                "metadata": c.metadata,
            }
            for c in split_chunks
        ]

        return metadatas, embeddings

    def add_to_topic_index(self, topic_id: int, metadatas: list[dict], embeddings):
        """Add document chunks to a topic's FAISS index."""
        from ilin.storage.vector_store import VectorStore

        store = VectorStore(topic_id)
        store.add(embeddings, metadatas)

    def retrieve_context(self, topic_id: int, query: str) -> list[dict]:
        """Retrieve relevant context chunks for a query."""
        return self.retriever.retrieve(topic_id, query)

    def build_prompt(self, query: str, context: list[dict], chat_history: str = "") -> str:
        """Build the full prompt using Gemma Instruct formatting."""
        context_text = ""
        for i, item in enumerate(context, 1):
            source = item["metadata"].get("source_file", "unknown")
            page = item["metadata"].get("page_number", "")
            page_info = f", page {page}" if page else ""
            context_text += f"[{i}] {item['metadata']['text']}\n(source: {source}{page_info})\n\n"

        history_section = f"\nChat History:\n{chat_history}\n" if chat_history else ""

        instruction = (
            f"You are a helpful assistant. Answer the user's question based ONLY on the provided context.\n"
            f"If the answer cannot be found in the context, say \"I don't have enough information to answer that.\"\n\n"
            f"Context:\n{context_text}\n"
            f"{history_section}"
            f"Question: {query}"
        )

        # CHANGED: Wrapped with Gemma's <start_of_turn> tags for proper instruction-following
        return f"<start_of_turn>user\n{instruction}<end_of_turn>\n<start_of_turn>model\n"

    async def generate_response(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate streaming response from prompt."""
        llm = self._get_llm()
        async for chunk in llm.generate(prompt):
            yield chunk
