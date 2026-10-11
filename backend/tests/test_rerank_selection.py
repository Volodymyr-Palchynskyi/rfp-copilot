from types import SimpleNamespace

import pytest

from app.core.config import settings
from app.rag.rerank import ProjectJudgement
from app.services.knowledge_service import KnowledgeService


def chunk(project_id: str, score: float) -> tuple[float, dict]:
    return score, {
        "project_id": project_id,
        "title": f"Project {project_id}",
        "industry": "x",
        "stack": "y",
        "total_hours": 1000,
        "duration_weeks": 10,
        "section": "Overview",
        "text": f"text of {project_id}",
    }


class FakeReranker:
    def __init__(self, relevance: dict[str, int] | Exception) -> None:
        self.relevance = relevance
        self.calls = 0

    async def judge(self, brief, candidates):
        self.calls += 1
        if isinstance(self.relevance, Exception):
            raise self.relevance
        return {
            c.project_id: ProjectJudgement(project_id=c.project_id, reason=f"why {c.project_id}", relevance=self.relevance[c.project_id])
            for c in candidates
            if c.project_id in self.relevance
        }


def make_service(monkeypatch, raw, reranker) -> KnowledgeService:
    monkeypatch.setattr(settings, "RERANK_ENABLED", True)
    monkeypatch.setattr(settings, "RAG_MIN_SCORE", 0.70)
    monkeypatch.setattr(settings, "RAG_CANDIDATE_MIN_SCORE", 0.60)
    service = KnowledgeService.__new__(KnowledgeService)  # skip real Embedder / Qdrant
    service._reranker = reranker

    async def fake_search(query, limit):
        return raw

    service._search_raw = fake_search
    return service


RAW = [chunk("a", 0.75), chunk("b", 0.68), chunk("c", 0.62), chunk("d", 0.50)]


async def test_rerank_keeps_judged_relevant_and_orders_by_relevance(monkeypatch):
    reranker = FakeReranker({"a": 2, "b": 3, "c": 1})
    refs = await make_service(monkeypatch, RAW, reranker).find_references("brief")

    assert [r.project_id for r in refs] == ["b", "a"]  # c scored 1 and is dropped; b outranks a
    assert refs[0].reason == "why b"


async def test_candidates_below_floor_never_reach_the_judge(monkeypatch):
    seen = []

    class Spy(FakeReranker):
        async def judge(self, brief, candidates):
            seen.extend(c.project_id for c in candidates)
            return await super().judge(brief, candidates)

    await make_service(monkeypatch, RAW, Spy({"a": 3, "b": 3, "c": 3})).find_references("brief")
    assert seen == ["a", "b", "c"]  # d (0.50) is below the 0.60 floor


async def test_no_candidates_means_no_llm_call(monkeypatch):
    reranker = FakeReranker({})
    refs = await make_service(monkeypatch, [chunk("d", 0.40)], reranker).find_references("brief")

    assert refs == [] and reranker.calls == 0


async def test_judge_failure_falls_back_to_similarity_threshold(monkeypatch):
    reranker = FakeReranker(RuntimeError("quota"))
    refs = await make_service(monkeypatch, RAW, reranker).find_references("brief")

    assert [r.project_id for r in refs] == ["a"]  # only a is >= 0.70
    assert refs[0].reason is None


async def test_rerank_can_be_bypassed_per_call(monkeypatch):
    reranker = FakeReranker({"a": 0})
    refs = await make_service(monkeypatch, RAW, reranker).find_references("brief", rerank=False)

    assert [r.project_id for r in refs] == ["a"] and reranker.calls == 0


async def test_combined_rule_requires_similarity_as_well_as_judge_agreement(monkeypatch):
    # The judge likes everything; the combined floor (0.65) drops b (0.68 passes) but c (0.62) must go.
    reranker = FakeReranker({"a": 3, "b": 3, "c": 3})
    service = make_service(monkeypatch, RAW, reranker)

    refs = await service.find_references("brief", min_similarity=0.65)

    assert [r.project_id for r in refs] == ["a", "b"]


async def test_combined_rule_floor_comes_from_settings_by_default(monkeypatch):
    reranker = FakeReranker({"a": 3, "b": 3, "c": 3})
    service = make_service(monkeypatch, RAW, reranker)
    monkeypatch.setattr(settings, "RERANK_REQUIRE_SIMILARITY", 0.70)

    refs = await service.find_references("brief")

    assert [r.project_id for r in refs] == ["a"]


async def test_explicit_zero_floor_overrides_the_setting(monkeypatch):
    reranker = FakeReranker({"a": 3, "c": 3})
    service = make_service(monkeypatch, RAW, reranker)
    monkeypatch.setattr(settings, "RERANK_REQUIRE_SIMILARITY", 0.70)

    refs = await service.find_references("brief", min_similarity=0.0)

    assert {r.project_id for r in refs} == {"a", "c"}
