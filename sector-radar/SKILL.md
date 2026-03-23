# sector-radar

**Stage:** 找标的 (Idea Generation)

## Description

Sector rotation and industry cycle scanner. Analyzes major sector ETFs to identify which industries are in an upswing or undervalued, helping allocate capital to the right sectors at the right time.

## Tracked Sectors

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

## Inputs

- `etfs` — List of sector ETF tickers (default: all 10 SPDR sector ETFs)
- `lookback_days` — Performance lookback window in days (default: 30)

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
# Run full sector scan (default: all 10 sectors)
python3 scripts/fetch_data.py

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
- Bullish: Score > 65 AND P/E below historical median
- Bearish: Score < 35 OR P/E > 25
- Neutral: Everything else
