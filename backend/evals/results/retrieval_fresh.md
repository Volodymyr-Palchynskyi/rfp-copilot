_Generated 2026-10-10 09:37 UTC_

# Retrieval eval (fresh set)

Held-out: the threshold in use (0.70) was chosen on the main set and is **not** re-tuned here. The sweep below is informational.

At the configured threshold 0.70: recall 100%, precision 100%, abstention 100%.

13 briefs (9 with a relevant project, 4 out of domain).

## Ranking quality (projects ranked by best chunk score)

| hit@1 | hit@3 | MRR |
|---|---|---|
| 100% | 100% | 1.00 |

## Top similarity score by category

| category | mean top score |
|---|---|
| close_analog | 0.733 |
| partial_overlap | 0.718 |
| no_analog | 0.661 |

## Threshold sweep (top 3 projects kept)

- recall: relevant project survived the threshold (cases with analogs)
- precision: share of kept projects that are relevant
- abstention: no project kept for out-of-domain briefs (the desired behaviour)

| threshold | recall | precision | abstention |
|---|---|---|---|
| 0.50 | 100% | 33% | 0% |
| 0.55 | 100% | 33% | 0% |
| 0.60 | 100% | 36% | 0% |
| 0.65 | 100% | 60% | 50% |
| 0.70 | 100% | 100% | 100% |
| 0.75 | 0% | 0% | 100% |

## Reference selection: similarity threshold vs LLM reranker

Threshold = cosine >= 0.70. Rerank = candidates >= 0.60, kept if the judge scores them >= 2 of 3.

| mode | recall | precision | abstention | mean time |
|---|---|---|---|---|
| threshold | 100% | 100% | 100% | 0.4s |
| rerank | 100% | 90% | 50% | 4.5s |

Reranker mistakes (id, category, kept): n06 partial_overlap ['004-healthcare-patient-app', '008-mobile-field-service']; n11 no_analog ['004-healthcare-patient-app']; n12 no_analog ['007-edtech-lms', '006-saas-analytics-dashboard']
