_Generated 2026-10-09 19:28 UTC_

# Generation eval

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 20 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 20 | 75% | 14% | 100% | 0% | 25s |
| all | baseline | 20 | 10% | 55% | n/a | 0% | 23s |
| close_analog | rag | 10 | 90% | 8% | 100% | 0% | 23s |
| close_analog | baseline | 10 | 0% | 58% | n/a | 0% | 24s |
| partial_overlap | rag | 6 | 83% | 14% | 100% | 0% | 25s |
| partial_overlap | baseline | 6 | 0% | 55% | n/a | 0% | 23s |
| out_of_domain | rag | 4 | 25% | 58% | n/a | 0% | 26s |
| out_of_domain | baseline | 4 | 50% | 38% | n/a | 0% | 22s |

## Per brief (midpoint hours)

| case | category | expected | rag | baseline |
|---|---|---|---|---|
| c01 | close_analog | 2200-3600 | 3055 | 1450 |
| c02 | close_analog | 4000-6000 | 5190 | 2120 |
| c03 | close_analog | 4500-7000 | 5630 | 1980 |
| c04 | close_analog | 2500-4200 | 4165 | 1420 |
| c05 | close_analog | 1000-1900 | 1945 | 835 |
| c06 | close_analog | 3200-5200 | 4655 | 1500 |
| c07 | close_analog | 2000-3300 | 2875 | 1890 |
| c08 | close_analog | 2600-4200 | 3675 | 1620 |
| c09 | close_analog | 3500-5500 | 4705 | 1810 |
| c10 | close_analog | 4000-6500 | 6120 | 1800 |
| c11 | partial_overlap | 3000-4800 | 3560 | 1670 |
| c12 | partial_overlap | 3000-5000 | 2900 | 1860 |
| c13 | partial_overlap | 2200-3800 | 2390 | 1430 |
| c14 | partial_overlap | 2000-3500 | 2390 | 1510 |
| c15 | partial_overlap | 3000-5000 | 4565 | 1620 |
| c16 | partial_overlap | 2500-4200 | 3350 | 1350 |
| c17 | out_of_domain | 300-800 | 1030 | 682 |
| c18 | out_of_domain | 500-1200 | 690 | 770 |
| c19 | out_of_domain | 3000-6000 | 1615 | 1690 |
| c20 | out_of_domain | 3500-6000 | 2240 | 2310 |
