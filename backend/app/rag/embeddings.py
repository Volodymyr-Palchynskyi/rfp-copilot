from typing import Literal

from google import genai
from google.genai import types

from app.core.config import settings

TaskType = Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]

# Gemini embedding API accepts up to 100 inputs per request.
_BATCH_SIZE = 100


class Embedder:
    """Thin async wrapper over Gemini embeddings. Documents and queries use different task types."""

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in settings or .env file.")
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def embed(self, texts: list[str], task_type: TaskType) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), _BATCH_SIZE):
            batch = texts[start:start + _BATCH_SIZE]
            response = await self._client.aio.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=settings.EMBEDDING_DIM,
                ),
            )
            vectors.extend(list(e.values) for e in response.embeddings)
        return vectors
