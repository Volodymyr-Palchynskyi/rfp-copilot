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
    # Used when the primary model is rate limited, overloaded or times out. Empty disables fallback.
    GEMINI_FALLBACK_MODEL: str = ""
    GEMINI_TIMEOUT_S: int = 90
    # USD per 1M tokens, used for cost estimates. 0 disables (prices change, set them in .env).
    PRICE_INPUT_PER_MTOK: float = 0.0
    PRICE_OUTPUT_PER_MTOK: float = 0.0

    # Abuse protection for the public demo
    MAX_BRIEF_CHARS: int = 4000
    RATE_LIMIT_GENERATIONS: int = 5  # generations per client per window
    RATE_LIMIT_SEARCHES: int = 30  # knowledge searches per client per window
    RATE_LIMIT_WINDOW_S: int = 600
    MAX_CONCURRENT_GENERATIONS: int = 3
    ADMIN_TOKEN: str = ""  # protects POST /knowledge/ingest; empty disables the endpoint

    # RAG configuration
    EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIM: int = 768
    KNOWLEDGE_DIR: str = "data/past_projects"
    QDRANT_PATH: str = ".qdrant"  # embedded local mode, no server needed
    QDRANT_URL: str = ""  # set to use a real Qdrant server instead of QDRANT_PATH
    QDRANT_COLLECTION: str = "past_projects"
    RAG_TOP_K: int = 8
    # Reranking: vector search proposes candidates above a low floor, an LLM judge decides.
    RERANK_ENABLED: bool = True
    RERANK_MODEL: str = ""  # empty = same model as GEMINI_MODEL
    RERANK_TIMEOUT_S: int = 30
    RERANK_MIN_RELEVANCE: int = 2  # judge scale 0-3, keep projects scoring at least this
    RAG_CANDIDATE_MIN_SCORE: float = 0.60
    RAG_MAX_CANDIDATES: int = 5
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