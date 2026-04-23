"""Application configuration with environment variable support."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8500
    debug: bool = False

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_expiry_hours: int = 24

    # LLM
    llm_backend: str = "llamacpp"
    llm_model_path: str = "data/models/model.gguf"
    llm_openai_base_url: str = ""
    llm_openai_api_key: str = ""
    llm_openai_model: str = ""
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.7

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_batch_size: int = 32

    # Retrieval
    retrieval_top_k: int = 5
    retrieval_use_mmr: bool = False
    retrieval_use_reranker: bool = False
    reranker_model_path: str = "data/models/bge-reranker-base"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Storage
    data_dir: Path = Path("data")
    db_url: str = "sqlite:///data/ilin.db"

    model_config = {"env_prefix": "ILIN_", "extra": "ignore"}


settings = Settings()
