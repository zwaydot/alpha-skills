---
name: Stock Screener
description: Multi-factor stock screening with server-side filtering — finds stocks by sector, industry, valuation, and profitability across US, HK, and other markets. Use this when the user asks to screen stocks, find investment candidates, filter by sector/industry, compare stocks on quality metrics, or scan a market for opportunities. Works with Yahoo Finance (yfinance) by default, but the methodology adapts to any market data API (FMP, Longbridge, Alpaca, etc.).
---

# Stock Screener

Multi-factor stock screening using a two-phase architecture: server-side filtering narrows the universe, then detail enrichment scores the top candidates.

## Two-Phase Architecture

**Phase 1 — Server-side filter** (1 API call):
Query the data provider's screener endpoint with sector, PE, ROE, and market cap constraints. Returns only matching candidates.

**Phase 2 — Detail enrichment** (N calls, N = 25-50):
Fetch full financial profiles for Phase 1 candidates. Re-validate filters (server and detail data can diverge), then score and rank.

This avoids scanning thousands of stocks individually. The bundled script uses Yahoo Finance's `EquityQuery` + `screen()` for Phase 1. If the user has a different data source (FMP, Longbridge MCP, Alpaca MCP), apply the same two-phase pattern with that API's screener endpoint.

## Scoring System (0-100)

| Component | Weight | Logic |
|-----------|--------|-------|
| Valuation | 30% | Lower P/E relative to max_pe threshold scores higher |
| Profitability | 30% | Higher ROE above min_roe threshold scores higher |
| Growth | 25% | Revenue growth 0-30%+ maps linearly to score |
| Scale | 15% | Market cap $1B-$1T on log scale |

Scores are continuous, not bucketed. A stock scoring 65 vs 45 reflects meaningful quality difference — explain this to the user by breaking down which components drive the gap.

## Script Usage

```bash
# US tech stocks (server-side screen, fast)
python3 scripts/fetch_data.py --sector Technology --pe 25

# Sub-industry filter (server filters sector, client filters industry)
python3 scripts/fetch_data.py --sector Technology --industry Semiconductors

# HK market
python3 scripts/fetch_data.py --region hk --sector Technology

# Custom tickers (direct fetch, no server screen)
python3 scripts/fetch_data.py --tickers AAPL MSFT NVDA TSLA META --pe 40 --roe 10

# Predefined HK index
python3 scripts/fetch_data.py --index hstech

# More results / no financial filters
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

CSV columns (fixed order, consistent across data providers):
`ticker, name, sector, industry, price, market_cap_B, pe, roe_pct, revenue_growth_pct, score`

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
| "fair value" | Relax `--pe` to 25-30 |
| "high growth" | Lower `--roe` to 10 |
| "all tech, no filter" | `--sector Technology --pe 0 --roe 0` |

## After Running the Script

The script outputs data. Your job is to add the analysis that makes it actionable:

1. **Explain the screening logic** — State what filters were applied, how many stocks were in the universe, and how many passed. The user needs to understand what they're looking at.

2. **Analyze top candidates** — For the top 3-5 stocks, explain WHY they scored high by breaking down the score components:
   - "ADBE scores 61.8: strong valuation (PE 14.5 vs 25 threshold = full valuation points), high profitability (ROE 58.8%), moderate growth (12%)"
   - "JPM scores 45.0: excellent valuation (PE 14.3) but lower profitability (ROE 16.1% barely above 15% threshold)"

3. **Note industry concentration** — If results cluster in one sub-industry (e.g., 6 of 10 are Software), flag this as concentration risk.

4. **Flag anomalies** — Stocks with extreme metrics (ROE >100%, negative growth, PE near threshold) deserve a note.

5. **Recommend next steps** — Suggest using `business-quality` for moat analysis or `valuation-matrix` for DCF/comparable valuation on top picks.
