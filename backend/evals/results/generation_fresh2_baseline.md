_Generated 2026-10-11 14:50 UTC_

# Generation eval (fresh2 set)

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 14 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | baseline | 14 | 7% | 57% | n/a | 0% | 21s |
| close_analog | baseline | 4 | 0% | 59% | n/a | 0% | 26s |
| partial_overlap | baseline | 5 | 0% | 62% | n/a | 0% | 21s |
| no_analog | baseline | 5 | 20% | 44% | n/a | 0% | 18s |

## Per brief (midpoint hours)

| case | category | expected | baseline |
|---|---|---|---|
| f01 | close_analog | 2600-4200 | 1510 |
| f02 | close_analog | 2000-3300 | 1098 |
| f03 | close_analog | 2600-4200 | 1380 |
| f04 | close_analog | 2400-4000 | 1190 |
| g01 | partial_overlap | 4200-6800 | 1390 |
| g02 | partial_overlap | 3200-5200 | 1895 |
| g03 | partial_overlap | 3200-5200 | 1355 |
| g04 | partial_overlap | 2000-3600 | 1890 |
| g05 | partial_overlap | 3000-5000 | 1505 |
| q01 | no_analog | 1800-3200 | 1305 |
| q02 | no_analog | 1000-2200 | 900 |
| q03 | no_analog | 700-1400 | 992 |
| q04 | no_analog | 1200-2400 | 1010 |
| q05 | no_analog | 3000-5500 | 1025 |
