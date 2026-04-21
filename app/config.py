from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./flashcards.db"

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama3-8b-8192"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Text chunking
    max_chunk_size: int = 2000
    max_chunk_overlap: int = 200

    # Flashcard generation
    default_num_cards: int = 10
    max_num_cards: int = 30

    # File upload
    max_file_size_mb: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
