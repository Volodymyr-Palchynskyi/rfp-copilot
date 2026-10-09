from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings schema.
    Reads environment variables and .env file automatically with runtime validation.
    """

    # Project metadata
    PROJECT_NAME: str = "RFP Proposal Copilot API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Server settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Gemini AI configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.7-flash"

    # RAG configuration
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIM: int = 768
    KNOWLEDGE_DIR: str = "data/past_projects"
    QDRANT_PATH: str = ".qdrant"  # embedded local mode, no server needed
    QDRANT_URL: str = ""  # set to use a real Qdrant server instead of QDRANT_PATH
    QDRANT_COLLECTION: str = "past_projects"
    RAG_TOP_K: int = 8
    RAG_MIN_SCORE: float = 0.70  # chosen by the retrieval eval threshold sweep (evals/results/retrieval.md)

    # CORS configuration (list of allowed frontend origins)
    CORS_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]

    # Configuration to load from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables not defined here
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Cached singleton provider for application settings.
    Ensures .env is read only once upon startup.
    """
    return Settings()


# Export pre-instantiated singleton for direct convenience
settings = get_settings()