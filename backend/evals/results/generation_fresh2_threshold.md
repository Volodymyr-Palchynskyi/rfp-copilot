_Generated 2026-10-11 14:52 UTC_

# Generation eval (fresh2 set)

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 14 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 14 | 50% | 33% | 83% | 0% | 26s |
| close_analog | rag | 4 | 100% | 6% | 100% | 0% | 23s |
| partial_overlap | rag | 5 | 20% | 61% | 100% | 0% | 28s |
| no_analog | rag | 5 | 40% | 34% | 0% | 0% | 26s |

## Per brief (midpoint hours)

| case | category | expected | rag |
|---|---|---|---|
| f01 | close_analog | 2600-4200 | 3570 |
| f02 | close_analog | 2000-3300 | 2725 |
| f03 | close_analog | 2600-4200 | 3625 |
| f04 | close_analog | 2400-4000 | 2740 |
| g01 | partial_overlap | 4200-6800 | 1692 |
| g02 | partial_overlap | 3200-5200 | 1570 |
| g03 | partial_overlap | 3200-5200 | 4270 |
| g04 | partial_overlap | 2000-3600 | 1585 |
| g05 | partial_overlap | 3000-5000 | 1555 |
| q01 | no_analog | 1800-3200 | 2830 |
| q02 | no_analog | 1000-2200 | 1090 |
| q03 | no_analog | 700-1400 | 467 |
| q04 | no_analog | 1200-2400 | 1190 |
| q05 | no_analog | 3000-5500 | 935 |
