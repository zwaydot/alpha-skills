---
name: sector-radar
description: Sector/ETF/fund momentum scanner for industry allocation and fund configuration. Compares any set of sector ETFs, thematic ETFs, country ETFs, or income ETFs by momentum, trend acceleration, relative valuation, and volume trend. Use this (NOT stock-screener) when the user wants to compare sectors or industries, select ETFs or funds, make sector allocation decisions, do portfolio rebalancing across sectors, compare thematic/geographic/income fund options, or identify sector rotation opportunities. Triggers for "which sector", "sector rotation", "ETF comparison", "fund allocation", "which industries are hot", "sector rebalance", "defensive vs cyclical", "overweight/underweight sectors". Do NOT use for screening individual stocks — that is stock-screener's job.
---

# sector-radar

**What it does:** Scans and ranks sector ETFs, thematic ETFs, country ETFs, or any ETF set by momentum and trend quality. Answers "which sectors/funds should I overweight?" — the step before stock-screener's "which stocks within that sector?"

**Who it's for:** Fund managers doing sector rebalancing, investors choosing between thematic ETFs, anyone making top-down industry or geographic allocation decisions.

## Scoring Model (0-100)

Four quantitative dimensions, all computed from ETF price/volume data:

| Dimension | Weight | Method | Why it matters |
|-----------|--------|--------|----------------|
| Momentum | 50% | Weighted returns: 3M 35% + 6M 35% + 12M 30% | Core rotation signal — Jegadeesh & Titman (1993), Moskowitz & Grinblatt (1999) sector momentum |
| Acceleration | 15% | 3M annualized vs 6M annualized return gap | Distinguishes accelerating trends from decelerating ones — positive = gaining strength |
| Relative Valuation | 20% | PE rank within result set (lower PE = higher score) | Cross-sector valuation comparison without absolute thresholds — Fama & French (1992) |
| Volume Trend | 15% | 20-day vs 60-day avg volume ratio | Confirms institutional conviction behind price moves |

**Design choices:**
- **Skip 1-month momentum**: Jegadeesh (1990) showed 1-month returns exhibit short-term reversal, not continuation.
- **Acceleration over earnings revision**: ETFs don't expose forward PE from free data sources. Momentum acceleration (3M vs 6M trend) is a pure price signal that separates strengthening from fading trends. For earnings revision context, use your own knowledge of sector earnings trends — see "After Running the Script" below.
- **Relative valuation**: PE 25 is cheap for tech but expensive for utilities. Ranking within the scanned set avoids sector-specific thresholds.

## Script Usage

```bash
# US SPDR sector ETFs vs S&P 500
python3 scripts/fetch_data.py XLK XLF XLE XLV XLI XLY XLP XLB XLRE XLU XLC --benchmark SPY

# With custom sector labels
python3 scripts/fetch_data.py XLK XLF XLE --labels Technology Financials Energy --benchmark SPY

# HK market sectors vs Tracker Fund
python3 scripts/fetch_data.py 3067.HK 3033.HK 3012.HK 2800.HK 2828.HK 3040.HK --benchmark 2800.HK

# Thematic ETFs
python3 scripts/fetch_data.py BOTZ ICLN HACK ARKK --benchmark QQQ

# Global market comparison
python3 scripts/fetch_data.py EWJ EWG EWU EWA FXI --benchmark SPY --labels Japan Germany UK Australia China
```

### Parameters

| Param | Required | Description |
|-------|----------|-------------|
| `etfs` | Yes | ETF tickers to scan (positional, space-separated) |
| `--benchmark` | No | Benchmark ticker for relative strength (e.g., SPY, QQQ, 2800.HK) |
| `--labels` | No | Sector labels matching ETFs order; defaults to ETF short name from Yahoo |

### Output

Markdown report with:
- **Sector Rankings** — sorted by composite score with returns, acceleration, PE, relative strength, volume trend
- **Momentum Leaders / Laggards** — with acceleration annotation
- **Momentum × Trend Quality Quadrant** — four-quadrant classification for allocation decisions
- CSV data on stderr for programmatic use

## Choosing ETFs for the User

