_Generated 2026-10-10 09:19 UTC_

# Retrieval eval (heldout set)

Held-out: the threshold in use (0.70) was chosen on the main set and is **not** re-tuned here. The sweep below is informational.

At the configured threshold 0.70: recall 82%, precision 100%, abstention 100%.

15 briefs (11 with a relevant project, 4 out of domain).

## Ranking quality (projects ranked by best chunk score)

| hit@1 | hit@3 | MRR |
|---|---|---|
| 100% | 100% | 1.00 |

## Top similarity score by category

| category | mean top score |
|---|---|
| close_analog | 0.739 |
| partial_overlap | 0.715 |
| out_of_domain | 0.666 |

## Threshold sweep (top 3 projects kept)

- recall: relevant project survived the threshold (cases with analogs)
- precision: share of kept projects that are relevant
- abstention: no project kept for out-of-domain briefs (the desired behaviour)

| threshold | recall | precision | abstention |
|---|---|---|---|
| 0.50 | 100% | 39% | 0% |
| 0.55 | 100% | 39% | 0% |
| 0.60 | 100% | 39% | 0% |
| 0.65 | 100% | 68% | 25% |
| 0.70 | 82% | 100% | 100% |
| 0.75 | 18% | 100% | 100% |

## Reference selection: similarity threshold vs LLM reranker

Threshold = cosine >= 0.70. Rerank = candidates >= 0.60, kept if the judge scores them >= 2 of 3.

| mode | recall | precision | abstention | mean time |
|---|---|---|---|---|
| threshold | 82% | 100% | 100% | 0.3s |
| rerank | 100% | 93% | 0% | 3.7s |

Reranker mistakes (id, category, kept): h11 partial_overlap ['006-saas-analytics-dashboard', '003-ecommerce-b2b-marketplace']; h12 out_of_domain ['004-healthcare-patient-app']; h13 out_of_domain ['003-ecommerce-b2b-marketplace', '004-healthcare-patient-app']; h14 out_of_domain ['005-hr-internal-ai-assistant', '003-ecommerce-b2b-marketplace']; h15 out_of_domain ['007-edtech-lms']
