_Generated 2026-10-10 09:19 UTC_

# Retrieval eval

At the configured threshold 0.70: recall 100%, precision 100%, abstention 100%.

20 briefs (16 with a relevant project, 4 out of domain).

## Ranking quality (projects ranked by best chunk score)

| hit@1 | hit@3 | MRR |
|---|---|---|
| 100% | 100% | 1.00 |

## Top similarity score by category

| category | mean top score |
|---|---|
| close_analog | 0.774 |
| partial_overlap | 0.730 |
| out_of_domain | 0.643 |

## Threshold sweep (top 3 projects kept)

- recall: relevant project survived the threshold (cases with analogs)
- precision: share of kept projects that are relevant
- abstention: no project kept for out-of-domain briefs (the desired behaviour)

| threshold | recall | precision | abstention |
|---|---|---|---|
| 0.50 | 100% | 40% | 0% |
| 0.55 | 100% | 40% | 0% |
| 0.60 | 100% | 40% | 0% |
| 0.65 | 100% | 54% | 75% |
| 0.70 | 100% | 100% | 100% |
| 0.75 | 56% | 100% | 100% |

## Reference selection: similarity threshold vs LLM reranker

Threshold = cosine >= 0.70. Rerank = candidates >= 0.60, kept if the judge scores them >= 2 of 3.

| mode | recall | precision | abstention | mean time |
|---|---|---|---|---|
| threshold | 100% | 100% | 100% | 0.3s |
| rerank | 100% | 100% | 25% | 3.6s |

Reranker mistakes (id, category, kept): c18 out_of_domain ['004-healthcare-patient-app']; c19 out_of_domain ['006-saas-analytics-dashboard']; c20 out_of_domain ['003-ecommerce-b2b-marketplace']
