---
name: Portfolio Monitor
description: Portfolio analytics — computes weighted returns, correlation matrix, volatility contributions, Sharpe ratio, and concentration risk (HHI) for a set of weighted holdings. Use this when the user wants to analyze their portfolio, check diversification, understand risk attribution, or evaluate position correlations.
---

# portfolio-monitor

**Stage:** Portfolio Management

## Inputs

- `portfolio` — Space-separated `TICKER:WEIGHT` pairs (e.g., `AAPL:30 MSFT:20 NVDA:50` or `0700.HK:30 9988.HK:20 1810.HK:50`)
- Weights can be percentages (must sum to ~100) or absolute values (auto-normalized)
- Supports mixed US/HK portfolios. Risk-free rate auto-detected from portfolio's primary market.

## Outputs

JSON portfolio analysis containing:
- `holdings` — Individual stock data with current prices and performance
- `portfolio_metrics` — Weighted return, volatility, Sharpe ratio estimate
- `correlation_matrix` — Pairwise correlations between holdings
- `volatility_contributions` — Each position's contribution to portfolio risk
- `concentration_risk` — HHI index and top-5 weight analysis
- `analysis_date` — Date of analysis

## Analytics

| Metric | Description |
|--------|-------------|
| Weighted Return (1M/3M/1Y) | Portfolio-level return by period |
| Portfolio Volatility | Annualized standard deviation |
| Correlation Matrix | Pairwise 1-year daily return correlations |
| Volatility Contribution | Each position's % contribution to total variance |
| HHI Concentration | Herfindahl–Hirschman Index (>2500 = concentrated) |

## Data Sources

- **yfinance** — Daily price history for correlation and volatility
- **yfinance** — `ticker.info` for current prices and fundamentals

## Script Usage

```bash
# Analyze a portfolio
python3 scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:50"

# Equal-weight portfolio
python3 scripts/fetch_data.py "AAPL:25 MSFT:25 GOOGL:25 AMZN:25"

# Save output
python3 scripts/fetch_data.py "AAPL:40 NVDA:30 MSFT:30" > portfolio.json
```

## Example Prompts

```
Monitor my portfolio: AAPL:30 MSFT:20 NVDA:50 — what's my concentration risk?
```

```
Calculate the correlation matrix and volatility contribution for AAPL:25 MSFT:25 GOOGL:25 AMZN:25
```

```
Is my tech-heavy portfolio (AAPL:40 NVDA:30 MSFT:30) well-diversified?
```

## Diversification Guidance

| Correlation | Interpretation |
|-------------|----------------|
| > 0.8 | High — minimal diversification benefit |
| 0.5 – 0.8 | Moderate — some diversification |
| < 0.5 | Low — good diversification |

**HHI Guide:**
- HHI < 1500: Well-diversified
- HHI 1500–2500: Moderately concentrated
- HHI > 2500: Highly concentrated — consider rebalancing
