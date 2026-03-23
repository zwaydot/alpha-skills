# competitive-dynamics

**Stage:** 深度研究 (Deep Research)

## Description

Competitive landscape analysis tool. Compares a target company against its peers across revenue growth, margin trends, and key financial ratios over 3 years. Reveals who is gaining share, who is losing ground, and where the competitive dynamics are shifting.

## Name

Competitive Dynamics Analysis

## Inputs

- `ticker` — Target company ticker symbol
- `peers` — Comma-separated list of competitor tickers (e.g., `MSFT,GOOGL,META`)
- `years` — Historical lookback in years (default: 3)

## Outputs

JSON report containing:
- `target` — Target company analysis
- `peers` — Peer company analyses
- `comparison` — Side-by-side metric comparison
- `competitive_position` — Relative ranking for each metric
- `share_dynamics` — Who is gaining/losing revenue share
- `margin_leaders` — Top performers by gross and net margin
- `analysis_date` — Date of analysis

## Comparison Metrics

| Metric | Description |
|--------|-------------|
| Revenue Growth (3Y CAGR) | Compound annual growth rate of revenue |
| Gross Margin Trend | 3-year direction and average level |
| Net Margin Trend | 3-year direction and average level |
| Operating Leverage | Change in operating margin vs. revenue growth |
| R&D Intensity | R&D as % of revenue (for tech/pharma) |

## Data Sources

- **yfinance** — `ticker.financials` (annual income statements)
- 3-year annual revenue, gross profit, net income, R&D expense

## Script Usage

```bash
# Compare NVDA against its peers
python3 scripts/fetch_data.py NVDA AMD,INTC,QCOM

# Single peer comparison
python3 scripts/fetch_data.py AAPL MSFT

# Save output
python3 scripts/fetch_data.py NVDA AMD,INTC > nvda_competitive.json
```

## Example Prompts

```
Analyze competitive dynamics for NVDA versus AMD, Intel, and Qualcomm
```

```
Compare Apple's revenue growth and margin trends against Microsoft and Google over 3 years
```

```
Who is gaining market share in cloud computing? Compare AMZN, MSFT, and GOOGL
```

## Interpretation Guide

**Revenue CAGR**: Higher is better. Companies growing faster than peers are likely gaining share.

**Gross Margin Trend**: Expanding margins suggest pricing power or scale advantages. Contracting margins may signal competition or cost pressure.

**Competitive Position**: Ranked 1st–Nth among the peer group for each metric. Overall position is the average rank.
