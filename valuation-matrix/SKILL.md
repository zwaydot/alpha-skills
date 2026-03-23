# valuation-matrix

**Stage:** 估值 (Valuation)

## Description

Multi-method valuation framework. Triangulates intrinsic value using FCF yield, EV/EBITDA, P/E, and analyst consensus price targets. Outputs a structured valuation range with upside/downside scenarios.

## Name

Valuation Matrix

## Inputs

- `ticker` — Single stock ticker symbol (e.g., `AAPL`)

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

| Method | Description |
|--------|-------------|
| FCF Yield | Implied fair value based on 4–6% FCF yield range |
| EV/EBITDA | Implied equity value using 10–18x EBITDA range |
| P/E Multiple | Implied price using 15–25x earnings range |
| Analyst Consensus | Median analyst 12-month price target |

## Valuation Range Logic

- **Bear Case**: 10th percentile of all method outputs
- **Base Case**: Median of all method outputs
- **Bull Case**: 90th percentile of all method outputs

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
