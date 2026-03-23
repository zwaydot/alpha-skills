# stock-screener

**Stage:** 找标的 (Idea Generation)

## Description

Multi-factor quantitative screener to find candidate stocks that meet buy-side quality thresholds. Filters the market for companies with attractive valuations, strong profitability, and growth momentum.

## Default Screening Criteria

| Factor | Threshold |
|--------|-----------|
| P/E Ratio | < 20 |
| ROE | > 15% |
| Revenue Growth (YoY) | > 10% |
| Market Cap | > $1B |

## Inputs

- `tickers` — List of ticker symbols to screen (or use a predefined universe)
- `pe_max` — Maximum P/E ratio (default: 20)
- `roe_min` — Minimum ROE % (default: 15)
- `revenue_growth_min` — Minimum revenue growth % (default: 10)
- `market_cap_min` — Minimum market cap in USD billions (default: 1)

## Outputs

CSV file containing:
- `ticker` — Stock symbol
- `name` — Company name
- `market_cap` — Market capitalization (USD)
- `pe_ratio` — Trailing P/E ratio
- `roe` — Return on equity (%)
- `revenue_growth` — YoY revenue growth (%)
- `score` — Composite score (0–100)

## Data Sources

- **yfinance** — Real-time and historical financial data
- Financials pulled from `ticker.info`, `ticker.financials`, `ticker.balance_sheet`

## Script Usage

```bash
# Screen a custom list of tickers
python3 scripts/fetch_data.py AAPL MSFT GOOGL NVDA META TSLA AMZN

# Use default S&P 100 universe (no args)
python3 scripts/fetch_data.py

# Override thresholds via env vars
PE_MAX=15 ROE_MIN=20 python3 scripts/fetch_data.py AAPL MSFT NVDA
```

Output saved to `screener_results.csv` in the current directory.

## Example Prompts

```
Run the stock screener on the top 50 S&P 500 names and show me candidates with P/E under 20 and ROE above 15%
```

```
Screen these tickers for quality: AAPL, MSFT, GOOGL, NVDA, META, TSLA, AMZN, JPM, V, MA
```

```
Find undervalued large-cap tech stocks with strong ROE and revenue growth
```

## Scoring Logic

The composite score weights:
- **Valuation (30%)** — Lower P/E = higher score
- **Profitability (40%)** — Higher ROE = higher score
- **Growth (30%)** — Higher revenue growth = higher score

Scores normalized 0–100. Stocks passing all filters sorted by score descending.
