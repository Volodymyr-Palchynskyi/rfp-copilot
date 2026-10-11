_Generated 2026-10-11 14:48 UTC_

# Retrieval eval (fresh2 set)

Held-out: the threshold in use (0.70) was chosen on the main set and is **not** re-tuned here. The sweep below is informational.

At the configured threshold 0.70: recall 56%, precision 100%, abstention 80%.

14 briefs (9 with a relevant project, 5 out of domain).

## Ranking quality (projects ranked by best chunk score)

| hit@1 | hit@3 | MRR |
|---|---|---|
| 89% | 100% | 0.94 |

## Top similarity score by category

| category | mean top score |
|---|---|
| close_analog | 0.747 |
| partial_overlap | 0.696 |
| no_analog | 0.675 |

## Threshold sweep (top 3 projects kept)

- recall: relevant project survived the threshold (cases with analogs)
- precision: share of kept projects that are relevant
- abstention: no project kept for out-of-domain briefs (the desired behaviour)

| threshold | recall | precision | abstention |
|---|---|---|---|
| 0.50 | 100% | 33% | 0% |
| 0.55 | 100% | 33% | 0% |
| 0.60 | 100% | 33% | 0% |
| 0.65 | 100% | 50% | 20% |
| 0.70 | 56% | 100% | 80% |
| 0.75 | 22% | 100% | 100% |

## Reference selection: similarity threshold vs LLM reranker

Threshold = cosine >= 0.70. Rerank = candidates >= 0.60, kept if the judge scores them >= 2 of 3.

| mode | recall | precision | abstention | mean time |
|---|---|---|---|---|
| threshold | 56% | 100% | 80% | 0.5s |
| rerank | 100% | 75% | 60% | 6.3s |
| combined | 100% | 75% | 100% | 7.3s |

Mistakes of `rerank` (id, category, kept): g02 partial_overlap ['002-fintech-kyc-onboarding', '003-ecommerce-b2b-marketplace']; g03 partial_overlap ['006-saas-analytics-dashboard', '001-logistics-fleet-portal']; g04 partial_overlap ['008-mobile-field-service', '005-hr-internal-ai-assistant']; q01 no_analog ['008-mobile-field-service']; q03 no_analog ['008-mobile-field-service']

Mistakes of `combined` (id, category, kept): g02 partial_overlap ['002-fintech-kyc-onboarding', '003-ecommerce-b2b-marketplace']; g03 partial_overlap ['006-saas-analytics-dashboard', '001-logistics-fleet-portal']; g04 partial_overlap ['008-mobile-field-service', '005-hr-internal-ai-assistant']
