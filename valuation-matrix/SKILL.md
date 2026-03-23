---
name: valuation-matrix
description: Multi-method valuation framework with sector-aware multiples. Triangulates intrinsic value using FCF yield, EV/EBITDA, P/E (with industry-appropriate ranges), and analyst consensus targets. Use this when the user asks about fair value, intrinsic value, whether a stock is overvalued/undervalued, or wants bear/base/bull price targets.
---

# valuation-matrix

**Stage:** Valuation

## Inputs

- `ticker` — Stock ticker symbol (e.g., `AAPL`, `0700.HK`). Market and sector are auto-detected to select appropriate valuation multiples.

## Outputs

JSON valuation model containing:
- `ticker` — Stock symbol
- `current_price` — Current market price
- `market_cap` — Market capitalization
- `enterprise_value` — EV (market cap + debt - cash)
- `raw_data` — FCF, EBITDA, EPS, analyst targets
- `valuation_methods` — Results from each method
- `valuation_range` — Bear / Base / Bull price targets
- `upside_pct` — % upside from current price to base target
- `recommendation` — Buy / Hold / Sell signal

## Valuation Methods

All multiple ranges are **sector-aware** — the script automatically selects appropriate ranges based on the company's sector (e.g., Technology gets higher P/E ranges than Energy).

| Method | Description |
|--------|-------------|
| FCF Yield | Implied fair value based on sector-appropriate FCF yield range |
| EV/EBITDA | Implied equity value using sector-appropriate EBITDA multiple range |
| P/E Multiple | Implied price using sector-appropriate earnings multiple range |
| Analyst Consensus | Median analyst 12-month price target |

## Valuation Range Logic

- **Bear Case**: Median of all methods' bear-case prices
- **Base Case**: Median of all methods' base-case prices
- **Bull Case**: Median of all methods' bull-case prices

## Data Sources

- **yfinance** — `ticker.info` for current price, EV, market cap, analyst targets
- **yfinance** — `ticker.cashflow` for free cash flow
- **yfinance** — `ticker.financials` for EBITDA and EPS

## Script Usage

```bash
# Valuation analysis for a single ticker
python3 scripts/fetch_data.py AAPL

# Multiple tickers
python3 scripts/fetch_data.py AAPL MSFT GOOGL

# Save output
python3 scripts/fetch_data.py NVDA > nvda_valuation.json
```

## Example Prompts

```
Run a valuation matrix for Apple — what's the fair value range?
```

```
Build a multi-method valuation for NVDA with bear/base/bull scenarios
```

```
Is Microsoft overvalued or undervalued based on FCF yield and EV/EBITDA?
```

## Interpretation Guide

| Upside % | Signal | Action |
|----------|--------|--------|
| > 30% | Deep Value | Strong Buy |
| 15–30% | Undervalued | Buy |
| -15% to 15% | Fairly Valued | Hold |
| -15% to -30% | Overvalued | Reduce |
| < -30% | Significantly Overvalued | Sell |

> ⚠️ Valuation models are estimates based on current data. Always combine with qualitative analysis.
