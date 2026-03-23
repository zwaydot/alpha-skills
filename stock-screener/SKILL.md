---
name: Stock Screener
description: Multi-factor stock screening across any universe — S&P 500, Nasdaq 100, sector ETFs, or custom ticker lists. Filters by valuation, profitability, and growth to surface investment candidates.
---

# Stock Screener

Multi-factor screening to find stocks that meet quality and value criteria. Supports any universe — not limited to S&P 500.

## Inputs

- **Universe** (choose one):
  - Index: `sp500` / `nasdaq100` / `russell2000`
  - Sector ETF: `XLK`, `XLF`, `XLE`, `XLV`, `XLI`, `XLY`, `XLP`, `XLB`, `XLRE`, `XLU`
  - Custom list: any set of tickers
- **Filters** (optional, with defaults):
  - Max P/E ratio (default: 20)
  - Min ROE % (default: 15%)
  - Min market cap in $B (default: $1B)

## Outputs

- CSV with: ticker, company name, sector, price, market cap, P/E, ROE, revenue growth, score
- Top candidates ranked by composite score

## Data Sources

- `yfinance` — real-time fundamentals, no API key required
- Wikipedia — S&P 500 / Nasdaq 100 constituent lists

## Script Usage

```bash
# S&P 500 (default)
python3 scripts/fetch_data.py

# Nasdaq 100
python3 scripts/fetch_data.py --index nasdaq100

# Tech sector only
python3 scripts/fetch_data.py --sector XLK

# Custom ticker list
python3 scripts/fetch_data.py --tickers AAPL MSFT NVDA GOOGL META AMZN

# Looser filters (higher P/E, lower ROE)
python3 scripts/fetch_data.py --index sp500 --pe 30 --roe 10 --mcap 5

# Save to specific file
python3 scripts/fetch_data.py --output my_candidates.csv
```

## Example Prompts

```
Run the stock screener on the Nasdaq 100 and show me the top quality candidates
```

```
Screen the tech sector (XLK) for stocks with P/E under 25 and ROE above 20%
```

```
Evaluate these 10 stocks against my quality criteria: AAPL MSFT NVDA TSLA META AMZN GOOGL V MA JPM
```
