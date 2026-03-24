---
name: portfolio-monitor
description: Portfolio diagnostics — sector exposure, risk decomposition, benchmark comparison, correlation, and concentration analysis for weighted holdings. Use this when the user wants to analyze their portfolio, check diversification, understand risk attribution, compare against a benchmark, or evaluate position sizing.
---

# portfolio-monitor

Portfolio diagnostics grounded in Modern Portfolio Theory (Markowitz, 1952). The core insight: portfolio risk is not the weighted average of individual risks — it depends on how holdings move together. This skill quantifies that through covariance-based risk decomposition, benchmark-relative performance, and concentration analysis.

## Methodology

### Risk Decomposition (Marginal Contribution to Variance)

Each holding's volatility contribution comes from the covariance matrix, not just its own volatility:

```
contribution_i = w_i × (Σ w_j × cov_ij) / portfolio_variance
```

A stock can have 30% weight but contribute 50% of portfolio risk if it's volatile and highly correlated with other holdings. The **Over/Under** column flags this mismatch — positive means the position contributes more risk than its weight suggests.

### Benchmark Comparison

Auto-selects benchmark by portfolio market: SPY (US), 2800.HK (HK), 510300.SS (CN). Computes:
- Return, volatility, Sharpe, max drawdown — side by side with delta
- Portfolio–benchmark correlation — how much the portfolio tracks the index

### Concentration (HHI)

Herfindahl–Hirschman Index at both holding and sector level:
- HHI < 1500: diversified
- 1500–2500: moderate
- &gt; 2500: concentrated

A portfolio can have low holding HHI but high sector HHI (e.g., 10 tech stocks equally weighted).

### Max Drawdown

Peak-to-trough decline from 1-year daily cumulative returns. Captures tail risk that volatility misses.

## Script Usage

```bash
python3 scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:50"
python3 scripts/fetch_data.py "AAPL:25 MSFT:25 JPM:25 XOM:25"
python3 scripts/fetch_data.py "0700.HK:40 9988.HK:30 1810.HK:30"
```

Weights auto-normalize. Supports US, HK, CN, JP, UK tickers. Mixed-market portfolios use the majority market's benchmark and risk-free rate.

## Output Schema

Markdown report (stdout) with: Holdings table, Performance vs Benchmark, Sector Exposure with visual bars, Risk Decomposition, Correlation Matrix, Concentration metrics.

JSON (stderr) with all raw data for programmatic use.

## After Running the Script

The script provides data. Your analysis should address:

1. **Risk budget assessment** — Compare each holding's weight vs volatility contribution. Flag positions where risk contribution exceeds weight by >5pp — these are risk-dominant positions. Example: "NVDA is 50% of your portfolio but drives 66.5% of risk due to its 45% annualized vol and moderate correlation with AAPL (0.49)."

2. **Benchmark-relative diagnosis** — Is the portfolio taking more risk (higher vol) for adequate return? Compare Sharpe ratios. A portfolio with higher return but lower Sharpe than its benchmark is achieving returns through risk, not skill. Example: "Your portfolio returned +29% vs SPY's +17%, but Sharpe (0.52 vs 0.38) shows only modest risk-adjusted outperformance."

3. **Diversification quality** — Look at correlation matrix and sector exposure together. High pairwise correlations (>0.7) within the same sector compound concentration risk. Low correlations across sectors indicate genuine diversification. Example: "MSFT–XOM correlation of 0.09 means energy provides real diversification for your tech-heavy portfolio."

4. **Drawdown context** — Max drawdown is the lived experience of the portfolio. A -24% drawdown means the investor saw a quarter of their capital vanish at some point. Compare to benchmark drawdown. Example: "Your -24% drawdown vs SPY's -16% means you experienced 50% worse pain during the selloff."

5. **Actionable suggestions** — Based on the diagnostics, suggest specific improvements. If sector HHI is high, name specific sectors that could reduce risk. If one position dominates risk, quantify what trimming it would do. If drawdown is severe, note what caused it. Recommend `business-quality` for deep-diving into risk-dominant positions, or `valuation-matrix` if considering rebalancing. For HK portfolios, recommend HK-listed alternatives (e.g., REITs, utilities, financials); for US portfolios, suggest missing GICS sectors.

## Interpreting Different Portfolio Types

Tailor your diagnosis to the portfolio's character:

- **Concentrated growth** (3-5 tech/growth names): The main risk is sector concentration and single-name dominance. Focus on which position drives disproportionate risk and what happens when the sector rotates. A negative Sharpe ratio here means the growth bet is actively losing to cash.
- **Balanced multi-sector** (6-15 names across sectors): Focus on whether the diversification is genuine (low cross-sector correlations) or illusory (many names, same factor exposure). Check if equal weights produce unequal risk contributions.
- **Income/defensive** (utilities, staples, REITs, dividend stocks): Expect lower volatility and smaller drawdowns than benchmark. The key question is whether the portfolio achieves adequate risk-adjusted return (Sharpe) despite lower absolute returns. A Sharpe above the benchmark with lower drawdown is a success for this archetype.
- **Cross-market** (mixed US/HK/CN): Note that the benchmark may not fully represent the portfolio. Currency risk adds a dimension not captured in the correlation matrix. Holdings in different markets may show lower correlations during normal times but can correlate during global risk-off events.
