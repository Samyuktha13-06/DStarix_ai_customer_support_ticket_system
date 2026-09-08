from functools import lru_cache

# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Customer Support System"
    app_env: str = "development"
    log_level: str = "INFO"

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-20b"

    database_url: str = "sqlite:///./data/support.db"
    chroma_persist_directory: str = "./data/chroma"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()