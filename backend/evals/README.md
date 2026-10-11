# Evals

Two suites, run on two case sets: the 20 tuned briefs in `cases.json` and 15 held-out briefs in `cases_heldout.json` (`--set heldout`), plus a third set `cases_fresh.json` (`--set fresh`) written after the reranker existed:

| category | briefs | what it tests |
|---|---|---|
| `close_analog` | 10 | a past project closely matches the brief |
| `partial_overlap` | 6 | only parts of one or two past projects apply |
| `out_of_domain` | 4 | nothing in the knowledge base applies, the system should abstain |

```bash
uv run python -m evals retrieval    # embeddings plus one reranker (LLM) call per brief
uv run python -m evals generation   # 2 x 20 Gemini calls (RAG vs no RAG), takes a few minutes
uv run python -m evals retrieval --set heldout
uv run python -m evals generation --set heldout   # 2 x 15 calls
uv run python -m evals generation --set fresh     # 2 x 13 calls
uv run python -m evals generation --set fresh --no-rerank   # threshold-only selection, writes *_threshold.*
```

Reports are written to `results/` (`.md` for humans, `.json` with per-brief rows). Stop the API server first:
the embedded Qdrant store can be opened by one process at a time.

## Caveats

- Expected hour ranges are my own judgement of what an experienced team would quote, anchored on the
  synthetic past projects. They are a yardstick, not ground truth.
- `close_analog` briefs are written to resemble corpus projects, so they measure how well the system
  uses a good analogy, not how often a good analogy exists in practice.
- One run per brief at temperature 0.2. Treat differences of a few percentage points as noise.

## Held-out set

`cases_heldout.json` was written after the prompt rules and the 0.70 threshold were tuned on `cases.json`.
Its briefs use more business wording and fewer technical terms, and their expected ranges were fixed before the
first run. Nothing was tuned against it. If you change the prompt or threshold based on its results, it stops
being held-out and should be replaced with fresh briefs.

## Results history

Share of briefs in the expected range, median error (single runs, temperature 0.2):

| set | no RAG | threshold | reranker | reranker + floor 0.65 |
|---|---|---|---|---|
| tuned (20) | 15%, 56% | 75%, 14% | 95%, 8% | not run |
| held-out (15) | 13%, 53% | 60%, 26% | 80%, 20% | not run |
| fresh (13) | 15%, 57% | 38%, 35% | 38%, 34% | not run |
| fresh2 (14) | 7%, 57% | 50%, 33% | 79%, 12% | 50%, 23% |

How the sets were used:

- **tuned**: everything was designed on it. **held-out**: its failures motivated the reranker, so it is no longer clean.
- **fresh**: the first clean test of the reranker. **fresh2**: reserved in advance for the combined-rule experiment.
- The combined rule (judge >= 2 AND cosine >= 0.65, the value fixed before the run) was run on fresh2 only, once, and
  lost to the judge alone (50% against 79%), so it was rejected. It stays in the code behind
  `RERANK_REQUIRE_SIMILARITY` (default 0, off).
- All sets are now spent: every configuration has been run on `fresh` and `fresh2`. A new honest measurement needs
  new briefs.

Fresh-set categories are defined strictly: `close_analog` (most of the scope maps to one past project),
`partial_overlap` (one or two substantial modules map, the rest is new), `no_analog` (only generic features or the same
industry in common).

Run a configuration with `--selection threshold|rerank|combined`, and add `--modes rag` to skip the no-RAG baseline when
it already exists (it does not depend on the selection rule). Reports land in `results/`, with the selection name as a
suffix (`generation_fresh2_combined.md`).

Retrieval-level view on fresh2 (`retrieval --set fresh2`): threshold recall 56% / precision 100% / abstention 80%,
reranker 100% / 75% / 60%, combined 100% / 75% / 100%. Precision counts every kept project that is not the single
expected one, so a reasonable extra analogy (for instance a marketplace for a gig-work shift board) is scored as a miss.
