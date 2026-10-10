_Generated 2026-10-10 09:40 UTC_

# Generation eval (fresh set)

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 13 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 13 | 38% | 34% | 91% | 0% | 25s |
| all | baseline | 13 | 15% | 57% | n/a | 0% | 21s |
| close_analog | rag | 5 | 80% | 15% | 100% | 0% | 25s |
| close_analog | baseline | 5 | 0% | 61% | n/a | 0% | 22s |
| partial_overlap | rag | 4 | 25% | 39% | 75% | 0% | 28s |
| partial_overlap | baseline | 4 | 0% | 63% | n/a | 0% | 22s |
| no_analog | rag | 4 | 0% | 52% | 100% | 0% | 23s |
| no_analog | baseline | 4 | 50% | 33% | n/a | 0% | 18s |

## Per brief (midpoint hours)

| case | category | expected | rag | baseline |
|---|---|---|---|---|
| n01 | close_analog | 2400-4000 | 2265 | 1360 |
| n02 | close_analog | 3800-6200 | 5070 | 1925 |
| n03 | close_analog | 3000-5000 | 4690 | 1575 |
| n04 | close_analog | 1000-1900 | 1665 | 742 |
| n05 | close_analog | 3800-5800 | 5200 | 1495 |
| n06 | partial_overlap | 2200-3800 | 4480 | 1905 |
| n07 | partial_overlap | 2800-4500 | 3110 | 1260 |
| n08 | partial_overlap | 3200-5200 | 2760 | 1630 |
| n09 | partial_overlap | 1800-3200 | 1430 | 702 |
| n10 | no_analog | 1200-2400 | 960 | 1470 |
| n11 | no_analog | 700-1500 | 1680 | 880 |
| n12 | no_analog | 1500-3000 | 3565 | 1145 |
| n13 | no_analog | 900-1800 | 660 | 730 |
