# RRG Regime Filter -- Smoothing & Noise Reduction Test

## Problem Statement

The raw RRG regime score at +/-3 threshold produces:
- 85 regime changes in 166 months (flip every 2 months)
- 86-87% of RISK-ON/OFF signals are 1-month flashes
- 57% of RISK-OFF signals are false alarms
- Score flips sign 53% of months

**Goal:** Find a filter that reduces false signals while preserving
crash detection with adequate lead time.

---
## Head-to-Head Comparison

| Variant | Changes | Whipsaws | RISK-OFF Signals | Precision | Crash Recall | Neutral% | Avg RISK-OFF Duration |
|---------|---------|----------|------------------|-----------|--------------|----------|----------------------|
| 0. Baseline (raw +/-3) | 85 | 32 | 23 | 43% | 9/13 (69%) | 63% | 1.2mo |
| 1. EMA(2) +/-3 | 41 | 12 | 10 | 60% | 6/13 (46%) | 81% | 1.4mo |
| 2. EMA(3) +/-3 | 20 | 7 | 8 | 38% | 3/13 (23%) | 91% | 1.2mo |
| 3. SMA(3) +/-3 | 20 | 7 | 6 | 17% | 1/13 (8%) | 92% | 1.2mo |
| 4. Raw +/-5 | 32 | 12 | 8 | 38% | 3/13 (23%) | 89% | 1.1mo |
| 5. EMA(3) +/-4 | 6 | 1 | 2 | 50% | 1/13 (8%) | 97% | 1.5mo |
| 6. Raw +/-3, 2mo confirm | 10 | 0 | 2 | 50% | 1/13 (8%) | 82% | 9.5mo |
| 7. Hysteresis (4/2) | 63 | 15 | 17 | 47% | 8/13 (62%) | 70% | 1.3mo |
| 8. Hysteresis (5/2) | 32 | 9 | 8 | 38% | 3/13 (23%) | 85% | 1.4mo |
| 9. EMA(3) + Hysteresis(4/2) | 6 | 0 | 2 | 50% | 1/13 (8%) | 96% | 2.0mo |
| 10. EMA(2) + Hysteresis(3.5/1.5) | 27 | 6 | 8 | 38% | 3/13 (23%) | 84% | 1.5mo |
| 11. Score+Momentum +/-3 | 114 | 35 | 40 | 42% | 13/13 (100%) | 44% | 1.2mo |
| 12. SMA(2) + Hysteresis(3.5/1.5) | 20 | 4 | 5 | 40% | 2/13 (15%) | 89% | 1.4mo |
| 13. EMA(3) + Hysteresis(3.5/1.0) | 14 | 3 | 5 | 20% | 1/13 (8%) | 92% | 1.4mo |

---
## Detailed Results

### 0. Baseline (raw +/-3)

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 28 | 1.2mo | 24 (86%) |
| RISK-OFF | 23 | 1.2mo | 20 (87%) |
| NEUTRAL | 35 | 3.0mo | 15 (43%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(-0.9), NEUTRAL(2.8), NEUTRAL(2.5), NEUTRAL(-1.2)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-2.9), NEUTRAL(0.6), NEUTRAL(-1.5), RISK-ON(4.7)] |
| China Devaluation | 2015-08 | 0mo | HIT |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.9), NEUTRAL(-1.1), NEUTRAL(-2.2), NEUTRAL(-1.9)] |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 2mo | HIT |
| Luna/UST Collapse | 2022-05 | 1mo | HIT |
| FTX Collapse | 2022-11 | 2mo | HIT |
| SVB Banking Crisis | 2023-03 | 3mo | HIT |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(1.2), NEUTRAL(-0.2), NEUTRAL(-2.0)] |
| Oct 2025 Mega Liq | 2025-10 | 0mo | HIT |
| Russia-Ukraine | 2022-02 | 3mo | HIT |

