# risk-framework

**Stage:** 风险管理 (Risk Management)

## Description

Systematic risk scoring framework. Evaluates a company across market risk, financial risk, and liquidity risk dimensions. Outputs a structured risk scorecard to help position sizing and portfolio risk management decisions.

## Name

Risk Framework

## Inputs

- `ticker` — Single stock ticker symbol (e.g., `AAPL`)

## Outputs

JSON risk scorecard containing:
- `ticker` — Stock symbol
- `risk_score` — Overall risk score 0–100 (lower = safer)
- `risk_level` — Low / Medium / High / Very High
- `dimensions` — Individual scores for each risk dimension
- `raw_metrics` — Beta, volatility, leverage ratios, liquidity ratios
- `key_risks` — Top 3 risk factors identified
- `assessment_date` — Date of analysis

## Risk Dimensions

| Dimension | Weight | Key Metrics |
|-----------|--------|-------------|
| Market Risk | 30% | Beta, 52-week volatility, drawdown |
| Financial Leverage Risk | 30% | Debt/Equity, Interest Coverage, Debt/EBITDA |
| Liquidity Risk | 20% | Current Ratio, Quick Ratio, Cash Ratio |
| Earnings Quality Risk | 20% | Accruals ratio, FCF/Net Income |

## Risk Scoring

- **0–25**: Low Risk — Strong financials, low volatility
- **26–50**: Medium Risk — Moderate risk profile, monitor closely
- **51–75**: High Risk — Elevated leverage or volatility
- **76–100**: Very High Risk — Significant financial stress signals

## Data Sources

- **yfinance** — `ticker.info` for beta, market data
- **yfinance** — `ticker.balance_sheet` for leverage and liquidity ratios
- **yfinance** — `ticker.history()` for realized volatility calculation

## Script Usage

```bash
# Risk assessment for a single ticker
python3 scripts/fetch_data.py AAPL

# Multiple tickers for comparison
python3 scripts/fetch_data.py AAPL TSLA AMZN

# Save output
python3 scripts/fetch_data.py NVDA > nvda_risk.json
```

## Example Prompts

```
Assess the risk profile for Tesla — what are the key risks?
```

```
Compare risk scores for AAPL, TSLA, and AMZN
```

```
Is NVDA's financial leverage a concern? Run a risk assessment.
```

## Position Sizing Guidance

| Risk Level | Suggested Max Position Size |
|------------|----------------------------|
| Low (0–25) | Up to 10% of portfolio |
| Medium (26–50) | Up to 7% of portfolio |
| High (51–75) | Up to 4% of portfolio |
| Very High (76–100) | Up to 2% of portfolio |

> ⚠️ Position sizing guidance is illustrative. Adjust based on your portfolio's overall risk tolerance.
