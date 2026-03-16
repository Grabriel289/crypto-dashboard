# RRG Composite Regime Filter -- Multi-Factor Noise Reduction

## Approach

Single-score smoothing (EMA, SMA, thresholds) fails the precision-recall tradeoff:
- Aggressive smoothing kills recall (8-23% crash detection)
- Light smoothing keeps noise (85 changes, 57% false alarms)

**Multi-factor composite** combines 5 independent signals:
1. **Score Level** (raw, no smoothing) -- preserves speed
2. **Score Trend** (2-month direction) -- catches deterioration
3. **Safe-Haven Rotation** (GLD+TLT+UUP positions) -- strongest crash predictor
4. **BTC Quadrant** (Leading/Lagging) -- crypto-specific signal
5. **Risk Breadth** (% risk assets bullish) -- broad confirmation

---
## Head-to-Head: All Variants

| Variant | Changes | Whipsaws | R-OFF Signals | Precision | Recall | Neutral% | Avg R-OFF Dur |
|---------|---------|----------|---------------|-----------|--------|----------|---------------|
| 0. Baseline (raw +/-3) | 85 | 32 | 23 | **43%** | **9/13 (69%)** | 63% | 1.2mo (20/23 flash) |
| V1. Conviction 3/5 | 91 | 27 | 24 | **54%** | **12/13 (92%)** | 62% | 1.1mo (22/24 flash) |
| V2. Conviction 4/5 | 46 | 17 | 8 | **50%** | **3/13 (23%)** | 84% | 1.1mo (7/8 flash) |
| V3. Weighted +/-4 | 62 | 22 | 15 | **60%** | **8/13 (62%)** | 75% | 1.2mo (13/15 flash) |
| V4. Weighted+Hyst(4/1.5) | 58 | 13 | 15 | **60%** | **8/13 (62%)** | 70% | 1.5mo (10/15 flash) |
| V5. Weighted +/-3 | 91 | 30 | 27 | **52%** | **12/13 (92%)** | 60% | 1.2mo (23/27 flash) |
| V6. Weighted+Hyst(3.5/1) | 72 | 16 | 21 | **57%** | **11/13 (85%)** | 60% | 1.6mo (14/21 flash) |

---
## Crash Detection: Event-by-Event Comparison

| Event | Month | Baseline (raw +/-3) | Conviction 3/5 | Conviction 4/5 | Weighted +/-4 | Weighted+Hyst(4/1.5) | Weighted +/-3 | Weighted+Hyst(3.5/1) |
|-------|-------|---|---|---|---|---|---|---|
| Taper Tantrum | 2013-06 | MISS | MISS | MISS | MISS | MISS | MISS | MISS |
| Oil Crash & EM Crisis | 2014-10 | MISS | HIT 3mo | MISS | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo |
| China Devaluation | 2015-08 | HIT 0mo | HIT 0mo | MISS | HIT 0mo | HIT 0mo | HIT 0mo | HIT 0mo |
| Volmageddon Q4 | 2018-10 | HIT 0mo | HIT 0mo | MISS | HIT 0mo | HIT 0mo | HIT 0mo | HIT 0mo |
| US-China Trade War | 2018-06 | MISS | HIT 3mo | MISS | MISS | MISS | HIT 3mo | HIT 3mo |
| Trade War Aug 2019 | 2019-08 | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo |
| COVID Crash | 2020-03 | HIT 2mo | HIT 2mo | HIT 2mo | HIT 2mo | HIT 2mo | HIT 2mo | HIT 2mo |
| Luna/UST Collapse | 2022-05 | HIT 1mo | HIT 1mo | MISS | HIT 1mo | HIT 1mo | HIT 1mo | HIT 1mo |
| FTX Collapse | 2022-11 | HIT 2mo | HIT 2mo | MISS | MISS | MISS | HIT 2mo | MISS |
| SVB Banking Crisis | 2023-03 | HIT 3mo | HIT 3mo | MISS | MISS | MISS | HIT 3mo | HIT 3mo |
| Trump Tariff 2025 | 2025-03 | MISS | HIT 0mo | MISS | MISS | MISS | HIT 0mo | HIT 0mo |
| Oct 2025 Mega Liq | 2025-10 | HIT 0mo | HIT 1mo | MISS | HIT 1mo | HIT 1mo | HIT 2mo | HIT 2mo |
| Russia-Ukraine | 2022-02 | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo | HIT 3mo |

