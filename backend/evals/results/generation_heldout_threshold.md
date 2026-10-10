_Generated 2026-10-10 09:09 UTC_

# Generation eval (heldout set)

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 15 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 15 | 60% | 26% | 89% | 0% | 21s |
| all | baseline | 15 | 7% | 57% | n/a | 0% | 23s |
| close_analog | rag | 6 | 83% | 14% | 100% | 0% | 19s |
| close_analog | baseline | 6 | 0% | 61% | n/a | 0% | 25s |
| partial_overlap | rag | 5 | 40% | 48% | 67% | 0% | 24s |
| partial_overlap | baseline | 5 | 0% | 65% | n/a | 0% | 23s |
| out_of_domain | rag | 4 | 50% | 33% | n/a | 0% | 21s |
| out_of_domain | baseline | 4 | 25% | 38% | n/a | 0% | 19s |

## Per brief (midpoint hours)

| case | category | expected | rag | baseline |
|---|---|---|---|---|
| h01 | close_analog | 1800-3000 | 2600 | 1035 |
| h02 | close_analog | 3500-5500 | 3080 | 1560 |
| h03 | close_analog | 3500-6000 | 5430 | 1510 |
| h04 | close_analog | 2400-4000 | 3905 | 1840 |
| h05 | close_analog | 1100-2000 | 1575 | 915 |
| h06 | close_analog | 3000-5000 | 4555 | 970 |
| h07 | partial_overlap | 3200-5000 | 3395 | 1455 |
| h08 | partial_overlap | 3000-4800 | 2010 | 1425 |
| h09 | partial_overlap | 1500-2800 | 1600 | 1320 |
| h10 | partial_overlap | 4500-7000 | 1720 | 2005 |
| h11 | partial_overlap | 2800-4600 | 910 | 1105 |
| h12 | out_of_domain | 1800-3500 | 1630 | 1795 |
| h13 | out_of_domain | 700-1500 | 1128 | 790 |
| h14 | out_of_domain | 2500-4500 | 1915 | 1785 |
| h15 | out_of_domain | 1500-3000 | 1625 | 1260 |