**False RISK-OFF signals (13):** 2012-05, 2013-08, 2015-01, 2015-12, 2016-06, 2017-02, 2017-05, 2017-08, 2018-12, 2021-07, 2022-06, 2023-08, 2023-10

### 1. EMA(2) +/-3

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 12 | 1.4mo | 8 (67%) |
| RISK-OFF | 10 | 1.4mo | 7 (70%) |
| NEUTRAL | 20 | 6.8mo | 3 (15%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(-0.0), NEUTRAL(1.9), NEUTRAL(2.3), NEUTRAL(-0.0)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-2.1), NEUTRAL(-0.3), NEUTRAL(-1.1), NEUTRAL(2.8)] |
| China Devaluation | 2015-08 | 0mo | HIT |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.2), NEUTRAL(-1.1), NEUTRAL(-1.8), NEUTRAL(-1.9)] |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 2mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.8), NEUTRAL(1.8), NEUTRAL(-1.5), RISK-ON(3.2)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(1.2), NEUTRAL(-2.7), NEUTRAL(2.6), NEUTRAL(0.9)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-2.6), NEUTRAL(0.8), NEUTRAL(1.2), NEUTRAL(-1.1)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.4), NEUTRAL(0.7), NEUTRAL(0.1), NEUTRAL(-1.3)] |
| Oct 2025 Mega Liq | 2025-10 | 0mo | HIT |
| Russia-Ukraine | 2022-02 | 3mo | HIT |

**False RISK-OFF signals (4):** 2012-05, 2016-01, 2018-12, 2023-10

### 2. EMA(3) +/-3

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 2 | 2.5mo | 0 (0%) |
| RISK-OFF | 8 | 1.2mo | 6 (75%) |
| NEUTRAL | 11 | 13.7mo | 2 (18%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(0.5), NEUTRAL(1.6), NEUTRAL(2.1), NEUTRAL(0.4)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-1.5), NEUTRAL(-0.5), NEUTRAL(-1.0), NEUTRAL(1.9)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.5), NEUTRAL(-2.6)] |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-1.7)] |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 1mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(1.2), NEUTRAL(-0.9), NEUTRAL(2.3)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(1.2), NEUTRAL(-1.7), NEUTRAL(1.8), NEUTRAL(0.9)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-1.8), NEUTRAL(0.4), NEUTRAL(0.9), NEUTRAL(-0.7)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.4), NEUTRAL(0.4), NEUTRAL(0.1), NEUTRAL(-0.9)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(0.1), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-2.8)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-2.7), NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.7)] |

**False RISK-OFF signals (5):** 2012-05, 2015-09, 2016-01, 2018-12, 2023-10

### 3. SMA(3) +/-3

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 4 | 1.8mo | 2 (50%) |
| RISK-OFF | 6 | 1.2mo | 5 (83%) |
| NEUTRAL | 11 | 13.8mo | 1 (9%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(1.1), NEUTRAL(1.0), NEUTRAL(1.5), NEUTRAL(1.4)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-1.0), NEUTRAL(-1.1), NEUTRAL(-1.3), NEUTRAL(1.3)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.3), NEUTRAL(0.5), NEUTRAL(-0.7), NEUTRAL(-2.4)] |
| Volmageddon Q4 | 2018-10 | -- | MISS [NEUTRAL(-1.1), NEUTRAL(-0.3), NEUTRAL(-0.0), NEUTRAL(-2.1)] |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(0.8), NEUTRAL(-1.5), NEUTRAL(-1.7), NEUTRAL(-1.7)] |
| Trade War Aug 2019 | 2019-08 | -- | MISS [NEUTRAL(-2.0), NEUTRAL(-2.2), NEUTRAL(-2.9), NEUTRAL(-1.5)] |
| COVID Crash | 2020-03 | 1mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(0.6), NEUTRAL(0.1), NEUTRAL(-0.3), NEUTRAL(1.9)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(0.4), NEUTRAL(-0.1), NEUTRAL(0.5), NEUTRAL(0.2)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(0.3), NEUTRAL(-0.6), NEUTRAL(-0.2), NEUTRAL(0.6)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-1.0), NEUTRAL(0.4), NEUTRAL(0.2), NEUTRAL(-0.3)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(1.1), NEUTRAL(-0.5), NEUTRAL(-1.9), NEUTRAL(-2.7)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-2.0), NEUTRAL(-0.6), NEUTRAL(-0.7), NEUTRAL(0.6)] |

