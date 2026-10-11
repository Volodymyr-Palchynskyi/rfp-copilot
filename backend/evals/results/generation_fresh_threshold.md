_Generated 2026-10-11 14:59 UTC_

# Generation eval (fresh set)

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 13 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 13 | 38% | 35% | 89% | 0% | 19s |
| close_analog | rag | 5 | 80% | 13% | 100% | 0% | 23s |
| partial_overlap | rag | 4 | 25% | 35% | 75% | 0% | 20s |
| no_analog | rag | 4 | 0% | 44% | n/a | 0% | 15s |

## Per brief (midpoint hours)

| case | category | expected | rag |
|---|---|---|---|
| n01 | close_analog | 2400-4000 | 2150 |
| n02 | close_analog | 3800-6200 | 5505 |
| n03 | close_analog | 3000-5000 | 4615 |
| n04 | close_analog | 1000-1900 | 1635 |
| n05 | close_analog | 3800-5800 | 5230 |
| n06 | partial_overlap | 2200-3800 | 4350 |
| n07 | partial_overlap | 2800-4500 | 3200 |
| n08 | partial_overlap | 3200-5200 | 2720 |
| n09 | partial_overlap | 1800-3200 | 1630 |
| n10 | no_analog | 1200-2400 | 950 |
| n11 | no_analog | 700-1500 | 648 |
| n12 | no_analog | 1500-3000 | 1095 |
| n13 | no_analog | 900-1800 | 800 |
