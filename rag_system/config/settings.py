from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str = Field(default="", validation_alias="OPENROUTER_API_KEY")
    openrouter_llm_model: str = "anthropic/claude-sonnet-20241022"
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_documents"

    database_url: str = "postgresql+psycopg://rag_user:rag_pass@localhost:5432/rag"

    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    use_reranker: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