**Principle**: Use broad sector ETFs for general rotation scans, thematic ETFs for specific themes, and country ETFs for geographic comparison. Always include a benchmark for relative strength context.

**Patterns**:
- **"US sector rotation"** → 11 SPDR sector ETFs (XLK XLF XLE XLV XLI XLY XLP XLB XLRE XLU XLC) + `--benchmark SPY`
- **"HK sector scan"** → HK sector ETFs (3067.HK, 3033.HK, 3012.HK, 2828.HK, 3040.HK) + `--benchmark 2800.HK`
- **"which tech sub-industries"** → Sub-sector ETFs like SMH, IGV, HACK, SKYY, BOTZ + `--benchmark XLK`
- **"global markets comparison"** → Country ETFs like EWJ, FXI, EWG, EWU, EWZ + `--benchmark SPY`

Use your knowledge of available ETFs — don't limit yourself to these examples.

## After Running the Script

The script outputs quantitative price/volume data. Your job is to layer on the qualitative analysis that makes it actionable for allocation decisions. Follow this framework:

### 1. Trend Quality Quadrant (lead with this)

The script outputs a four-quadrant classification. This is the core decision framework:

| Quadrant | Momentum | Acceleration | Signal | Action |
|----------|----------|-------------|--------|--------|
| **Strong + accelerating** | High | Positive | Trend gaining strength | Overweight — highest conviction rotation target |
| **Strong + decelerating** | High | Negative | Trend may be peaking | Take partial profits or tighten stops |
| **Weak + accelerating** | Low | Positive | Early signs of reversal | Potential contrarian entry — watch for confirmation |
| **Weak + decelerating** | Low | Negative | Deteriorating across timeframes | Underweight or avoid |

### 2. Macro & Catalyst Context (the "why" behind the numbers)

The script tells you what's happening (which sectors are strong/weak). Your job is to explain why — this is where buy-side analysts add the most value. Use your own knowledge first; only search the web if you genuinely lack context on a specific event or sector (e.g., an unfamiliar regional market). For mainstream US/HK/global sectors, your training data already covers the macro backdrop, sector catalysts, and competitive dynamics well enough. Avoiding unnecessary web searches keeps response time under 2 minutes.

- **Macro drivers**: What's currently driving sector rotation? Interest rate cycle, geopolitical events, fiscal policy, earnings cycle stage. Be specific — "Fed held at 3.5-3.75% with hawkish dot plot" is useful, "rates are high" is not.
- **Sector catalysts**: For each top/bottom-ranked sector, identify the specific catalyst or headwind explaining the signal. E.g., Energy momentum from Middle East supply disruption, Tech weakness from AI capex ROI skepticism.
- **Signal vs narrative alignment**: Where the quantitative signal confirms the consensus narrative, conviction is higher. Where they diverge (e.g., strong momentum in a sector everyone is bearish on), flag it — that's either a contrarian opportunity or a trap.

This context transforms raw momentum data into an investment thesis. Without it, the analysis is just a sorted table.

### 3. Relative Strength & Volume Confirmation

- Frame returns relative to benchmark when provided. A sector returning +5% while the benchmark returned +8% is underperforming — the RS 6M column shows this directly.
- Volume confirms or contradicts price signals:
  - Strong momentum + rising volume (>1.1) = **confirmed institutional buying**
  - Strong momentum + fading volume (<0.9) = **trend exhaustion — be cautious**
  - Weak momentum + rising volume = **distribution — institutional selling**

### 4. Allocation Recommendations

Be specific and layered:
- **Tactical (3-6 months)**: Based on momentum quadrant + macro catalysts. "Overweight Energy, underweight Tech" with the specific catalyst driving each call.
- **Structural (12+ months)**: Based on valuation rank + macro backdrop. Low-momentum sectors with cheap valuations and positive earnings revision are the strongest structural candidates.
- **Risk flags**: Note sector concentration, valuation extremes, momentum-volume divergences, or macro scenarios that would invalidate the thesis.

### 5. Connect to Next Steps

- Suggest `stock-screener` to find specific stocks within top-ranked sectors
- Suggest `business-quality` for moat analysis on sector leaders
- For geographic comparisons, note currency, macro, and policy risk factors
