from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    # Load the backend/.env file relative to this config file so the app
    # finds environment variables even when started from the repository root.
    model_config = SettingsConfigDict(env_file=str(_ENV_PATH), env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = Field(default="AI Adaptive Learning Platform API")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_adaptive_learning")
    jwt_secret_key: str = Field(default="JBbKWL84jmW7WHJtGU3WcZ0bEZWM1ArMCEbNX0v0rJb")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=30)
    jwt_refresh_token_expires_days: int = Field(default=7)
    groq_api_key: str = Field(default="")
    groq_chat_model: str = Field(default="qwen/qwen3.8-27b")
    ai_chunk_size: int = Field(default=1200)
    ai_chunk_overlap: int = Field(default=180)
    ai_retrieval_top_k: int = Field(default=5)
    ai_vector_store_path: str = Field(default="app/storage/cache/ai/vectorstore")
    ai_chunk_store_path: str = Field(default="app/storage/cache/ai/chunks.json")
    ai_generated_asset_dir: str = Field(default="app/storage/cache/ai/generated")
    ai_use_fallback: bool = Field(default=False)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