**False RISK-OFF signals (5):** 2012-05, 2015-09, 2016-02, 2018-12, 2023-10

### 4. Raw +/-5

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 9 | 1.1mo | 8 (89%) |
| RISK-OFF | 8 | 1.1mo | 7 (88%) |
| NEUTRAL | 16 | 9.2mo | 1 (6%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(-0.9), NEUTRAL(2.8), NEUTRAL(2.5), NEUTRAL(-1.2)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-2.9), NEUTRAL(0.6), NEUTRAL(-1.5), NEUTRAL(4.7)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.3), NEUTRAL(-1.8), NEUTRAL(-0.6), NEUTRAL(-4.7)] |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.9), NEUTRAL(-1.1), NEUTRAL(-2.2), NEUTRAL(-1.9)] |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 2mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.8), NEUTRAL(3.1), NEUTRAL(-3.1), RISK-ON(5.6)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(0.8), NEUTRAL(-4.7), RISK-ON(5.3), NEUTRAL(0.0)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-4.4), NEUTRAL(2.5), NEUTRAL(1.4), NEUTRAL(-2.2)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(1.2), NEUTRAL(-0.2), NEUTRAL(-2.0)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(-1.8), NEUTRAL(-1.8), NEUTRAL(-2.2), NEUTRAL(-4.0)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-4.7), NEUTRAL(4.4), NEUTRAL(-1.9), NEUTRAL(-0.8)] |

**False RISK-OFF signals (5):** 2012-05, 2015-09, 2016-01, 2018-12, 2023-10

### 5. EMA(3) +/-4

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 1 | 2.0mo | 0 (0%) |
| RISK-OFF | 2 | 1.5mo | 1 (50%) |
| NEUTRAL | 4 | 40.2mo | 0 (0%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(0.5), NEUTRAL(1.6), NEUTRAL(2.1), NEUTRAL(0.4)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-1.5), NEUTRAL(-0.5), NEUTRAL(-1.0), NEUTRAL(1.9)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.5), NEUTRAL(-2.6)] |
| Volmageddon Q4 | 2018-10 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(-0.1), NEUTRAL(-0.6), NEUTRAL(-3.1)] |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-1.7)] |
| Trade War Aug 2019 | 2019-08 | -- | MISS [NEUTRAL(-3.2), NEUTRAL(-1.6), NEUTRAL(-1.2), NEUTRAL(-2.4)] |
| COVID Crash | 2020-03 | 1mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(1.2), NEUTRAL(-0.9), NEUTRAL(2.3)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(1.2), NEUTRAL(-1.7), NEUTRAL(1.8), NEUTRAL(0.9)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-1.8), NEUTRAL(0.4), NEUTRAL(0.9), NEUTRAL(-0.7)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.4), NEUTRAL(0.4), NEUTRAL(0.1), NEUTRAL(-0.9)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(0.1), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-2.8)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-2.7), NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.7)] |

**False RISK-OFF signals (1):** 2016-01

