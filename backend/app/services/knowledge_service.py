import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import settings
from app.rag.chunking import load_corpus
from app.rag.embeddings import Embedder
from app.rag.store import VectorStore
from app.schemas.knowledge import ChunkHit, IngestResult

logger = logging.getLogger(__name__)

MAX_REFERENCE_PROJECTS = 3


@dataclass
class ReferenceContext:
    """A past project plus the chunks that matched the query (used to ground the prompt)."""

    project_id: str
    title: str
    industry: str
    stack: str
    total_hours: int
    duration_weeks: int
    score: float
    chunks: list[tuple[str, str]] = field(default_factory=list)  # (section, text)


class KnowledgeService:
    def __init__(self) -> None:
        self._embedder = Embedder()
        self._store = VectorStore()

    async def ingest(self) -> IngestResult:
        chunks = load_corpus(Path(settings.KNOWLEDGE_DIR))
        if not chunks:
            raise ValueError(f"No markdown documents found in {settings.KNOWLEDGE_DIR}")
        vectors = await self._embedder.embed([c.text for c in chunks], "RETRIEVAL_DOCUMENT")
        await self._store.rebuild(chunks, vectors)
        projects = {c.payload["project_id"] for c in chunks}
        logger.info("Ingested %d chunks from %d projects", len(chunks), len(projects))
        return IngestResult(projects=len(projects), chunks=len(chunks))

    async def ensure_indexed(self) -> None:
        if await self._store.count() == 0:
            await self.ingest()

    async def search(self, query: str, limit: int | None = None) -> list[ChunkHit]:
        raw = await self._search_raw(query, limit or settings.RAG_TOP_K)
        return [
            ChunkHit(
                score=round(score, 4),
                project_id=p["project_id"],
                title=p["title"],
                section=p["section"],
                text=p["text"],
            )
            for score, p in raw
        ]

    async def find_references(self, query: str) -> list[ReferenceContext]:
        """Retrieve chunks, drop weak matches, then group by project and keep the best few."""
        raw = await self._search_raw(query, settings.RAG_TOP_K)
        projects: dict[str, ReferenceContext] = {}
        for score, p in raw:
            if score < settings.RAG_MIN_SCORE:
                continue
            ref = projects.setdefault(
                p["project_id"],
                ReferenceContext(
                    project_id=p["project_id"],
                    title=p["title"],
                    industry=p["industry"],
                    stack=p["stack"],
                    total_hours=p["total_hours"],
                    duration_weeks=p["duration_weeks"],
                    score=score,
                ),
            )
            ref.score = max(ref.score, score)
            ref.chunks.append((p["section"], p["text"]))
        ranked = sorted(projects.values(), key=lambda r: r.score, reverse=True)
        return ranked[:MAX_REFERENCE_PROJECTS]

    async def rank_projects(self, query: str) -> list[tuple[str, float]]:
        """All projects ranked by their best chunk score, with no threshold. Used by evals."""
        raw = await self._search_raw(query, limit=1000)
        best: dict[str, float] = {}
        for score, p in raw:
            best[p["project_id"]] = max(score, best.get(p["project_id"], 0.0))
        return sorted(best.items(), key=lambda item: item[1], reverse=True)

    async def _search_raw(self, query: str, limit: int) -> list[tuple[float, dict]]:
        [vector] = await self._embedder.embed([query], "RETRIEVAL_QUERY")
        return await self._store.search(vector, limit)
