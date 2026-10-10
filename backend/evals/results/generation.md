_Generated 2026-10-10 09:24 UTC_

# Generation eval

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 20 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 20 | 95% | 8% | 100% | 0% | 23s |
| all | baseline | 20 | 15% | 56% | n/a | 0% | 19s |
| close_analog | rag | 10 | 100% | 6% | 100% | 0% | 21s |
| close_analog | baseline | 10 | 20% | 55% | n/a | 0% | 19s |
| partial_overlap | rag | 6 | 100% | 12% | 100% | 0% | 24s |
| partial_overlap | baseline | 6 | 0% | 56% | n/a | 0% | 16s |
| out_of_domain | rag | 4 | 75% | 26% | 100% | 0% | 25s |
| out_of_domain | baseline | 4 | 25% | 66% | n/a | 0% | 23s |

## Per brief (midpoint hours)

| case | category | expected | rag | baseline |
|---|---|---|---|---|
| c01 | close_analog | 2200-3600 | 2780 | 1540 |
| c02 | close_analog | 4000-6000 | 5210 | 1620 |
| c03 | close_analog | 4500-7000 | 5565 | 1700 |
| c04 | close_analog | 2500-4200 | 3335 | 1495 |
| c05 | close_analog | 1000-1900 | 1620 | 1080 |
| c06 | close_analog | 3200-5200 | 4650 | 1280 |
| c07 | close_analog | 2000-3300 | 2840 | 2110 |
| c08 | close_analog | 2600-4200 | 3660 | 2315 |
| c09 | close_analog | 3500-5500 | 4850 | 1570 |
| c10 | close_analog | 4000-6500 | 5430 | 2390 |
| c11 | partial_overlap | 3000-4800 | 4035 | 1350 |
| c12 | partial_overlap | 3000-5000 | 3240 | 1790 |
| c13 | partial_overlap | 2200-3800 | 2220 | 1420 |
| c14 | partial_overlap | 2000-3500 | 3080 | 1490 |
| c15 | partial_overlap | 3000-5000 | 4445 | 1450 |
| c16 | partial_overlap | 2500-4200 | 3340 | 1452 |
| c17 | out_of_domain | 300-800 | 880 | 900 |
| c18 | out_of_domain | 500-1200 | 605 | 595 |
| c19 | out_of_domain | 3000-6000 | 3460 | 1110 |
| c20 | out_of_domain | 3500-6000 | 5070 | 1490 |