### 6. Raw +/-3, 2mo confirm

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 4 | 2.8mo | 0 (0%) |
| RISK-OFF | 2 | 9.5mo | 0 (0%) |
| NEUTRAL | 5 | 27.2mo | 0 (0%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(-0.9), NEUTRAL(2.8), NEUTRAL(2.5), NEUTRAL(-1.2)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-2.9), NEUTRAL(0.6), NEUTRAL(-1.5), NEUTRAL(4.7)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.3), NEUTRAL(-1.8), NEUTRAL(-0.6), NEUTRAL(-4.7)] |
| Volmageddon Q4 | 2018-10 | -- | MISS [NEUTRAL(0.8), NEUTRAL(0.3), NEUTRAL(-1.1), NEUTRAL(-5.6)] |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.9), NEUTRAL(-1.1), NEUTRAL(-2.2), NEUTRAL(-1.9)] |
| Trade War Aug 2019 | 2019-08 | -- | MISS [NEUTRAL(-7.8), NEUTRAL(0.0), NEUTRAL(-0.8), NEUTRAL(-3.6)] |
| COVID Crash | 2020-03 | 1mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.8), NEUTRAL(3.1), NEUTRAL(-3.1), NEUTRAL(5.6)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(0.8), NEUTRAL(-4.7), NEUTRAL(5.3), NEUTRAL(0.0)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-4.4), NEUTRAL(2.5), NEUTRAL(1.4), NEUTRAL(-2.2)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(1.2), NEUTRAL(-0.2), NEUTRAL(-2.0)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(-1.8), NEUTRAL(-1.8), NEUTRAL(-2.2), NEUTRAL(-4.0)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-4.7), NEUTRAL(4.4), NEUTRAL(-1.9), NEUTRAL(-0.8)] |

**False RISK-OFF signals (1):** 2015-09

### 7. Hysteresis (4/2)

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 20 | 1.4mo | 14 (70%) |
| RISK-OFF | 17 | 1.3mo | 14 (82%) |
| NEUTRAL | 27 | 4.3mo | 9 (33%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(-0.9), NEUTRAL(2.8), NEUTRAL(2.5), NEUTRAL(-1.2)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-2.9), NEUTRAL(0.6), NEUTRAL(-1.5), RISK-ON(4.7)] |
| China Devaluation | 2015-08 | 0mo | HIT |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.9), NEUTRAL(-1.1), NEUTRAL(-2.2), NEUTRAL(-1.9)] |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 2mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.8), NEUTRAL(3.1), NEUTRAL(-3.1), RISK-ON(5.6)] |
| FTX Collapse | 2022-11 | 2mo | HIT |
| SVB Banking Crisis | 2023-03 | 3mo | HIT |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(1.2), NEUTRAL(-0.2), NEUTRAL(-2.0)] |
| Oct 2025 Mega Liq | 2025-10 | 0mo | HIT |
| Russia-Ukraine | 2022-02 | 3mo | HIT |

**False RISK-OFF signals (9):** 2012-05, 2015-01, 2015-12, 2016-06, 2017-08, 2018-12, 2021-07, 2023-08, 2023-10

### 8. Hysteresis (5/2)

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 9 | 1.6mo | 5 (56%) |
| RISK-OFF | 8 | 1.4mo | 6 (75%) |
| NEUTRAL | 16 | 8.8mo | 2 (12%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(-0.9), NEUTRAL(2.8), NEUTRAL(2.5), NEUTRAL(-1.2)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-2.9), NEUTRAL(0.6), NEUTRAL(-1.5), NEUTRAL(4.7)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.3), NEUTRAL(-1.8), NEUTRAL(-0.6), NEUTRAL(-4.7)] |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.9), NEUTRAL(-1.1), NEUTRAL(-2.2), NEUTRAL(-1.9)] |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 2mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.8), NEUTRAL(3.1), NEUTRAL(-3.1), RISK-ON(5.6)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(0.8), NEUTRAL(-4.7), RISK-ON(5.3), NEUTRAL(0.0)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-4.4), NEUTRAL(2.5), NEUTRAL(1.4), NEUTRAL(-2.2)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(1.2), NEUTRAL(-0.2), NEUTRAL(-2.0)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(-1.8), NEUTRAL(-1.8), NEUTRAL(-2.2), NEUTRAL(-4.0)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-4.7), NEUTRAL(4.4), NEUTRAL(-1.9), NEUTRAL(-0.8)] |

