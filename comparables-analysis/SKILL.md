---
name: Comps analysis with public/private peers
description: Generate peer benchmarking tables with valuation multiples (EV/Revenue, EV/EBITDA, P/E, P/B) and operating metrics that auto-refresh with live data. Supports both public company trading comps and private company transaction comps. Use for valuation, M&A screening, and competitive positioning analysis.
---

# Comps Analysis with Public/Private Peers

Create comprehensive comparative analysis between a target company and selected peers.

## Inputs

- **Target company**: Ticker symbol or company name (e.g. `AAPL`, `Tesla`)
- **Peer list**: 4–10 comparable company tickers (e.g. `MSFT GOOGL META AMZN`)
- **Comps type**: Trading comps (public) or transaction comps (M&A)
- **Market**: US (default), China A-shares (`sh`/`sz` prefix), Hong Kong (`hk` prefix)
- **Optional**: Custom metric weights, outlier exclusion criteria

## Outputs

- **CSV file**: `comps_YYYYMMDD_HHMM.csv` — all peers with key metrics
- **Markdown table**: Formatted comparison with valuation multiples
- **Implied valuation range**: Median/mean multiple applied to target

## Data Sources

- **Yahoo Finance** (via `yfinance`): US & international public companies
- **SEC EDGAR**: For deeper financial detail on US companies
- **User-provided**: Private company financials, transaction databases

## Example Usage

```
"Run trading comps for Tesla vs. EV peers: RIVN, NIO, XPEV"
"Compare Apple to FAANG peers on EV/Revenue and P/E"
"Build a SaaS comps table for a $500M ARR company"
```

## Quick Start: Fetch Live Data

```bash
# Fetch valuation multiples for a peer group
python3 scripts/fetch_data.py AAPL MSFT GOOGL META AMZN

# Save to a named CSV
python3 scripts/fetch_data.py TSLA RIVN LCID NIO XPEV --output ev_comps.csv

# Also export JSON
python3 scripts/fetch_data.py AAPL MSFT GOOGL --json
```

**Output fields per company:**
- Market Cap, Enterprise Value
- Revenue TTM, EBITDA TTM
- Trailing P/E, Forward P/E, P/B
- EV/Revenue, EV/EBITDA
- Gross Margin, Operating Margin, Net Margin
- Revenue Growth YoY, Earnings Growth YoY
- ROE, ROA, Debt/Equity, Free Cash Flow

## Overview

This Skill generates:
- Trading comparables (public companies)
- Transaction comparables (M&A deals)
- Operating metrics benchmarking
- Valuation multiple analysis

## Supported Markets

| Market | Code Prefix | Example |
|--------|-------------|---------|
| US Stocks | (none) | AAPL, MSFT |
| China A-Shares | sh/sz | sh600519, sz000001 |
| Hong Kong | hk | hk00700, hk09988 |

## Workflow

### Step 1: Peer Selection

Identify comparable companies based on:
- **Industry/Sector**: Same or adjacent industries
- **Size**: Revenue, market cap range
- **Growth profile**: High growth vs. mature
- **Business model**: Similar revenue streams
- **Geography**: Regional vs. global players

### Step 2: Fetch Live Data

```bash
python3 scripts/fetch_data.py AAPL MSFT GOOGL META AMZN --output tech_comps.csv
```

### Step 3: Calculate Multiples

**Valuation Multiples:**
- EV/Revenue (TTM and forward)
- EV/EBITDA (TTM and forward)
- P/E (TTM and forward)
- P/B (Book value)
- EV/FCF (Free cash flow)

**Operating Metrics:**
- Revenue growth (YoY, 3-year CAGR)
- Gross margin, EBITDA margin, Operating margin
- ROE, ROA, ROIC
- Debt/Equity, Net debt/EBITDA
- CapEx/Revenue

### Step 4: Generate Output

Create output with:
- **Summary table**: All peers with key metrics
- **Multiple comparison**: Valuation ranges
- **Operating metrics**: Efficiency and profitability comparison
- **Implied valuation**: Apply median/multiple to target

## Output Format

**CSV + Markdown Table** with:
1. **Summary**: Target + Peers key data
2. **Trading Multiples**: EV/Revenue, EV/EBITDA, P/E comparison
3. **Operating Metrics**: Margins, growth, returns
4. **Implied Valuation**: Range based on peer multiples

## Usage Examples

### Example 1: Tech company comps

```
User: "Run trading comps for Tesla vs EV peers"

python3 scripts/fetch_data.py TSLA RIVN LCID NIO XPEV --output ev_comps.csv

Output:
- Median EV/Revenue: 3.2x
- TSLA trading at: 5.8x (82% premium)
- Implied price range: $180-$280
```

### Example 2: Large-cap tech comps

```
User: "Compare Apple to mega-cap tech"

python3 scripts/fetch_data.py AAPL MSFT GOOGL META AMZN NVDA

Output: Tech sector comps table with valuations and margins
```

### Example 3: M&A Transaction comps

```
User: "Find precedent transactions in SaaS space last 2 years"

→ Claude analyzes deal databases and structures output:
- Target: SaaS companies, $500M-$5B deal size
- Transaction multiples (EV/Revenue, EV/ARR)
```

## Best Practices

- **Minimum 4-6 peers** for statistical relevance
- **Document selection criteria** for audit trail
- **Use both TTM and forward multiples**
- **Flag outliers** (high debt, one-time items)
- **Include footnotes** for non-GAAP adjustments

## Key Outputs

1. **Peer Comparison CSV** — all metrics per company
2. **Valuation Multiple Ranges** (Min, Max, Median, Mean)
3. **Operating Metrics Benchmark**
4. **Implied Valuation Range**
5. **Peer Selection Justification**

## Related Skills

- `financial-modeling` - For detailed target company model
- `dcf-modeling` - For intrinsic valuation complement
- `initiating-coverage` - For full research report
