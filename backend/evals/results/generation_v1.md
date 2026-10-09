_Generated 2026-10-09 19:19 UTC_

# Generation eval

Model: `gemini-3.7-flash`, temperature 0.2, single run per brief, 20 briefs.

- in range: midpoint of total hours falls inside the expected range
- median error: |midpoint - expected midpoint| / expected midpoint
- cites refs: estimation_basis names at least one provided reference project
- fabricated refs: estimation_basis names a past project that was not provided

| category | mode | n | in range | median error | cites refs | fabricated refs | latency |
|---|---|---|---|---|---|---|---|
| all | rag | 20 | 55% | 20% | 100% | 0% | 22s |
| all | baseline | 20 | 0% | 83% | n/a | 0% | 21s |
| close_analog | rag | 10 | 100% | 6% | 100% | 0% | 22s |
| close_analog | baseline | 10 | 0% | 86% | n/a | 0% | 21s |
| partial_overlap | rag | 6 | 17% | 35% | 100% | 0% | 24s |
| partial_overlap | baseline | 6 | 0% | 85% | n/a | 0% | 22s |
| out_of_domain | rag | 4 | 0% | 81% | n/a | 0% | 22s |
| out_of_domain | baseline | 4 | 0% | 78% | n/a | 0% | 22s |

## Per brief (midpoint hours)

| case | category | expected | rag | baseline |
|---|---|---|---|---|
| c01 | close_analog | 2200-3600 | 2455 | 492 |
| c02 | close_analog | 4000-6000 | 5200 | 530 |
| c03 | close_analog | 4500-7000 | 5165 | 478 |
| c04 | close_analog | 2500-4200 | 3640 | 592 |
| c05 | close_analog | 1000-1900 | 1490 | 460 |
| c06 | close_analog | 3200-5200 | 4655 | 448 |
| c07 | close_analog | 2000-3300 | 2770 | 598 |
| c08 | close_analog | 2600-4200 | 3670 | 580 |
| c09 | close_analog | 3500-5500 | 4720 | 368 |
| c10 | close_analog | 4000-6500 | 5480 | 592 |
| c11 | partial_overlap | 3000-4800 | 2610 | 435 |
| c12 | partial_overlap | 3000-5000 | 2380 | 698 |
| c13 | partial_overlap | 2200-3800 | 1885 | 570 |
| c14 | partial_overlap | 2000-3500 | 1835 | 560 |
| c15 | partial_overlap | 3000-5000 | 2210 | 498 |
| c16 | partial_overlap | 2500-4200 | 2530 | 432 |
| c17 | out_of_domain | 300-800 | 235 | 269 |
| c18 | out_of_domain | 500-1200 | 210 | 237 |
| c19 | out_of_domain | 3000-6000 | 588 | 475 |
| c20 | out_of_domain | 3500-6000 | 535 | 765 |