**False RISK-OFF signals (5):** 2012-05, 2015-09, 2016-01, 2018-12, 2023-10

### 9. EMA(3) + Hysteresis(4/2)

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 1 | 3.0mo | 0 (0%) |
| RISK-OFF | 2 | 2.0mo | 0 (0%) |
| NEUTRAL | 4 | 39.8mo | 1 (25%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(0.5), NEUTRAL(1.6), NEUTRAL(2.1), NEUTRAL(0.4)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-1.5), NEUTRAL(-0.5), NEUTRAL(-1.0), NEUTRAL(1.9)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.5), NEUTRAL(-2.6)] |
| Volmageddon Q4 | 2018-10 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(-0.1), NEUTRAL(-0.6), NEUTRAL(-3.1)] |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-1.7)] |
| Trade War Aug 2019 | 2019-08 | -- | MISS [NEUTRAL(-3.2), NEUTRAL(-1.6), NEUTRAL(-1.2), NEUTRAL(-2.4)] |
| COVID Crash | 2020-03 | 1mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(1.2), NEUTRAL(-0.9), NEUTRAL(2.3)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(1.2), NEUTRAL(-1.7), NEUTRAL(1.8), NEUTRAL(0.9)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-1.8), NEUTRAL(0.4), NEUTRAL(0.9), NEUTRAL(-0.7)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.4), NEUTRAL(0.4), NEUTRAL(0.1), NEUTRAL(-0.9)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(0.1), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-2.8)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-2.7), NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.7)] |

**False RISK-OFF signals (1):** 2016-01

### 10. EMA(2) + Hysteresis(3.5/1.5)

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 7 | 2.1mo | 3 (43%) |
| RISK-OFF | 8 | 1.5mo | 5 (62%) |
| NEUTRAL | 13 | 10.7mo | 2 (15%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(-0.0), NEUTRAL(1.9), NEUTRAL(2.3), NEUTRAL(-0.0)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-2.1), NEUTRAL(-0.3), NEUTRAL(-1.1), NEUTRAL(2.8)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.8), NEUTRAL(-0.9), NEUTRAL(-0.7), NEUTRAL(-3.4)] |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.2), NEUTRAL(-1.1), NEUTRAL(-1.8), NEUTRAL(-1.9)] |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 2mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.8), NEUTRAL(1.8), NEUTRAL(-1.5), NEUTRAL(3.2)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(1.2), NEUTRAL(-2.7), NEUTRAL(2.6), NEUTRAL(0.9)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-2.6), NEUTRAL(0.8), NEUTRAL(1.2), NEUTRAL(-1.1)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.4), NEUTRAL(0.7), NEUTRAL(0.1), NEUTRAL(-1.3)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(-1.4), NEUTRAL(-1.9), NEUTRAL(-3.3)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-3.4), NEUTRAL(1.8), NEUTRAL(-0.7), NEUTRAL(-0.8)] |

**False RISK-OFF signals (5):** 2012-05, 2015-09, 2016-01, 2018-12, 2023-10

