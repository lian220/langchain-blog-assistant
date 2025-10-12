from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    anthropic_api_key: str
    tavily_api_key: str = ""
    pexels_api_key: str = ""

    # Blog content settings
    content_dir: str = "content/blog"

    # ChromaDB settings
    chroma_persist_dir: str = "./chroma_db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
