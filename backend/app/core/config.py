from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "RepoPilot AI"
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 1440
    cors_origins: str = "http://localhost:5173"

    database_url: str = "postgresql+psycopg2://repopilot:repopilot@localhost:5432/repopilot"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "repo_chunks"
    qdrant_api_key: str = ""

    github_token: str = ""

    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_timeout_seconds: int = 90

    max_repo_files: int = 350
    max_file_bytes: int = 180_000
    chunk_lines: int = 90
    chunk_overlap_lines: int = 15

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    @property
    def cors_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
