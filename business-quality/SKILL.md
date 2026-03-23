# business-quality

**Stage:** 深度研究 (Deep Research)

## Description

Moat assessment and business quality scorecard. Evaluates a company's competitive advantages by analyzing multi-year trends in profitability metrics. Outputs a structured scorecard rating the durability and quality of the business model.

## Name

Business Quality Assessment

## Inputs

- `ticker` — Single stock ticker symbol (e.g., `AAPL`)
- `years` — Historical lookback in years (default: 5)

## Outputs

JSON scorecard containing:
- `ticker` — Stock symbol
- `company_name` — Company full name
- `metrics` — 5-year historical values for ROE, ROIC, gross margin, net margin
- `trends` — Direction and CAGR for each metric
- `quality_score` — Composite score 0–100
- `moat_rating` — Wide / Narrow / None
- `assessment_date` — Date of analysis

## Scoring Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| ROE Level | 20% | >20% = excellent, >15% = good |
| ROE Stability | 15% | Low variance over 5 years |
| ROIC Level | 20% | >15% = excellent, >10% = good |
| Gross Margin | 20% | >50% = excellent (asset-light), >30% = good |
| Net Margin | 15% | >15% = excellent, >10% = good |
| Margin Trend | 10% | Expanding vs. contracting |

## Moat Rating Logic

- **Wide Moat**: Quality score ≥ 75 AND ROE > 20% for 4+ of 5 years
- **Narrow Moat**: Quality score 50–74 OR ROE consistently 15–20%
- **No Moat**: Quality score < 50

## Data Sources

- **yfinance** — `ticker.financials`, `ticker.balance_sheet`, `ticker.info`
- ROIC calculated as: NOPAT / Invested Capital
- 5-year annual data via `ticker.financials` (annual statements)

## Script Usage

```bash
# Assess a single company
python3 scripts/fetch_data.py AAPL

# Multiple tickers
python3 scripts/fetch_data.py AAPL MSFT GOOGL

# Save JSON output
python3 scripts/fetch_data.py AAPL > aapl_quality.json
```

Output printed as formatted JSON to stdout.

## Example Prompts

```
Assess the business quality and moat for Apple — is it a wide-moat company?
```

```
Compare business quality scores for AAPL, MSFT, and GOOGL
```

```
Analyze the profitability trend for NVDA over the past 5 years and rate its competitive moat
```

## Interpretation Guide

| Score Range | Rating | Interpretation |
|-------------|--------|----------------|
| 80–100 | Exceptional | Wide moat, pricing power, high barriers |
| 60–79 | Strong | Durable competitive advantages |
| 40–59 | Average | Some advantages, but competition present |
| 20–39 | Weak | Commoditized, margin pressure |
| 0–19 | Poor | No visible moat |
