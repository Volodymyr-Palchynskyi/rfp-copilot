"""
Retrieval eval: does the vector search surface the right past projects, and which
relevance threshold separates real analogies from noise?

Only embedding calls are needed (no generation), so it is cheap enough to run on every change.
"""
import asyncio
import time
from statistics import mean

from app.services.knowledge_service import MAX_REFERENCE_PROJECTS, KnowledgeService
from app.core.config import settings
from evals.common import CATEGORIES, COMBINED_MIN_SIMILARITY, Case, load_cases, md_table, pct, result_name, save_report

THRESHOLDS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]


def _rank_metrics(cases: list[Case], rankings: dict[str, list[tuple[str, float]]]) -> dict:
    """Threshold-independent ranking quality, for cases that have a relevant project."""
    positives = [c for c in cases if c.expected_projects]
    hit1 = hit3 = 0
    reciprocal_ranks = []
    for c in positives:
        ids = [pid for pid, _ in rankings[c.id]]
        rank = next((i + 1 for i, pid in enumerate(ids) if pid in c.expected_projects), None)
        hit1 += rank == 1
        hit3 += rank is not None and rank <= 3
        reciprocal_ranks.append(1 / rank if rank else 0.0)
    n = len(positives)
    return {"cases": n, "hit@1": hit1 / n, "hit@3": hit3 / n, "mrr": mean(reciprocal_ranks)}


def _threshold_metrics(cases: list[Case], rankings: dict[str, list[tuple[str, float]]], threshold: float) -> dict:
    """What the pipeline actually does at a given threshold: keep top-N projects above it."""
    positives = [c for c in cases if c.expected_projects]
    negatives = [c for c in cases if not c.expected_projects]

    recalled = 0
    relevant_kept = total_kept = 0
    for c in positives:
        kept = [pid for pid, s in rankings[c.id] if s >= threshold][:MAX_REFERENCE_PROJECTS]
        recalled += any(pid in c.expected_projects for pid in kept)
        relevant_kept += sum(pid in c.expected_projects for pid in kept)
        total_kept += len(kept)

    abstained = sum(
        not [1 for _, s in rankings[c.id] if s >= threshold] for c in negatives
    )
    return {
        "threshold": threshold,
        "recall": recalled / len(positives),
        "precision": relevant_kept / total_kept if total_kept else 0.0,
        "abstention": abstained / len(negatives),
    }


async def _selection_metrics(
    service: KnowledgeService, cases: list[Case], rerank: bool, min_similarity: float = 0.0
) -> dict:
    """End-to-end reference selection as the pipeline does it, with or without the LLM reranker."""
    semaphore = asyncio.Semaphore(4)

    async def one(case: Case) -> tuple[Case, list[str], float]:
        async with semaphore:
            start = time.perf_counter()
            refs = await service.find_references(case.brief, rerank=rerank, min_similarity=min_similarity)
            return case, [r.project_id for r in refs], time.perf_counter() - start

    results = await asyncio.gather(*(one(c) for c in cases))
    positives = [(c, kept) for c, kept, _ in results if c.expected_projects]
    negatives = [(c, kept) for c, kept, _ in results if not c.expected_projects]
    relevant_kept = sum(pid in c.expected_projects for c, kept in positives for pid in kept)
    total_kept = sum(len(kept) for _, kept in positives)
    return {
        "recall": sum(any(pid in c.expected_projects for pid in kept) for c, kept in positives) / len(positives),
        "precision": relevant_kept / total_kept if total_kept else 0.0,
        "abstention": sum(not kept for _, kept in negatives) / len(negatives),
        "mean_latency_s": mean(t for _, _, t in results),
        "kept": {c.id: kept for c, kept, _ in results},
    }


