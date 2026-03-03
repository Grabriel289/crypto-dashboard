# ABM Signal Validation — Results
## Run date: 2026-03-03 08:43

### Ground Truth Summary
- Seasons detected: 20
- Date range: 2019-03-12 00:00:00 to 2024-12-17 00:00:00
- Seasons:
  - Season 1: 2019-03-12 00:00:00 → 2019-03-30 00:00:00 (peak: 2019-03-29 00:00:00, 18d, max outperf: 19.98%)
  - Season 2: 2019-06-06 00:00:00 → 2019-06-15 00:00:00 (peak: 2019-06-12 00:00:00, 10d, max outperf: 42.31%)
  - Season 3: 2019-10-04 00:00:00 → 2019-10-17 00:00:00 (peak: 2019-10-14 00:00:00, 14d, max outperf: 19.82%)
  - Season 4: 2019-11-25 00:00:00 → 2019-12-04 00:00:00 (peak: 2019-12-02 00:00:00, 10d, max outperf: 17.09%)
  - Season 5: 2020-01-30 00:00:00 → 2020-02-24 00:00:00 (peak: 2020-02-12 00:00:00, 26d, max outperf: 36.15%)
  - Season 6: 2020-04-21 00:00:00 → 2020-04-29 00:00:00 (peak: 2020-04-28 00:00:00, 9d, max outperf: 19.73%)
  - Season 7: 2020-06-03 00:00:00 → 2020-09-02 00:00:00 (peak: 2020-08-04 00:00:00, 91d, max outperf: 42.54%)
  - Season 8: 2020-11-28 00:00:00 → 2020-12-07 00:00:00 (peak: 2020-12-05 00:00:00, 10d, max outperf: 37.55%)
  - Season 9: 2021-01-16 00:00:00 → 2021-03-11 00:00:00 (peak: 2021-02-10 00:00:00, 55d, max outperf: 198.07%)
  - Season 10: 2021-03-25 00:00:00 → 2021-05-21 00:00:00 (peak: 2021-05-07 00:00:00, 58d, max outperf: 106.87%)
  - Season 11: 2021-08-13 00:00:00 → 2021-09-19 00:00:00 (peak: 2021-09-08 00:00:00, 38d, max outperf: 62.85%)
  - Season 12: 2021-10-26 00:00:00 → 2021-11-23 00:00:00 (peak: 2021-10-27 00:00:00, 28d, max outperf: 37.67%)
  - Season 13: 2022-03-29 00:00:00 → 2022-04-10 00:00:00 (peak: 2022-04-03 00:00:00, 13d, max outperf: 20.18%)
  - Season 14: 2022-08-04 00:00:00 → 2022-08-14 00:00:00 (peak: 2022-08-11 00:00:00, 11d, max outperf: 22.61%)
  - Season 15: 2023-01-15 00:00:00 → 2023-02-12 00:00:00 (peak: 2023-01-28 00:00:00, 29d, max outperf: 42.23%)
  - Season 16: 2023-07-14 00:00:00 → 2023-07-24 00:00:00 (peak: 2023-07-20 00:00:00, 11d, max outperf: 16.32%)
  - Season 17: 2023-11-08 00:00:00 → 2024-01-19 00:00:00 (peak: 2023-12-27 00:00:00, 72d, max outperf: 32.57%)
  - Season 18: 2024-03-01 00:00:00 → 2024-03-31 00:00:00 (peak: 2024-03-09 00:00:00, 31d, max outperf: 62.57%)
  - Season 19: 2024-09-26 00:00:00 → 2024-10-18 00:00:00 (peak: 2024-09-30 00:00:00, 22d, max outperf: 19.06%)
  - Season 20: 2024-11-24 00:00:00 → 2024-12-17 00:00:00 (peak: 2024-12-03 00:00:00, 24d, max outperf: 72.99%)

### Test A — BM Lead Time
| Method | Median Lead (days) | Min | Max | Detected/Total |
|--------|--------------------|-----|-----|----------------|
| BM_14D | 55 | 29 | 60 | 19/20 |
| BM_30D | 57 | 15 | 60 | 19/20 |
| EMA | 33 | -7 | 56 | 19/20 |

### Test B — BM False Signal Rate
| Method | Total Signals | False Rate | Signals/Year |
|--------|---------------|------------|--------------|
| BM_14D | 831 | 70.5% | 145.7 |
| BM_30D | 918 | 77.6% | 160.9 |
| EMA | 48 | 45.8% | 8.4 |

### Test C — ETH/BTC ROC Peak Lead Time
| Method | Median Lead (days) | Detected/Total |
|--------|--------------------|----------------|
| ROC_7D | 4 | 20/20 |
| ROC_14D | 4 | 18/20 |
| ROC_7D+3D | -2 | 19/20 |

### Test D — ETH/BTC ROC False Alarm Rate
| Method | Total Warnings | False Alarm | Warnings/Year |
|--------|----------------|-------------|---------------|
| ROC_7D | 172 | 48.8% | 28.7 |
| ROC_14D | 116 | 47.4% | 19.3 |
| ROC_7D+3D | 115 | 45.2% | 19.2 |

### Test E — Best Combination
Rank 1: EMA + ROC_7D — Score: 51.6
Rank 2: EMA + ROC_14D — Score: 51.4
Rank 3: EMA + ROC_7D+3D — Score: 46.5

### Verdict
**RECOMMENDED: EMA + ETH/BTC ROC_7D**
→ Update ABM_Spec_v2.md Section 2 and 3 accordingly

### Score Breakdown (Top 3)
| Rank | BM | ROC | BM Lead | BM False | BM Noise | ROC Lead | ROC False | ROC Noise | Score |
|------|----|-----|---------|----------|----------|----------|-----------|-----------|-------|
| 1 | EMA | ROC_7D | 33.0d | 45.8% | 8.4/yr | 4.0d | 48.8% | 28.7/yr | 51.6 |
| 2 | EMA | ROC_14D | 33.0d | 45.8% | 8.4/yr | 3.5d | 47.4% | 19.3/yr | 51.4 |
| 3 | EMA | ROC_7D+3D | 33.0d | 45.8% | 8.4/yr | -2.0d | 45.2% | 19.2/yr | 46.5 |