### 11. Score+Momentum +/-3

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 31 | 1.5mo | 19 (61%) |
| RISK-OFF | 40 | 1.2mo | 33 (82%) |
| NEUTRAL | 44 | 1.7mo | 28 (64%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | 0mo | HIT |
| Oil Crash & EM Crisis | 2014-10 | 3mo | HIT |
| China Devaluation | 2015-08 | 2mo | HIT |
| Volmageddon Q4 | 2018-10 | 0mo | HIT |
| US-China Trade War | 2018-06 | 3mo | HIT |
| Trade War Aug 2019 | 2019-08 | 3mo | HIT |
| COVID Crash | 2020-03 | 2mo | HIT |
| Luna/UST Collapse | 2022-05 | 3mo | HIT |
| FTX Collapse | 2022-11 | 2mo | HIT |
| SVB Banking Crisis | 2023-03 | 3mo | HIT |
| Trump Tariff 2025 | 2025-03 | 0mo | HIT |
| Oct 2025 Mega Liq | 2025-10 | 3mo | HIT |
| Russia-Ukraine | 2022-02 | 3mo | HIT |

**False RISK-OFF signals (23):** 2012-04, 2013-08, 2013-11, 2014-04, 2015-01, 2015-12, 2016-06, 2016-12, 2017-02, 2017-05, 2017-08, 2017-11, 2018-12, 2020-07, 2020-10, 2021-01, 2021-07, 2021-10, 2022-06, 2023-08, 2023-10, 2024-03, 2024-10

### 12. SMA(2) + Hysteresis(3.5/1.5)

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 5 | 2.2mo | 1 (20%) |
| RISK-OFF | 5 | 1.4mo | 3 (60%) |
| NEUTRAL | 11 | 13.5mo | 1 (9%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(0.2), NEUTRAL(1.0), NEUTRAL(2.7), NEUTRAL(0.7)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-1.9), NEUTRAL(-1.1), NEUTRAL(-0.4), NEUTRAL(1.6)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(1.6), NEUTRAL(-0.7), NEUTRAL(-1.2), NEUTRAL(-2.6)] |
| Volmageddon Q4 | 2018-10 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(0.6), NEUTRAL(-0.4), NEUTRAL(-3.3)] |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-1.6), NEUTRAL(-1.5), NEUTRAL(-1.6), NEUTRAL(-2.0)] |
| Trade War Aug 2019 | 2019-08 | 2mo | HIT |
| COVID Crash | 2020-03 | 1mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-1.3), NEUTRAL(1.2), NEUTRAL(0.0), NEUTRAL(1.3)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(2.2), NEUTRAL(-1.9), NEUTRAL(0.3), NEUTRAL(2.7)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-2.2), NEUTRAL(-0.9), NEUTRAL(2.0), NEUTRAL(-0.4)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(0.0), NEUTRAL(0.4), NEUTRAL(0.5), NEUTRAL(-1.1)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(0.2), NEUTRAL(-1.8), NEUTRAL(-2.0), NEUTRAL(-3.1)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-3.0), NEUTRAL(-0.1), NEUTRAL(1.3), NEUTRAL(-1.3)] |

**False RISK-OFF signals (3):** 2012-05, 2015-09, 2016-01

### 13. EMA(3) + Hysteresis(3.5/1.0)

**Regime Duration:**
| Regime | Count | Avg Duration | 1-mo Flashes |
|--------|-------|-------------|--------------|
| RISK-ON | 2 | 3.5mo | 0 (0%) |
| RISK-OFF | 5 | 1.4mo | 3 (60%) |
| NEUTRAL | 8 | 19.0mo | 1 (12%) |

