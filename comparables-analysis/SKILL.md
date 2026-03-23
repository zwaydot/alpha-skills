---
name: comparables-analysis
description: Generate peer benchmarking tables with valuation multiples (EV/Revenue, EV/EBITDA, P/E, P/B) and operating metrics that auto-refresh with live data. Supports both public company trading comps and private company transaction comps. Use for valuation, M&A screening, and competitive positioning analysis.
---

# Comparables Analysis

Create comprehensive comparative analysis between target company and selected peers.

## Overview

This Skill generates:
- Trading comparables (public companies)
- Transaction comparables (M&A deals)
- Operating metrics benchmarking
- Valuation multiple analysis

## Data Sources

- **Yahoo Finance**: US/international public companies
- **Tencent Finance**: A-shares, Hong Kong stocks
- **User data**: Private company financials, transaction databases
- **Manual input**: For non-public peers

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

### Step 2: Data Extraction

```bash
# Fetch peer data
python3 ~/.openclaw/workspace/skills/financial-services/comparables-analysis/scripts/fetch_peers.py \
  --target AAPL \
  --peers MSFT,GOOGL,META,AMZN

# Output: peers_data.json
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

Create Excel output with:
- **Summary table**: All peers with key metrics
- **Multiple comparison**: Charts showing valuation ranges
- **Operating metrics**: Efficiency and profitability comparison
- **Implied valuation**: Apply median/multiple to target

## Output Format

**Excel File** with multiple sheets:

1. **Summary**: Target + Peers key data
2. **Trading Multiples**: EV/Revenue, EV/EBITDA, P/E comparison
3. **Operating Metrics**: Margins, growth, returns
4. **Implied Valuation**: Range based on peer multiples
5. **Notes**: Peer selection rationale

## Usage Examples

### Example 1: Tech company comps

```
User: "Run trading comps for Tesla vs EV peers"

Target: TSLA
Peers: RIVN, LCID, NIO, XPEV, BYD (hk01211)
Multiples: EV/Revenue, EV/EBITDA, P/S

Output:
- Median EV/Revenue: 3.2x
- TSLA trading at: 5.8x (82% premium)
- Implied price range: $180-$280
```

### Example 2: Chinese bank comps

```
User: "Compare ICBC with other major Chinese banks"

Target: 工商银行 (sh601398)
Peers: 建设银行(sh601939), 农业银行(sh601288), 招商银行(sh600036)
Metrics: P/B, P/E, NIM, NPL ratio, ROE

Output: Banking sector comps table
```

### Example 3: M&A Transaction comps

```
User: "Find precedent transactions in SaaS space last 2 years"

Filter: 
- Target: SaaS companies
- Deal size: $500M-$5B
- Date: 2023-2025

Output: Transaction multiples (EV/Revenue, EV/ARR)
```

## Best Practices

- **Minimum 4-6 peers** for statistical relevance
- **Document selection criteria** for audit trail
- **Use both TTM and forward multiples**
- **Flag outliers** (high debt, one-time items)
- **Include footnotes** for non-GAAP adjustments

## Key Outputs

1. **Peer Comparison Table** (Excel)
2. **Valuation Multiple Ranges** (Min, Max, Median, Mean)
3. **Operating Metrics Benchmark**
4. **Implied Valuation Range**
5. **Peer Selection Justification**

## Related Skills

- `financial-modeling` - For detailed target company model
- `dcf-modeling` - For intrinsic valuation complement
- `initiating-coverage` - For full research report
