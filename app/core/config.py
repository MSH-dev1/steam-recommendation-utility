"""Application configuration. Environment variables only."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Steam Recommendation Utility"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    base_url: str = "http://localhost:8000"

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/steamrec"

    # Steam (filled in at step 2-3, may be empty at start)
    steam_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
