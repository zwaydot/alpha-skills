---
name: Sector Radar
description: Sector rotation and industry cycle scanner. Ranks 10 SPDR sector ETFs by momentum, valuation, and relative strength to identify which industries are in an upswing or undervalued. Use this when the user asks about sector rotation, industry momentum, which sectors are hot/cold, or wants to compare sectors.
---

# sector-radar

**Stage:** Idea Generation

## Tracked Sectors

### US (default)
| ETF | Sector |
|-----|--------|
| XLK | Technology |
| XLF | Financials |
| XLE | Energy |
| XLV | Healthcare |
| XLI | Industrials |
| XLY | Consumer Discretionary |
| XLP | Consumer Staples |
| XLB | Materials |
| XLRE | Real Estate |
| XLU | Utilities |

### HK (Hong Kong)
| ETF | Sector |
|-----|--------|
| 3067.HK | HK Tech (HSTECH ETF) |
| 3033.HK | HK Financials |
| 3012.HK | HK Property |
| 2800.HK | HK Broad Market (Tracker Fund) |
| 2828.HK | China A-share ETF |
| 3040.HK | HK Consumer |

## Inputs

- `etfs` — List of sector ETF tickers (default: all 10 US SPDR sector ETFs)
- `--market` — Market to scan: `US` (default) or `HK`

## Outputs

Markdown report containing:
- **Sector Ranking Table** — sorted by momentum score
- **Valuation Summary** — P/E ratio by sector
- **Momentum Signals** — 1M / 3M / 6M / 1Y price performance
- **Cycle Assessment** — bullish / neutral / bearish rating per sector
- **Top Pick** — highest-conviction sector call

## Data Sources

- **yfinance** — ETF price data, valuation info, volume trends
- `ticker.history()` for price momentum
- `ticker.info` for P/E and yield

## Script Usage

```bash
# Run full US sector scan (default: all 10 sectors)
python3 scripts/fetch_data.py

# Hong Kong market sectors
python3 scripts/fetch_data.py --market HK

# Custom ETF list
python3 scripts/fetch_data.py XLK XLF XLE XLV

# Save output to file
python3 scripts/fetch_data.py > sector_report.md
```

## Example Prompts

```
Scan all sectors and tell me which ones have the best momentum and lowest valuation right now
```

```
Which sectors are in an upswing cycle? I want to rotate into defensive names.
```

```
Show me a sector heat map with momentum and valuation for the past month
```

## Methodology

**Momentum Score (0–100):**
- 1M return: 40% weight
- 3M return: 35% weight
- 6M return: 25% weight

**Cycle Assessment:**
- Bullish: Score > 65 AND P/E < 22
- Bearish: Score < 35 OR P/E > 28
- Neutral: Everything else
