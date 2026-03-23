---
name: stock-screener
description: "Multi-factor stock screening with scored ranking across US, HK, and global markets. Use this skill whenever the user wants to: screen or filter stocks by any criteria (sector, industry, PE, ROE, growth, valuation, profitability), find investment candidates or stock picks, compare multiple stocks on financial metrics, scan a market or index for opportunities, rank stocks by quality or value, or find stocks that are cheap, undervalued, high-growth, or high-quality. Covers any request involving narrowing a universe of stocks down to ranked candidates using quantitative filters. Do NOT use for single-stock deep analysis (DCF, earnings reports), portfolio allocation, trade execution, or price quotes."
---

# Stock Screener

Multi-factor stock screening using a two-phase architecture: server-side filtering narrows the universe, then detail enrichment scores the top candidates with a 5-factor model.

## Two-Phase Architecture

**Phase 1 — Server-side filter** (1 API call):
Query the data provider's screener endpoint with sector, PE, ROE, and market cap constraints. Returns only matching candidates.

**Phase 2 — Detail enrichment** (N calls, N = 25-50):
Fetch full financial profiles for Phase 1 candidates. Re-validate filters (server and detail data can diverge), then score and rank using the 5-factor model.

This avoids scanning thousands of stocks individually. The bundled script uses Yahoo Finance's `EquityQuery` + `screen()` for Phase 1. If the user has a different data source (FMP, Longbridge MCP, Alpaca MCP), apply the same two-phase pattern with that API's screener endpoint.

## Methodology

The scoring model draws on established multi-factor investing research, adapted into a lightweight screening tool.

### Academic and Practitioner Foundations

**Factor selection** is grounded in decades of asset pricing research:

- **Valuation** (PE + EV/EBITDA): The value premium is one of the oldest documented anomalies in finance. Fama & French (1992) established that low price-to-book stocks outperform. We use PE and EV/EBITDA as complementary lenses — PE captures the equity holder's perspective, while EV/EBITDA captures operating value regardless of capital structure (useful for cross-company comparison when leverage differs). This mirrors the Greenblatt Magic Formula's use of earnings yield (EBIT/EV) rather than PE alone.

- **Profitability** (ROE): Novy-Marx (2013) demonstrated that gross profitability is a strong predictor of returns, independent of value. AQR's "Quality Minus Junk" paper (Asness, Frazzini & Pedersen, 2019) uses profitability as one of four quality dimensions. ROE is our proxy — imperfect (leverage can inflate it), but widely available and interpretable. ROIC would be more precise but is not directly available from yfinance.

