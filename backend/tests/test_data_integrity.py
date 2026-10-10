"""
Offline integrity checks for the knowledge base and the eval sets.

They exist because the data is hand-written and silently wrong data is the worst kind of bug
here: project 001 once claimed 3,400 hours in its metadata while its scope added up to 3,000,
and the model saw both numbers.
"""
import re
from pathlib import Path

import pytest

from app.rag.chunking import load_corpus
from evals.common import CASE_FILES, load_cases

CORPUS_DIR = Path(__file__).parent.parent / "data" / "past_projects"
REQUIRED_SECTIONS = {"Overview", "Scope and Estimates", "Tech Decisions", "Risks and Lessons"}
VALID_CATEGORIES = {"close_analog", "partial_overlap", "out_of_domain", "no_analog"}
NO_REFERENCE_CATEGORIES = {"out_of_domain", "no_analog"}


def documents() -> list[Path]:
    return sorted(CORPUS_DIR.glob("*.md"))


def meta_of(path: Path) -> dict[str, str]:
    block = re.match(r"---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.DOTALL).group(1)
    return dict(line.split(": ", 1) for line in block.splitlines())


@pytest.mark.parametrize("path", documents(), ids=lambda p: p.stem)
def test_scope_hours_add_up_to_total_hours(path):
    text = path.read_text(encoding="utf-8")
    scope = text.split("## Scope and Estimates")[1].split("\n## ")[0]
    summed = sum(int(h.replace(",", "")) for h in re.findall(r":\s*([\d,]+)\s*h\b", scope))

    assert summed == int(meta_of(path)["total_hours"])


@pytest.mark.parametrize("path", documents(), ids=lambda p: p.stem)
def test_document_has_required_metadata_and_sections(path):
    meta = meta_of(path)
    assert meta["id"] == path.stem
    for key in ("title", "industry", "stack", "team_size", "duration_weeks", "total_hours"):
        assert meta.get(key), f"{path.name}: missing {key}"

    sections = {c.payload["section"] for c in load_corpus(CORPUS_DIR) if c.payload["project_id"] == meta["id"]}
    assert sections == REQUIRED_SECTIONS


def test_chunk_ids_are_unique():
    ids = [c.id for c in load_corpus(CORPUS_DIR)]
    assert len(ids) == len(set(ids))


CORPUS_IDS = {p.stem for p in documents()}


@pytest.mark.parametrize("case_set", CASE_FILES)
def test_eval_cases_are_well_formed(case_set):
    cases = load_cases(case_set)
    assert cases, f"{case_set} is empty"
    assert len({c.id for c in cases}) == len(cases), "duplicate case ids"

    for c in cases:
        assert c.category in VALID_CATEGORIES, c.id
        low, high = c.hours_range
        assert 0 < low < high, f"{c.id}: bad hour range"
        assert high / low <= 3, f"{c.id}: range is so wide it can hardly fail"
        assert len(c.brief) >= 100, f"{c.id}: brief too short"
        assert set(c.expected_projects) <= CORPUS_IDS, f"{c.id}: unknown project id"
        if c.category in NO_REFERENCE_CATEGORIES:
            assert not c.expected_projects, f"{c.id}: no-analog case must not expect projects"
        else:
            assert c.expected_projects, f"{c.id}: analog case needs an expected project"


def test_case_ids_and_briefs_are_unique_across_sets():
    all_cases = [c for case_set in CASE_FILES for c in load_cases(case_set)]
    assert len({c.id for c in all_cases}) == len(all_cases), "case id reused in another set"
    assert len({c.brief for c in all_cases}) == len(all_cases), "same brief appears in two sets"
