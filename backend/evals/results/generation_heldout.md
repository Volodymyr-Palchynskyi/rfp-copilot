_Generated 2026-10-10 09:28 UTC_

# Generation eval (heldout set)

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 15 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 15 | 80% | 20% | 93% | 0% | 26s |
| all | baseline | 15 | 13% | 53% | n/a | 0% | 20s |
| close_analog | rag | 6 | 83% | 13% | 83% | 0% | 27s |
| close_analog | baseline | 6 | 17% | 58% | n/a | 0% | 19s |
| partial_overlap | rag | 5 | 100% | 19% | 100% | 0% | 23s |
| partial_overlap | baseline | 5 | 0% | 59% | n/a | 0% | 20s |
| out_of_domain | rag | 4 | 50% | 36% | 100% | 0% | 27s |
| out_of_domain | baseline | 4 | 25% | 45% | n/a | 0% | 22s |

## Per brief (midpoint hours)

| case | category | expected | rag | baseline |
|---|---|---|---|---|
| h01 | close_analog | 1800-3000 | 2640 | 1395 |
| h02 | close_analog | 3500-5500 | 5590 | 1505 |
| h03 | close_analog | 3500-6000 | 5200 | 1495 |
| h04 | close_analog | 2400-4000 | 3840 | 1630 |
| h05 | close_analog | 1100-2000 | 1675 | 1100 |
| h06 | close_analog | 3000-5000 | 4605 | 1095 |
| h07 | partial_overlap | 3200-5000 | 3520 | 1665 |
| h08 | partial_overlap | 3000-4800 | 3140 | 1620 |
| h09 | partial_overlap | 1500-2800 | 1690 | 1405 |
| h10 | partial_overlap | 4500-7000 | 4605 | 1830 |
| h11 | partial_overlap | 2800-4600 | 4215 | 935 |
| h12 | out_of_domain | 1800-3500 | 3190 | 1345 |
| h13 | out_of_domain | 700-1500 | 2190 | 1122 |
| h14 | out_of_domain | 2500-4500 | 1790 | 1650 |
| h15 | out_of_domain | 1500-3000 | 2760 | 1338 |