---
## Best Variant Deep Dive: V6. Weighted+Hyst(3.5/1)

**Regime changes:** 72 (vs 85 baseline)
**Whipsaws:** 16 (vs 32 baseline)
**RISK-OFF precision:** 57% (vs 43% baseline)
**Crash recall:** 11/13 (85%)

### Regime Duration:
| Regime | Count | Avg Duration | Max | 1-mo Flashes |
|--------|-------|-------------|-----|--------------|
| RISK-ON | 22 | 1.5mo | 3mo | 12 (55%) |
| RISK-OFF | 21 | 1.6mo | 3mo | 14 (67%) |
| NEUTRAL | 30 | 3.3mo | 9mo | 9 (30%) |

### False RISK-OFF Signals (9):
  - 2012-05
  - 2013-08
  - 2014-04
  - 2015-01
  - 2016-01
  - 2021-07
  - 2022-06
  - 2023-08
  - 2024-03

### All Events Assessment:
| Event | Month | Type | Regime At | Before | Hit? | Lead |
|-------|-------|------|-----------|--------|------|------|
| Taper Tantrum | 2013-06 | CRASH | NEUTRAL (-2.5) | NEUTRAL | no | 0mo |
| Oil Crash & EM Crisis | 2014-10 | CRASH | RISK-ON (+4.5) | RISK-OFF | **YES** | 3mo |
| China Devaluation | 2015-08 | CRASH | RISK-OFF (-4.8) | NEUTRAL | **YES** | 0mo |
| Volmageddon Q4 | 2018-10 | CRASH | RISK-OFF (-5.2) | NEUTRAL | **YES** | 0mo |
| US-China Trade War | 2018-06 | CRASH | NEUTRAL (-2.0) | NEUTRAL | **YES** | 3mo |
| Trade War Aug 2019 | 2019-08 | CRASH | RISK-OFF (-4.0) | NEUTRAL | **YES** | 3mo |
| COVID Crash | 2020-03 | CRASH | RISK-OFF (-4.0) | RISK-OFF | **YES** | 2mo |
| Luna/UST Collapse | 2022-05 | CRASH | NEUTRAL (+3.2) | RISK-OFF | **YES** | 1mo |
| FTX Collapse | 2022-11 | CRASH | NEUTRAL (+0.5) | RISK-ON | no | 0mo |
| SVB Banking Crisis | 2023-03 | CRASH | NEUTRAL (-2.5) | RISK-ON | **YES** | 3mo |
| Trump Tariff 2025 | 2025-03 | CRASH | RISK-OFF (-3.8) | NEUTRAL | **YES** | 0mo |
| Oct 2025 Mega Liq | 2025-10 | CRASH | RISK-OFF (-2.8) | RISK-OFF | **YES** | 2mo |
| Russia-Ukraine | 2022-02 | CRASH | NEUTRAL (-1.0) | NEUTRAL | **YES** | 3mo |
| BTC 2013 Peak | 2013-11 | PEAK | NEUTRAL (-1.5) | NEUTRAL | **YES** | 0mo |
| BTC 2017 Peak | 2017-12 | PEAK | NEUTRAL (-1.0) | NEUTRAL | **YES** | 0mo |
| BTC 2021 ATH | 2021-11 | PEAK | RISK-OFF (-5.5) | NEUTRAL | **YES** | 0mo |
| BTC ETF $73K | 2024-03 | PEAK | RISK-OFF (-3.8) | RISK-ON | no | 0mo |
| BTC 2015 Bottom | 2015-01 | BOTTOM | RISK-OFF (-5.5) | NEUTRAL | **YES** | 0mo |
| Crypto Winter Bottom | 2018-12 | BOTTOM | RISK-OFF (-3.8) | RISK-OFF | **YES** | 0mo |
| BTC Cycle Bottom | 2022-11 | BOTTOM | NEUTRAL (+0.5) | RISK-ON | no | 0mo |
| Post-COVID Rally | 2020-06 | BULLISH | RISK-ON (+3.0) | RISK-ON | **YES** | 0mo |
| Powell Pivot | 2019-01 | BULLISH | RISK-ON (+5.5) | RISK-OFF | **YES** | 0mo |
| QE3 Launch | 2012-09 | BULLISH | NEUTRAL (+0.0) | NEUTRAL | no | 0mo |
| First Rate Cut | 2024-09 | BULLISH | NEUTRAL (+2.5) | NEUTRAL | no | 0mo |

