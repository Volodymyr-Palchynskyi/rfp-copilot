_Generated 2026-10-11 14:57 UTC_

# Generation eval (fresh2 set)

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 14 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 14 | 50% | 23% | 100% | 0% | 28s |
| close_analog | rag | 4 | 100% | 7% | 100% | 0% | 29s |
| partial_overlap | rag | 5 | 60% | 16% | 100% | 0% | 26s |
| no_analog | rag | 5 | 0% | 48% | n/a | 0% | 28s |

## Per brief (midpoint hours)

| case | category | expected | rag |
|---|---|---|---|
| f01 | close_analog | 2600-4200 | 3600 |
| f02 | close_analog | 2000-3300 | 2830 |
| f03 | close_analog | 2600-4200 | 3615 |
| f04 | close_analog | 2400-4000 | 2660 |
| g01 | partial_overlap | 4200-6800 | 5370 |
| g02 | partial_overlap | 3200-5200 | 5440 |
| g03 | partial_overlap | 3200-5200 | 4535 |
| g04 | partial_overlap | 2000-3600 | 3670 |
| g05 | partial_overlap | 3000-5000 | 4625 |
| q01 | no_analog | 1800-3200 | 1155 |
| q02 | no_analog | 1000-2200 | 860 |
| q03 | no_analog | 700-1400 | 692 |
| q04 | no_analog | 1200-2400 | 928 |
| q05 | no_analog | 3000-5500 | 880 |
