# Evals

Two suites, run on two case sets: the 20 tuned briefs in `cases.json` and 15 held-out briefs in `cases_heldout.json` (`--set heldout`), plus a third set `cases_fresh.json` (`--set fresh`) written after the reranker existed:

| category | briefs | what it tests |
|---|---|---|
| `close_analog` | 10 | a past project closely matches the brief |
| `partial_overlap` | 6 | only parts of one or two past projects apply |
| `out_of_domain` | 4 | nothing in the knowledge base applies, the system should abstain |

```bash
uv run python -m evals retrieval    # embeddings only, cheap, run on every retrieval change
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

| step | tuned set in range | held-out in range | fresh in range |
|---|---|---|---|
| no RAG (calibrated prompt) | 15% | 13% | 15% |
| similarity threshold 0.70 | 75% | 60% | not run yet |
| + LLM reranker | 95% | 80% | 38% |

The threshold-only run on the fresh set was interrupted by the daily API quota (250 requests per model), so that
cell is empty rather than filled with a partial result. Re-run with `--set fresh --no-rerank`.

Why the reranker numbers fall: the tuned set was used to design everything, the held-out set's failures motivated
the reranker, and the fresh set (13 briefs with stricter labels) is the first clean test. On it, retrieval-level
metrics look like this: threshold 100% recall / 100% precision / 100% abstention, reranker 100% / 90% / 50%. For the
four "nothing reusable" briefs the reranker kept weak analogies (a healthcare app for a leave-request tool, an LMS and
an analytics product for a podcast platform) and RAG ended at 0% in range, worse than no RAG (50%).
Fresh-set categories are defined more strictly: `close_analog` (most of the scope maps to one past project),
`partial_overlap` (one or two substantial modules map, the rest is new), `no_analog` (only generic features or the
same industry in common).

Archived threshold-only reports for the earlier sets: `results/generation_v2_threshold.*`,
`results/generation_heldout_threshold.*`.

## Reserved set: `fresh2`

`cases_fresh2.json` (14 briefs: 4 close, 5 partial, 5 no analog, same strict category definitions as `fresh`) was
written on 2026-10-10 **before any run**, with its expected hour ranges fixed in advance. It is reserved for the
next planned experiment: a combined selection rule (similarity floor AND reranker agreement) against the current
rerank-only and threshold-only rules. Do not run it to explore or to tune; run each candidate configuration on it once
and report all of them. After that it is spent like the other sets.
