# Evals

Two suites, run on two case sets: the 20 tuned briefs in `cases.json` and 15 held-out briefs in `cases_heldout.json` (`--set heldout`):

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

| step | tuned set in range | held-out in range | held-out partial overlap |
|---|---|---|---|
| similarity threshold 0.70 | 75% | 60% | 40% |
| + LLM reranker | 95% | 80% | 100% |
| no RAG (calibrated prompt) | 15% | 13% | 0% |

Archived threshold-only reports: `results/generation_v2_threshold.*`, `results/generation_heldout_threshold.*`.
The reranker was designed after seeing the held-out retrieval failures (two partial-overlap briefs missed by the
threshold), so the held-out set is no longer a clean test of it. Retrieval-level view (`retrieval --set heldout`):
recall 82% to 100%, precision 100% to 93%, abstention 100% to 0%. The reranker deliberately accepts a past project
when one substantial module is reusable, which my "out of domain" labels did not anticipate.
The next honest measurement needs fresh briefs.
