from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str = Field(default="", validation_alias="OPENROUTER_API_KEY")
    openrouter_llm_model: str = Field(
        default="anthropic/claude-sonnet-20241022",
        validation_alias="OPENROUTER_MODEL",
    )
    openrouter_embedding_model: str = "openai/text-embedding-3-small"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    qdrant_host: str = Field(default="localhost", validation_alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, validation_alias="QDRANT_PORT")
    qdrant_collection: str = "rag_documents"

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    postgres_user: str = Field(default="rag_user", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="rag_pass", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="rag_db", validation_alias="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5
    reranker_model: str = Field(
        default="rerank-multilingual-v3.0",
        validation_alias="RERANKER_MODEL",
    )
    use_reranker: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