async def run(case_set: str = "main", variant: str = "") -> None:
    service = KnowledgeService()
    await service.ensure_indexed()
    cases = load_cases(case_set)

    rankings = {c.id: await service.rank_projects(c.brief) for c in cases}

    rank = _rank_metrics(cases, rankings)
    selection = {
        "threshold": await _selection_metrics(service, cases, rerank=False),
        "rerank": await _selection_metrics(service, cases, rerank=True),
        "combined": await _selection_metrics(service, cases, rerank=True, min_similarity=COMBINED_MIN_SIMILARITY),
    }
    sweep = [_threshold_metrics(cases, rankings, t) for t in THRESHOLDS]

    top_by_category = {
        cat: mean(rankings[c.id][0][1] for c in cases if c.category == cat) for cat in CATEGORIES if any(c.category == cat for c in cases)
    }
    misses = [
        (c.id, c.expected_projects, [(pid, round(s, 3)) for pid, s in rankings[c.id][:3]])
        for c in cases
        if c.expected_projects and not any(pid in c.expected_projects for pid, _ in rankings[c.id][:3])
    ]

    md = "# Retrieval eval" + ("" if case_set == "main" else f" ({case_set} set)") + "\n\n"
    if case_set != "main":
        md += (
            f"Held-out: the threshold in use ({settings.RAG_MIN_SCORE:.2f}) was chosen on the main set and "
            "is **not** re-tuned here. The sweep below is informational.\n\n"
        )
    in_use = _threshold_metrics(cases, rankings, settings.RAG_MIN_SCORE)
    md += (
        f"At the configured threshold {settings.RAG_MIN_SCORE:.2f}: recall {pct(in_use['recall'])}, "
        f"precision {pct(in_use['precision'])}, abstention {pct(in_use['abstention'])}.\n\n"
    )
    md += f"{len(cases)} briefs ({rank['cases']} with a relevant project, {len(cases) - rank['cases']} out of domain).\n\n"
    md += "## Ranking quality (projects ranked by best chunk score)\n\n"
    md += md_table(
        ["hit@1", "hit@3", "MRR"],
        [[pct(rank["hit@1"]), pct(rank["hit@3"]), f"{rank['mrr']:.2f}"]],
    )
    md += "\n\n## Top similarity score by category\n\n"
    md += md_table(["category", "mean top score"], [[c, f"{s:.3f}"] for c, s in top_by_category.items()])
    md += f"\n\n## Threshold sweep (top {MAX_REFERENCE_PROJECTS} projects kept)\n\n"
    md += "- recall: relevant project survived the threshold (cases with analogs)\n"
    md += "- precision: share of kept projects that are relevant\n"
    md += "- abstention: no project kept for out-of-domain briefs (the desired behaviour)\n\n"
    md += md_table(
        ["threshold", "recall", "precision", "abstention"],
        [[f"{m['threshold']:.2f}", pct(m["recall"]), pct(m["precision"]), pct(m["abstention"])] for m in sweep],
    )
    md += "\n\n## Reference selection: similarity threshold vs LLM reranker\n\n"
    md += (
        f"Threshold = cosine >= {settings.RAG_MIN_SCORE:.2f}. Rerank = candidates >= {settings.RAG_CANDIDATE_MIN_SCORE:.2f}, "
        f"kept if the judge scores them >= {settings.RERANK_MIN_RELEVANCE} of 3.\n\n"
    )
    md += md_table(
        ["mode", "recall", "precision", "abstention", "mean time"],
        [
            [name, pct(m["recall"]), pct(m["precision"]), pct(m["abstention"]), f"{m['mean_latency_s']:.1f}s"]
            for name, m in selection.items()
        ],
    )
    for mode in ("rerank", "combined"):
        wrong = [
            (c.id, c.category, kept)
            for c in cases
            for kept in [selection[mode]["kept"][c.id]]
            if (c.expected_projects and not any(pid in c.expected_projects for pid in kept))
            or (not c.expected_projects and kept)
            or (c.expected_projects and any(pid not in c.expected_projects for pid in kept))
        ]
        if wrong:
            md += f"\n\nMistakes of `{mode}` (id, category, kept): " + "; ".join(f"{i} {cat} {k}" for i, cat, k in wrong)
    if misses:
        md += "\n\n## Misses (no relevant project in top 3)\n\n"
        md += md_table(["case", "expected", "got"], [[i, ", ".join(e), g] for i, e, g in misses])

    print(md)
    save_report(result_name("retrieval", case_set), md, {"rank": rank, "sweep": sweep, "selection": selection, "top_by_category": top_by_category})
