import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import settings
from app.rag.chunking import load_corpus
from app.rag.embeddings import Embedder
from app.rag.rerank import Candidate, Reranker
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
    reason: str | None = None  # reranker's explanation, when reranking is on


class KnowledgeService:
    def __init__(self) -> None:
        self._embedder = Embedder()
        self._store = VectorStore()
        self._reranker = Reranker() if settings.RERANK_ENABLED else None

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

    async def find_references(
        self, query: str, rerank: bool | None = None, min_similarity: float | None = None
    ) -> list[ReferenceContext]:
        """
        Pick past projects to ground an estimate on.

        With reranking: the vector search proposes candidates above a low similarity floor and an LLM
        judge keeps the ones that are real analogies. Cosine similarity alone cannot separate them
        (see evals/results/retrieval_heldout.md). Without it, or if the judge fails: a plain threshold.
        """
        use_rerank = (settings.RERANK_ENABLED and self._reranker is not None) if rerank is None else rerank
        raw = await self._search_raw(query, settings.RAG_TOP_K * 2)

        if use_rerank and self._reranker is not None:
            candidates = self._group(raw, settings.RAG_CANDIDATE_MIN_SCORE)[: settings.RAG_MAX_CANDIDATES]
            if not candidates:
                return []
            try:
                floor = settings.RERANK_REQUIRE_SIMILARITY if min_similarity is None else min_similarity
                return await self._rerank(query, candidates, floor)
            except Exception:
                logger.exception("Reranking failed, falling back to the similarity threshold")

        return self._group(raw, settings.RAG_MIN_SCORE)[:MAX_REFERENCE_PROJECTS]

    async def _rerank(
        self, query: str, candidates: list[ReferenceContext], min_similarity: float = 0.0
    ) -> list[ReferenceContext]:
        judgements = await self._reranker.judge(
            query,
            [
                Candidate(
                    project_id=c.project_id,
                    title=c.title,
                    industry=c.industry,
                    stack=c.stack,
                    excerpt="\n\n".join(f"[{section}]\n{text}" for section, text in c.chunks),
                )
                for c in candidates
            ],
        )
        kept = []
        for c in candidates:
            judgement = judgements.get(c.project_id)
            if judgement and judgement.relevance >= settings.RERANK_MIN_RELEVANCE and c.score >= min_similarity:
                c.reason = judgement.reason
                kept.append((judgement.relevance, c))
        kept.sort(key=lambda item: (item[0], item[1].score), reverse=True)
        return [c for _, c in kept][:MAX_REFERENCE_PROJECTS]

    @staticmethod
    def _group(raw: list[tuple[float, dict]], min_score: float) -> list[ReferenceContext]:
        """Group chunks by project, drop chunks below min_score, rank projects by their best chunk."""
        projects: dict[str, ReferenceContext] = {}
        for score, p in raw:
            if score < min_score:
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
        return sorted(projects.values(), key=lambda r: r.score, reverse=True)

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
