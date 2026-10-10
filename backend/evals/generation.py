"""
Generation eval: does grounding in past projects make estimates better?

Every brief is run twice, with RAG and without (same model, same prompt, no references),
and compared against the expected hour ranges in cases.json.
Calls the Gemini API (2 x number of briefs), so it costs money and takes a few minutes.
"""
import asyncio
import time
from collections import defaultdict
from statistics import mean, median

from app.core.config import settings
from app.rag.chunking import load_corpus
from app.schemas.proposal import ProposalRequest, ProposalResponse
from app.services.knowledge_service import KnowledgeService
from app.services.proposal_service import ProposalService
from pathlib import Path
from evals.common import CATEGORIES, Case, load_cases, md_table, pct, result_name, save_report

CONCURRENCY = 3
RETRIES = 2


def _corpus_names() -> dict[str, str]:
    """project_id -> title, used to detect references to projects that were never provided."""
    return {c.payload["project_id"]: c.payload["title"] for c in load_corpus(Path(settings.KNOWLEDGE_DIR))}


def _mentioned(text: str, names: dict[str, str]) -> set[str]:
    lowered = text.lower()
    return {pid for pid, title in names.items() if pid.lower() in lowered or title.lower() in lowered}


async def _generate(service: ProposalService, case: Case) -> tuple[ProposalResponse | None, float, str | None]:
    request = ProposalRequest(client_name="Eval Client", project_description=case.brief)
    error = None
    for attempt in range(RETRIES + 1):
        start = time.perf_counter()
        try:
            return await service.generate_proposal(request), time.perf_counter() - start, None
        except Exception as exc:  # noqa: BLE001 - eval harness records any failure
            error = f"{type(exc).__name__}: {exc}"
            if "PerDay" in str(exc):  # daily quota is gone, retrying only burns time
                break
            await asyncio.sleep(2 * (attempt + 1))
    return None, 0.0, error


def _score(case: Case, response: ProposalResponse, names: dict[str, str]) -> dict:
    lo, hi = case.hours_range
    mid = (response.total_hours_min + response.total_hours_max) / 2
    provided = {r.project_id for r in response.references}
    mentioned = _mentioned(response.estimation_basis, names)
    return {
        "hours_mid": mid,
        "in_range": lo <= mid <= hi,
        "ape": abs(mid - case.expected_mid) / case.expected_mid,
        "refs": len(provided),
        "cites_reference": bool(provided & mentioned) if provided else None,
        "fabricated_reference": bool(mentioned - provided),
        "features": len(response.features),
    }


async def run(case_set: str = "main", variant: str = "") -> None:
    cases = load_cases(case_set)
    names = _corpus_names()

    knowledge = KnowledgeService()
    await knowledge.ensure_indexed()
    services = {"rag": ProposalService(knowledge=knowledge), "baseline": ProposalService(knowledge=None)}

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async def job(mode: str, case: Case) -> dict:
        async with semaphore:
            response, latency, error = await _generate(services[mode], case)
        row = {"case": case.id, "category": case.category, "mode": mode, "latency_s": round(latency, 1)}
        if response is None:
            return {**row, "error": error}
        return {**row, **_score(case, response, names), "estimation_basis": response.estimation_basis}

    by_id = {c.id: c for c in cases}
    rows = await asyncio.gather(*(job(m, c) for c in cases for m in services))
    ok = [r for r in rows if "error" not in r]
    failed = [r for r in rows if "error" in r]

    def summarise(subset: list[dict]) -> dict:
        if not subset:
            return {}
        cites = [r["cites_reference"] for r in subset if r["cites_reference"] is not None]
        return {
            "n": len(subset),
            "in_range": mean(r["in_range"] for r in subset),
            "median_ape": median(r["ape"] for r in subset),
            "mean_ape": mean(r["ape"] for r in subset),
            "cites_reference": mean(cites) if cites else None,
            "fabricated": mean(r["fabricated_reference"] for r in subset),
            "latency_s": mean(r["latency_s"] for r in subset),
        }

    def row_for(label: str, mode: str, category: str | None) -> list:
        s = summarise([r for r in ok if r["mode"] == mode and (category is None or r["category"] == category)])
        if not s:
            return [label, mode, "-", "-", "-", "-", "-", "-"]
        cites = "n/a" if s["cites_reference"] is None else pct(s["cites_reference"])
        return [label, mode, s["n"], pct(s["in_range"]), pct(s["median_ape"]), cites, pct(s["fabricated"]), f"{s['latency_s']:.0f}s"]

    headers = ["category", "mode", "n", "in range", "median error", "cites refs", "fabricated refs", "latency"]
    table_rows = [row_for("all", m, None) for m in services]
    for cat in (c for c in CATEGORIES if any(case.category == c for case in cases)):
        table_rows += [row_for(cat, m, cat) for m in services]

    title = "Generation eval" + ("" if case_set == "main" else f" ({case_set} set)")
    md = f"# {title}\n\nModel: `{settings.GEMINI_MODEL}`, temperature 0.2, single run per brief, {len(cases)} briefs.\n\n"
    md += "- in range: midpoint of total hours falls inside the expected range\n"
    md += "- median error: |midpoint - expected midpoint| / expected midpoint\n"
    md += "- cites refs: estimation_basis names at least one provided reference project\n"
    md += "- fabricated refs: estimation_basis names a past project that was not provided\n\n"
    md += md_table(headers, table_rows)

    per_case = []
    for cid in by_id:
        cells = [cid, by_id[cid].category, f"{by_id[cid].hours_range[0]}-{by_id[cid].hours_range[1]}"]
        for mode in services:
            r = next((x for x in ok if x["case"] == cid and x["mode"] == mode), None)
            cells.append(f"{r['hours_mid']:.0f}" if r else "error")
        per_case.append(cells)
    md += "\n\n## Per brief (midpoint hours)\n\n"
    md += md_table(["case", "category", "expected", *services], per_case)

    if failed:
        md += f"\n\n## Failures ({len(failed)})\n\n" + "\n".join(f"- {r['case']} / {r['mode']}: {r['error']}" for r in failed)

    print(md)
    save_report(result_name("generation", case_set, variant), md, {"model": settings.GEMINI_MODEL, "rows": rows})
