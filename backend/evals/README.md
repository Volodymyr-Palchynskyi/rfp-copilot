# Evals

Two suites, both driven by the 20 briefs in `cases.json`:

| category | briefs | what it tests |
|---|---|---|
| `close_analog` | 10 | a past project closely matches the brief |
| `partial_overlap` | 6 | only parts of one or two past projects apply |
| `out_of_domain` | 4 | nothing in the knowledge base applies, the system should abstain |

```bash
uv run python -m evals retrieval    # embeddings only, cheap, run on every retrieval change
uv run python -m evals generation   # 2 x 20 Gemini calls (RAG vs no RAG), takes a few minutes
```

Reports are written to `results/` (`.md` for humans, `.json` with per-brief rows). Stop the API server first:
the embedded Qdrant store can be opened by one process at a time.

## Caveats

- Expected hour ranges are my own judgement of what an experienced team would quote, anchored on the
  synthetic past projects. They are a yardstick, not ground truth.
- `close_analog` briefs are written to resemble corpus projects, so they measure how well the system
  uses a good analogy, not how often a good analogy exists in practice.
- One run per brief at temperature 0.2. Treat differences of a few percentage points as noise.