- **Growth** (revenue + earnings growth): CANSLIM (William O'Neil) emphasizes current quarterly earnings growth of 25%+ as a primary screen. We blend revenue and earnings growth to capture both top-line expansion and margin improvement. Growth is capped at 50% for scoring to prevent outliers from dominating.

- **Momentum** (52-week price return): Jegadeesh & Titman (1993) documented that stocks with strong recent performance continue to outperform over 3-12 month horizons. Carhart (1997) added momentum as the fourth factor to the Fama-French model. MSCI includes momentum as one of its core 6 factor indexes. We use 52-week price change as a simple, robust momentum signal.

- **Safety** (debt/equity + cash flow quality): The Piotroski F-Score dedicates 3 of 9 signals to leverage and liquidity. AQR's quality framework includes "safety" (low beta, low leverage, low earnings volatility) as a core dimension. We combine debt-to-equity (balance sheet risk) with operating cash flow / net income ratio (earnings quality — high ratio means earnings are backed by real cash, not accruals).

### Why Relative Valuation Scoring

Absolute thresholds (e.g., "PE < 20 is cheap") fail across sectors — PE 20 is expensive for utilities but cheap for software. Following the approach used by Schwab Equity Ratings and MSCI factor indexes, we score valuation *relatively within the result set*. Each stock's PE and EV/EBITDA are rank-ordered among peers in the screen output. This means the cheapest stock in any result set gets the highest valuation score, regardless of absolute PE level.

### Why Style Presets

Academic research (MSCI Adaptive Multi-Factor Allocation, 2023) shows that factor performance is regime-dependent — value outperforms in recoveries, momentum in trends, quality in downturns. Full dynamic weight optimization requires ML infrastructure beyond a screening tool's scope. Style presets are a practical middle ground: the user declares intent (value / growth / quality), and weights shift accordingly. This aligns with how institutional multi-factor products (MSCI, FTSE Russell) offer tilted index variants.

### Why Market Cap Is Not a Scoring Factor

The Fama-French size factor (SMB) shows that smaller companies tend to outperform larger ones over long periods. Scoring market cap positively would penalize small caps, contradicting the academic evidence. Market cap is retained as a *filter* (`--mcap`) for investability — screening out micro-caps that may be illiquid — but does not contribute to the composite score.

### Limitations

- **No sector-relative scoring across the full universe**: Valuation is relative within each screen's result set, not across the entire market. A screen limited to one sector gives good relative ranking; a cross-sector screen may compare apples to oranges.
- **ROE as profitability proxy**: ROE is inflated by leverage. A company with 50% ROE and 300% D/E is not necessarily higher quality than one with 20% ROE and 0% D/E. The safety factor partially compensates by penalizing high leverage.
- **Point-in-time snapshot**: All metrics are trailing 12 months. Cyclical businesses may look cheap at peak earnings or expensive at trough earnings.
- **No forward estimates**: The model uses reported data only, not analyst consensus estimates. Forward PE is included in the output for reference but not in scoring.

## 5-Factor Scoring System (0-100)

| Factor | Balanced | Value | Growth | Quality | Metrics |
|--------|----------|-------|--------|---------|---------|
| Valuation | 25% | 40% | 10% | 15% | Composite: PE + EV/EBITDA, relative within result set |
| Profitability | 25% | 20% | 15% | 35% | ROE above threshold |
| Growth | 20% | 10% | 40% | 15% | Revenue growth + earnings growth blend |
| Momentum | 15% | 10% | 25% | 10% | 52-week price change |
| Safety | 15% | 20% | 10% | 25% | Low debt/equity + cash flow quality (OCF/net income) |

### Style Presets (`--style`)

- **balanced** (default): Equal emphasis across all factors. General-purpose screening.
- **value**: Heavy valuation + safety weights. For cyclicals, deep value, dividend stocks.
- **growth**: Heavy growth + momentum weights. For high-growth tech, emerging sectors.
- **quality**: Heavy profitability + safety weights. For defensive compounders, low-volatility picks.

### Key Design Decisions

- **Composite valuation**: PE and EV/EBITDA are scored *relatively within the result set* (rank-based), not against absolute thresholds. This means a PE of 25 scores well in a set of growth stocks but poorly in a set of utilities.
- **Market cap is a filter, not a scoring factor**: Academic research shows small caps tend to outperform (size premium). Market cap is used only as a screening threshold (`--mcap`), not as a quality signal.
- **Missing data handled gracefully**: Banks have no EV/EBITDA; pre-profit companies lack PE. The model uses available metrics and assigns neutral scores for missing ones.

## Script Usage

```bash
# US tech stocks, balanced scoring
python3 scripts/fetch_data.py --sector Technology --pe 25

# Growth-focused screening
python3 scripts/fetch_data.py --sector Technology --pe 40 --style growth

# Value screening for financials
python3 scripts/fetch_data.py --sector "Financial Services" --style value

# Quality compounders in healthcare
python3 scripts/fetch_data.py --sector Healthcare --style quality

# Sub-industry filter
python3 scripts/fetch_data.py --sector Technology --industry Semiconductors

# HK market
python3 scripts/fetch_data.py --region hk --sector Technology

# Custom tickers
python3 scripts/fetch_data.py --tickers AAPL MSFT NVDA TSLA META --pe 40 --roe 10

# Predefined HK index
python3 scripts/fetch_data.py --index hstech

# No financial filters
python3 scripts/fetch_data.py --sector Technology --top 50 --pe 0 --roe 0
```

### Parameters

| Param | Default | Description |
|-------|---------|-------------|
| `--region` | us | Market region (us, hk, gb, jp, etc.) |
| `--sector` | (none) | Sector filter (Technology, Healthcare, etc.) |
| `--industry` | (none) | Sub-industry filter, partial match |
| `--pe` | 20 | Max P/E; 0 to disable |
| `--roe` | 15 | Min ROE %; 0 to disable |
| `--mcap` | 1.0 | Min market cap ($B); 0 to disable |
| `--top` | 25 | Max server-side results |
| `--style` | balanced | Scoring style: balanced, value, growth, quality |
| `--tickers` | (none) | Custom ticker list (bypasses server screen) |
| `--index` | (none) | hsi or hstech (predefined HK lists) |

### Market-Specific Defaults

| Market | PE | ROE | Notes |
|--------|-----|-----|-------|
| US | 20 | 15% | Standard |
| HK | 15-25 | 10-15% | Structural discount |
| JP | 15-20 | 8-12% | Lower ROE norms |
| CN | 20-30 | 10-15% | Scarcity premium |

## Output Schema

CSV columns (fixed order):
`ticker, name, sector, industry, price, market_cap_B, pe, forward_pe, ev_ebitda, roe_pct, revenue_growth_pct, earnings_growth_pct, momentum_52w_pct, debt_equity, score`

The script also prints a formatted report to stdout with ranked table, industry breakdown, and score distribution.

## Translating User Intent

| User says | Parameters |
|-----------|-----------|
| "tech stocks" | `--sector Technology` |
| "semiconductors" | `--sector Technology --industry Semiconductors` |
| "AI stocks" | `--sector Technology --industry Semiconductor` |
| "bank stocks" | `--sector "Financial Services" --industry Banks` |
| "pharma" | `--sector Healthcare --industry "Drug Manufacturers"` |
| "HK tech" | `--region hk --sector Technology` |
| "cheap stocks" / "undervalued" | `--style value` |
| "high growth" | `--style growth`, relax `--pe` to 40+ |
| "quality compounders" | `--style quality` |
| "defensive picks" | `--style quality` |
| "fair value" | Relax `--pe` to 25-30 |
| "all tech, no filter" | `--sector Technology --pe 0 --roe 0` |

## After Running the Script

The script outputs data. Your job is to add the analysis that makes it actionable:

1. **Explain the screening logic** — State what filters and style preset were applied, how many stocks were in the universe, and how many passed.

2. **Analyze top candidates** — For the top 3-5 stocks, explain WHY they scored high by breaking down which of the 5 factors drive the score:
   - "MSFT scores 77.9 (balanced): top valuation rank (PE 23.9, EV/EBITDA 16.4 — cheapest in set), strong profitability (ROE 34.4%), solid growth (38.2% blend), low debt (D/E 31.5). Momentum dragged slightly (-2.9%)."
   - "NVDA scores 79.1 (growth): explosive growth (84.4%) and momentum (42.2%) dominate under growth weights, despite poor valuation rank."

3. **Compare style impact** — If the user's intent suggests a specific style, note how rankings would differ under other presets.

4. **Note industry concentration** — If results cluster in one sub-industry, flag this as concentration risk.

5. **Flag anomalies and filter noise** — The script returns raw data that may include non-ordinary shares (preferred stocks, depositary receipts, dual-listed duplicates like RHHBY/RHHBF for Roche). When presenting results to the user, identify and exclude these: preferred shares typically have abnormally low PE and contain "Depositary" in their name; duplicates are the same company appearing with different tickers. Only surface the primary common stock ticker for each company. Also flag extreme metrics (ROE >100%, negative growth, very high D/E) and explain why.

6. **Recommend next steps** — Suggest using `business-quality` for moat analysis or `valuation-matrix` for DCF/comparable valuation on top picks.