**Crash Detection:**
| Event | Month | Lead | Result |
|-------|-------|------|--------|
| Taper Tantrum | 2013-06 | -- | MISS [NEUTRAL(0.5), NEUTRAL(1.6), NEUTRAL(2.1), NEUTRAL(0.4)] |
| Oil Crash & EM Crisis | 2014-10 | -- | MISS [NEUTRAL(-1.5), NEUTRAL(-0.5), NEUTRAL(-1.0), NEUTRAL(1.9)] |
| China Devaluation | 2015-08 | -- | MISS [NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.5), NEUTRAL(-2.6)] |
| Volmageddon Q4 | 2018-10 | -- | MISS [NEUTRAL(-0.5), NEUTRAL(-0.1), NEUTRAL(-0.6), NEUTRAL(-3.1)] |
| US-China Trade War | 2018-06 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-1.7)] |
| Trade War Aug 2019 | 2019-08 | -- | MISS [NEUTRAL(-3.2), NEUTRAL(-1.6), NEUTRAL(-1.2), NEUTRAL(-2.4)] |
| COVID Crash | 2020-03 | 1mo | HIT |
| Luna/UST Collapse | 2022-05 | -- | MISS [NEUTRAL(-0.7), NEUTRAL(1.2), NEUTRAL(-0.9), NEUTRAL(2.3)] |
| FTX Collapse | 2022-11 | -- | MISS [NEUTRAL(1.2), NEUTRAL(-1.7), NEUTRAL(1.8), NEUTRAL(0.9)] |
| SVB Banking Crisis | 2023-03 | -- | MISS [NEUTRAL(-1.8), NEUTRAL(0.4), NEUTRAL(0.9), NEUTRAL(-0.7)] |
| Trump Tariff 2025 | 2025-03 | -- | MISS [NEUTRAL(-0.4), NEUTRAL(0.4), NEUTRAL(0.1), NEUTRAL(-0.9)] |
| Oct 2025 Mega Liq | 2025-10 | -- | MISS [NEUTRAL(0.1), NEUTRAL(-0.9), NEUTRAL(-1.5), NEUTRAL(-2.8)] |
| Russia-Ukraine | 2022-02 | -- | MISS [NEUTRAL(-2.7), NEUTRAL(0.9), NEUTRAL(-0.5), NEUTRAL(-0.7)] |

**False RISK-OFF signals (4):** 2012-05, 2015-09, 2016-01, 2018-12

---
## Finding the Best Filter

### Composite Score (weighted)

Weights: Precision 30% + Recall 30% + Low Whipsaw 20% + Lead Time 20%

| Variant | Precision | Recall | Whipsaw Reduction | Score |
|---------|-----------|--------|-------------------|-------|
| 0. Baseline (raw +/-3) | 43% | 69% | 0% | **49.4** |
| 1. EMA(2) +/-3 | 60% | 46% | 62% | **62.1** |
| 2. EMA(3) +/-3 | 38% | 23% | 78% | **47.1** |
| 3. SMA(3) +/-3 | 17% | 8% | 78% | **29.6** |
| 4. Raw +/-5 | 38% | 23% | 62% | **47.3** |
| 5. EMA(3) +/-4 | 50% | 8% | 97% | **43.3** |
| 6. Raw +/-3, 2mo confirm | 50% | 8% | 100% | **44.0** |
| 7. Hysteresis (4/2) | 47% | 62% | 53% | **60.5** |
| 8. Hysteresis (5/2) | 38% | 23% | 72% | **49.2** |
| 9. EMA(3) + Hysteresis(4/2) | 50% | 8% | 100% | **44.0** |
| 10. EMA(2) + Hysteresis(3.5/1.5) | 38% | 23% | 81% | **51.1** |
| 11. Score+Momentum +/-3 | 42% | 100% | -9% | **58.9** |
| 12. SMA(2) + Hysteresis(3.5/1.5) | 40% | 15% | 88% | **44.1** |
| 13. EMA(3) + Hysteresis(3.5/1.0) | 20% | 8% | 91% | **33.1** |

### Winner: **1. EMA(2) +/-3** (score: 62.1)

---
## Recommendation for Production

Based on the analysis, the optimal approach depends on use case:

### For Crash Avoidance (conservative):
- Prioritize **recall** (catch all crashes) over precision
- Accept some false alarms to never miss a real crash
- Best: variant with highest recall + reasonable precision

### For Active Trading (balanced):
- Need both precision AND recall
- Can't afford false signals (each one costs a trade)
- Best: variant with highest composite score

### For Trend Confirmation (aggressive):
- Prioritize **precision** (only act on high-confidence signals)
- OK to miss some crashes if the signals you do get are reliable
- Best: variant with highest precision
