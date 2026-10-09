from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.rag.chunking import Chunk


class VectorStore:
    """Qdrant wrapper. Embedded local mode by default, a real server when QDRANT_URL is set."""

    def __init__(self) -> None:
        if settings.QDRANT_URL:
            self._client = AsyncQdrantClient(url=settings.QDRANT_URL)
        else:
            self._client = AsyncQdrantClient(path=settings.QDRANT_PATH)
        self._collection = settings.QDRANT_COLLECTION

    async def count(self) -> int:
        if not await self._client.collection_exists(self._collection):
            return 0
        return (await self._client.count(self._collection)).count

    async def rebuild(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """The corpus is small, so ingestion simply rebuilds the collection (idempotent)."""
        if await self._client.collection_exists(self._collection):
            await self._client.delete_collection(self._collection)
        await self._client.create_collection(
            collection_name=self._collection,
            vectors_config=VectorParams(size=settings.EMBEDDING_DIM, distance=Distance.COSINE),
        )
        await self._client.upsert(
            collection_name=self._collection,
            points=[
                PointStruct(id=c.id, vector=v, payload={**c.payload, "text": c.text})
                for c, v in zip(chunks, vectors, strict=True)
            ],
        )

    async def search(self, vector: list[float], limit: int) -> list[tuple[float, dict]]:
        response = await self._client.query_points(
            collection_name=self._collection,
            query=vector,
            limit=limit,
            with_payload=True,
        )
        return [(p.score, p.payload or {}) for p in response.points]
