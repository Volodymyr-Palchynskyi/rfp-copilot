_Generated 2026-10-09 19:14 UTC_

# Retrieval eval

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