---
## Monthly Composite Score Timeline (Best Variant)

| Month | Raw Score | SH Rotation | BTC Quad | Risk Breadth | Composite | Regime |
|-------|-----------|-------------|----------|-------------|-----------|--------|
| 2012-01 | +0.3 | 1/3 | nan | 46% | +0.0 | NEUTRAL |
| 2012-02 | +4.7 | 0/3 | nan | 73% | +4.0 | RISK-ON |
| 2012-03 | -0.6 | 3/3 | nan | 54% | -1.2 | NEUTRAL |
| 2012-04 | -1.2 | 2/3 | nan | 46% | -2.5 | NEUTRAL |
| 2012-05 | -7.2 | 3/3 | nan | 9% | -7.0 | RISK-OFF |
| 2012-06 | +8.4 | 0/3 | nan | 91% | +6.5 | RISK-ON |
| 2012-07 | -2.8 | 2/3 | nan | 36% | -0.5 | NEUTRAL |
| 2012-08 | +1.2 | 1/3 | nan | 54% | -0.8 | NEUTRAL |
| 2012-09 | -0.9 | 1/3 | nan | 36% | +0.0 | NEUTRAL |
| 2012-10 | +1.6 | 1/3 | nan | 64% | +0.8 | NEUTRAL |
| 2012-11 | -1.6 | 2/3 | nan | 46% | -1.0 | NEUTRAL |
| 2012-12 | +4.4 | 1/3 | nan | 64% | +2.5 | NEUTRAL |
| 2013-01 | +3.1 | 0/3 | nan | 54% | +4.8 | RISK-ON |
| 2013-02 | +1.2 | 2/3 | nan | 64% | -1.0 | NEUTRAL |
| 2013-03 | -0.9 | 3/3 | nan | 54% | -2.8 | NEUTRAL |
| 2013-04 | +2.8 | 1/3 | nan | 64% | +1.8 | NEUTRAL |
| 2013-05 | +2.5 | 1/3 | nan | 64% | +2.5 | NEUTRAL |
| 2013-06 << Taper Tantrum | -1.2 | 2/3 | nan | 36% | -2.5 | NEUTRAL |
| 2013-07 | +1.2 | 1/3 | nan | 46% | +0.0 | NEUTRAL |
| 2013-08 | -3.8 | 2/3 | nan | 27% | -3.5 | RISK-OFF |
| 2013-09 | +2.8 | 1/3 | nan | 54% | +1.8 | NEUTRAL |
| 2013-10 | -2.1 | 0/3 | Leading | 17% | +0.0 | NEUTRAL |
| 2013-11 << BTC 2013 Peak | -2.9 | 0/3 | Leading | 8% | -1.5 | NEUTRAL |
| 2013-12 | +3.8 | 3/3 | Lagging | 92% | +1.0 | NEUTRAL |
| 2014-01 | -0.6 | 3/3 | Weakening | 83% | -0.2 | NEUTRAL |
| 2014-02 | +3.5 | 3/3 | Lagging | 92% | -0.5 | NEUTRAL |
| 2014-03 | +2.6 | 3/3 | Lagging | 83% | +0.2 | NEUTRAL |
| 2014-04 | -1.8 | 3/3 | Lagging | 58% | -3.8 | RISK-OFF |
| 2014-05 | +0.9 | 0/3 | Leading | 33% | +1.8 | NEUTRAL |
| 2014-06 | -0.9 | 1/3 | Improving | 42% | +0.5 | NEUTRAL |
| 2014-07 | -2.9 | 2/3 | Lagging | 33% | -4.5 | RISK-OFF |
| 2014-08 | +0.6 | 3/3 | Lagging | 67% | -1.5 | RISK-OFF |
| 2014-09 | -1.5 | 3/3 | Lagging | 50% | -2.2 | RISK-OFF |
| 2014-10 << Oil Crash & EM Crisis | +4.7 | 0/3 | Lagging | 67% | +4.5 | RISK-ON |
| 2014-11 | +1.8 | 2/3 | Leading | 58% | +1.5 | RISK-ON |
| 2014-12 | +0.6 | 2/3 | Lagging | 50% | -2.8 | NEUTRAL |
| 2015-01 | -4.4 | 3/3 | Lagging | 42% | -5.5 | RISK-OFF |
| 2015-02 | +6.5 | 0/3 | Improving | 75% | +7.0 | RISK-ON |
| 2015-03 | -2.4 | 2/3 | Lagging | 42% | -2.2 | NEUTRAL |
| 2015-04 | +2.9 | 0/3 | Improving | 50% | +3.0 | NEUTRAL |
| 2015-05 | +0.3 | 1/3 | Leading | 58% | +2.5 | NEUTRAL |
| 2015-06 | -1.8 | 1/3 | Leading | 33% | -1.2 | NEUTRAL |
| 2015-07 | -0.6 | 2/3 | Leading | 50% | +0.8 | NEUTRAL |
| 2015-08 << China Devaluation | -4.7 | 3/3 | Lagging | 42% | -4.8 | RISK-OFF |
| 2015-09 | -5.0 | 3/3 | Leading | 33% | -5.2 | RISK-OFF |
| 2015-10 | +3.5 | 0/3 | Leading | 58% | +5.8 | RISK-ON |
| 2015-11 | +2.4 | 1/3 | Leading | 67% | +5.0 | RISK-ON |
| 2015-12 | -4.4 | 2/3 | Leading | 42% | -2.5 | NEUTRAL |
| 2016-01 | -6.5 | 3/3 | Lagging | 25% | -7.2 | RISK-OFF |
| 2016-02 | -2.1 | 1/3 | Weakening | 33% | -1.5 | RISK-OFF |
| 2016-03 | +4.1 | 0/3 | Lagging | 67% | +4.5 | RISK-ON |
| 2016-04 | -0.9 | 0/3 | Weakening | 33% | +0.2 | NEUTRAL |
| 2016-05 | +4.7 | 1/3 | Leading | 75% | +3.5 | RISK-ON |
| 2016-06 | -4.1 | 2/3 | Leading | 25% | -2.5 | NEUTRAL |
| 2016-07 | +3.8 | 0/3 | Lagging | 67% | +3.0 | NEUTRAL |
| 2016-08 | +5.9 | 2/3 | Leading | 92% | +5.0 | RISK-ON |
| 2016-09 | +4.1 | 0/3 | Weakening | 67% | +3.5 | RISK-ON |
| 2016-10 | +0.3 | 1/3 | Leading | 50% | +0.2 | NEUTRAL |
| 2016-11 | +0.9 | 1/3 | Weakening | 42% | -1.2 | NEUTRAL |
| 2016-12 | -2.4 | 2/3 | Leading | 25% | -2.5 | NEUTRAL |
| 2017-01 | -1.5 | 2/3 | Lagging | 42% | -2.8 | NEUTRAL |
| 2017-02 | -3.5 | 2/3 | Leading | 25% | -1.8 | NEUTRAL |
| 2017-03 | -1.1 | 2/3 | Lagging | 54% | -1.2 | NEUTRAL |
| 2017-04 | -1.7 | 2/3 | Leading | 38% | +0.0 | NEUTRAL |
| 2017-05 | -3.1 | 1/3 | Leading | 23% | -1.5 | NEUTRAL |
| 2017-06 | +0.8 | 2/3 | Weakening | 54% | +0.0 | NEUTRAL |
| 2017-07 | +3.3 | 0/3 | Weakening | 62% | +4.2 | RISK-ON |
| 2017-08 | -4.2 | 1/3 | Leading | 15% | -3.0 | NEUTRAL |
| 2017-09 | +4.2 | 1/3 | Lagging | 77% | +1.5 | NEUTRAL |
| 2017-10 | +0.0 | 1/3 | Weakening | 54% | +1.8 | NEUTRAL |
| 2017-11 | -1.7 | 2/3 | Leading | 46% | -1.5 | NEUTRAL |
| 2017-12 << BTC 2017 Peak | -0.3 | 3/3 | Weakening | 69% | -1.0 | NEUTRAL |
| 2018-01 | +5.6 | 1/3 | Lagging | 92% | +4.0 | RISK-ON |
| 2018-02 | -1.4 | 3/3 | Weakening | 62% | -1.8 | NEUTRAL |
| 2018-03 | -1.9 | 3/3 | Lagging | 54% | -3.8 | RISK-OFF |
| 2018-04 | -1.1 | 1/3 | Leading | 38% | +1.0 | NEUTRAL |
| 2018-05 | -2.2 | 2/3 | Lagging | 46% | -3.0 | NEUTRAL |
| 2018-06 << US-China Trade War | -1.9 | 2/3 | Lagging | 46% | -2.0 | NEUTRAL |
| 2018-07 | +0.8 | 0/3 | Leading | 38% | +3.2 | NEUTRAL |
| 2018-08 | +0.3 | 2/3 | Lagging | 54% | -0.5 | NEUTRAL |
| 2018-09 | -1.1 | 2/3 | Lagging | 46% | -2.0 | NEUTRAL |
| 2018-10 << Volmageddon Q4 | -5.6 | 3/3 | Leading | 31% | -5.2 | RISK-OFF |
| 2018-11 | +0.3 | 2/3 | Lagging | 62% | -1.2 | RISK-OFF |
| 2018-12 | -5.6 | 3/3 | Leading | 31% | -3.8 | RISK-OFF |
| 2019-01 | +7.8 | 0/3 | Lagging | 85% | +5.5 | RISK-ON |
| 2019-02 | +3.6 | 0/3 | Leading | 54% | +5.8 | RISK-ON |
| 2019-03 | +0.8 | 1/3 | Leading | 46% | -0.5 | NEUTRAL |
| 2019-04 | +1.1 | 0/3 | Leading | 38% | +1.8 | NEUTRAL |
| 2019-05 | -7.8 | 3/3 | Leading | 15% | -6.0 | RISK-OFF |
| 2019-06 | +0.0 | 1/3 | Weakening | 46% | -0.5 | NEUTRAL |
| 2019-07 | -0.8 | 3/3 | Lagging | 69% | +0.0 | NEUTRAL |
| 2019-08 << Trade War Aug 2019 | -3.6 | 3/3 | Lagging | 54% | -4.0 | RISK-OFF |
| 2019-09 | +7.2 | 1/3 | Lagging | 92% | +4.0 | RISK-ON |
| 2019-10 | +7.2 | 0/3 | Weakening | 85% | +6.0 | RISK-ON |
| 2019-11 | +3.9 | 2/3 | Lagging | 85% | -0.2 | NEUTRAL |
| 2019-12 | +1.9 | 0/3 | Lagging | 46% | -1.0 | NEUTRAL |
| 2020-01 | -6.7 | 3/3 | Leading | 23% | -5.2 | RISK-OFF |
| 2020-02 | -6.7 | 3/3 | Leading | 23% | -5.2 | RISK-OFF |
| 2020-03 << COVID Crash | -4.2 | 3/3 | Lagging | 31% | -4.0 | RISK-OFF |
| 2020-04 | +4.2 | 0/3 | Leading | 62% | +5.8 | RISK-ON |
| 2020-05 | +1.4 | 0/3 | Leading | 54% | +4.8 | RISK-ON |
| 2020-06 | +4.4 | 0/3 | Lagging | 69% | +3.0 | RISK-ON |
| 2020-07 | -1.7 | 1/3 | Leading | 38% | +0.2 | NEUTRAL |
| 2020-08 | +3.6 | 0/3 | Weakening | 62% | +2.8 | NEUTRAL |
| 2020-09 | -0.6 | 3/3 | Lagging | 54% | -2.2 | NEUTRAL |
| 2020-10 | -1.9 | 1/3 | Leading | 31% | -1.2 | NEUTRAL |
| 2020-11 | +4.2 | 0/3 | Leading | 62% | +5.8 | RISK-ON |
| 2020-12 | -2.2 | 1/3 | Leading | 31% | -0.8 | NEUTRAL |
| 2021-01 | -0.8 | 3/3 | Weakening | 54% | -3.2 | NEUTRAL |
| 2021-02 | -0.3 | 1/3 | Weakening | 38% | -0.5 | NEUTRAL |
| 2021-03 | +1.1 | 3/3 | Weakening | 62% | -1.8 | NEUTRAL |
| 2021-04 | -0.6 | 3/3 | Lagging | 69% | -1.5 | NEUTRAL |
| 2021-05 | -0.8 | 3/3 | Lagging | 62% | -2.2 | NEUTRAL |
| 2021-06 | +1.1 | 2/3 | Lagging | 62% | -1.2 | NEUTRAL |
| 2021-07 | -4.4 | 3/3 | Leading | 31% | -3.5 | RISK-OFF |
| 2021-08 | +2.2 | 0/3 | Leading | 46% | +3.5 | RISK-ON |
| 2021-09 | +0.0 | 1/3 | Lagging | 46% | +0.5 | NEUTRAL |
| 2021-10 | -1.4 | 0/3 | Leading | 23% | +1.0 | NEUTRAL |
| 2021-11 << BTC 2021 ATH | -4.7 | 3/3 | Lagging | 38% | -5.5 | RISK-OFF |
| 2021-12 | +4.4 | 1/3 | Lagging | 77% | +3.0 | NEUTRAL |
| 2022-01 | -1.9 | 3/3 | Lagging | 54% | -1.5 | NEUTRAL |
| 2022-02 << Russia-Ukraine | -0.8 | 1/3 | Improving | 38% | -1.0 | NEUTRAL |
| 2022-03 | +3.1 | 1/3 | Leading | 62% | +4.2 | RISK-ON |
| 2022-04 | -3.1 | 3/3 | Lagging | 38% | -4.8 | RISK-OFF |
| 2022-05 << Luna/UST Collapse | +5.6 | 1/3 | Lagging | 77% | +3.2 | NEUTRAL |
| 2022-06 | -3.1 | 3/3 | Lagging | 46% | -4.0 | RISK-OFF |
| 2022-07 | +3.6 | 1/3 | Leading | 62% | +2.8 | NEUTRAL |
| 2022-08 | +0.8 | 1/3 | Lagging | 54% | +0.5 | NEUTRAL |
| 2022-09 | -4.7 | 2/3 | Leading | 23% | -3.2 | NEUTRAL |
| 2022-10 | +5.3 | 0/3 | Leading | 69% | +7.5 | RISK-ON |
| 2022-11 << FTX Collapse | +0.0 | 1/3 | Lagging | 46% | +0.5 | NEUTRAL |
| 2022-12 | -4.4 | 3/3 | Leading | 38% | -3.5 | RISK-OFF |
| 2023-01 | +2.5 | 1/3 | Leading | 54% | +3.5 | RISK-ON |
| 2023-02 | +1.4 | 2/3 | Leading | 62% | +2.2 | RISK-ON |
| 2023-03 << SVB Banking Crisis | -2.2 | 2/3 | Leading | 46% | -2.5 | NEUTRAL |
| 2023-04 | -0.6 | 2/3 | Leading | 54% | +0.0 | NEUTRAL |
| 2023-05 | +0.3 | 2/3 | Lagging | 62% | -0.5 | NEUTRAL |
| 2023-06 | +5.3 | 0/3 | Weakening | 62% | +5.2 | RISK-ON |
| 2023-07 | +2.8 | 0/3 | Lagging | 54% | +3.0 | RISK-ON |
| 2023-08 | -4.2 | 3/3 | Lagging | 38% | -5.5 | RISK-OFF |
| 2023-09 | +0.8 | 1/3 | Leading | 54% | +1.8 | NEUTRAL |
| 2023-10 | -6.9 | 1/3 | Leading | 8% | -3.2 | NEUTRAL |
| 2023-11 | +1.1 | 1/3 | Weakening | 54% | +0.2 | NEUTRAL |
| 2023-12 | +4.2 | 1/3 | Leading | 69% | +5.0 | RISK-ON |
| 2024-01 | +2.5 | 1/3 | Weakening | 62% | +1.2 | RISK-ON |
| 2024-02 | +1.9 | 0/3 | Leading | 46% | +1.8 | RISK-ON |
| 2024-03 << BTC ETF $73K | -2.2 | 1/3 | Weakening | 31% | -3.8 | RISK-OFF |
| 2024-04 | -2.5 | 2/3 | Lagging | 46% | -4.5 | RISK-OFF |
| 2024-05 | -1.7 | 1/3 | Weakening | 31% | -1.2 | RISK-OFF |
| 2024-06 | +1.9 | 2/3 | Lagging | 69% | +1.0 | NEUTRAL |
| 2024-07 | -1.3 | 2/3 | Weakening | 43% | -1.5 | NEUTRAL |
| 2024-08 | +3.7 | 1/3 | Lagging | 64% | +0.8 | NEUTRAL |
| 2024-09 | +0.0 | 0/3 | Leading | 36% | +2.5 | NEUTRAL |
| 2024-10 | -2.9 | 2/3 | Leading | 36% | -2.5 | NEUTRAL |
| 2024-11 | +0.5 | 0/3 | Leading | 36% | +2.5 | NEUTRAL |
| 2024-12 | -0.5 | 2/3 | Lagging | 50% | -0.5 | NEUTRAL |
| 2025-01 | +1.2 | 1/3 | Leading | 60% | +1.8 | NEUTRAL |
| 2025-02 | -0.2 | 3/3 | Lagging | 67% | -1.5 | NEUTRAL |
| 2025-03 << Trump Tariff 2025 | -2.0 | 2/3 | Lagging | 47% | -3.8 | RISK-OFF |
| 2025-04 | +1.8 | 1/3 | Leading | 60% | +2.5 | NEUTRAL |
| 2025-05 | +2.8 | 0/3 | Leading | 53% | +5.8 | RISK-ON |
| 2025-06 | +2.2 | 0/3 | Lagging | 53% | +2.2 | RISK-ON |
| 2025-07 | -1.8 | 1/3 | Leading | 27% | -1.2 | NEUTRAL |
| 2025-08 | -1.8 | 2/3 | Lagging | 47% | -3.5 | RISK-OFF |
| 2025-09 | -2.2 | 3/3 | Lagging | 40% | -4.0 | RISK-OFF |
| 2025-10 << Oct 2025 Mega Liq | -4.0 | 3/3 | Leading | 40% | -2.8 | RISK-OFF |

---
## Improvement Summary: Baseline vs Best

| Metric | Baseline (raw +/-3) | Best Composite | Improvement |
|--------|--------------------|--------------------|-------------|
| Regime changes | 85 | 72 | **15% fewer** |
| Whipsaws | 32 | 16 | **50% fewer** |
| RISK-OFF precision | 43% | 57% | **+14pp** |
| Crash recall | 69% | 85% | **+15pp** |
| 1-mo RISK-OFF flashes | 20 | 14 | **30% fewer** |
| Avg RISK-OFF duration | 1.2mo | 1.6mo | **+0.4mo** |
