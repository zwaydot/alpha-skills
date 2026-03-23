---
name: Competitive Landscape Assessment
description: Create structured competitive landscape assessments with market positioning analysis, competitive dynamics evaluation, and strategic recommendations. Use for market entry analysis, strategic planning, investor presentations, and due diligence.
---

# Competitive Landscape Assessment

Build comprehensive competitive positioning analyses comparing a target company against key peers.

## Inputs

- **Target company**: Ticker symbol (e.g. `AAPL`) or company name
- **Competitors**: 3–8 competitor tickers (e.g. `MSFT GOOGL META`)
- **Analysis focus**: Valuation, profitability, growth, financial health — or all
- **Output format**: JSON + CSV (default) or Markdown table

## Outputs

- **JSON file**: `<TARGET>_competitive_landscape_YYYYMMDD_HHMM.json` — full data + insights
- **CSV file**: `<TARGET>_competitive_landscape_YYYYMMDD_HHMM.csv` — tabular comparison
- **Competitive positioning summary**: Rankings across market cap, revenue, margins, valuation

## Data Sources

- **Yahoo Finance** (via `yfinance`): Market cap, EV, revenue, EBITDA, margins, growth, valuation multiples, R&D spend, leverage, dividends, beta

## Example Usage

```
"Map the competitive landscape for Apple vs. FAANG"
"Compare Tesla to EV competitors: RIVN, NIO, XPEV"
"Competitive assessment for Nvidia vs. AMD and Intel"
```

## Quick Start: Fetch Competitive Data

```bash
# Compare Apple to tech peers
python3 scripts/fetch_data.py AAPL --competitors MSFT GOOGL META AMZN

# EV competitive landscape
python3 scripts/fetch_data.py TSLA --competitors RIVN NIO XPEV BYD

# Save named output with CSV
python3 scripts/fetch_data.py NVDA --competitors AMD INTC QCOM --output semis_landscape.json --csv
```

**Script output includes:**
- Market cap ranking among peers
- Revenue comparison
- Profitability comparison (gross, operating, net margins, ROE, ROA)
- Valuation comparison (EV/Revenue, EV/EBITDA, P/E trailing/forward, PEG)
- Growth comparison (revenue growth YoY, earnings growth YoY)
- Financial health (current ratio, debt/equity, net debt, FCF)
- R&D spend, dividend yield, beta

## Overview

This Skill creates:
- Competitive positioning analysis
- Market share and scale comparison
- Profitability and efficiency benchmarking
- Valuation relative to peers
- Strategic strengths and weakness assessment

## Analysis Dimensions

| Dimension | Metrics |
|-----------|---------|
| **Scale** | Market Cap, Revenue, Employees |
| **Profitability** | Gross/Op/Net Margins, ROE, ROA |
| **Growth** | Revenue YoY, Earnings YoY |
| **Valuation** | EV/Revenue, EV/EBITDA, P/E, PEG |
| **Financial Health** | Current Ratio, Debt/Equity, Net Debt, FCF |
| **Innovation** | R&D Spend, R&D % Revenue |
| **Returns** | Dividend Yield, Buyback yield |

## Workflow

### Step 1: Fetch Competitive Data

```bash
python3 scripts/fetch_data.py <TARGET> --competitors <PEER1> <PEER2> <PEER3> --csv
```

### Step 2: Analyze Competitive Position

From the JSON insights:
- **Market cap ranking**: Where does target sit vs. peers?
- **Revenue scale**: Leader, challenger, or follower?
- **Margin profile**: Premium margins = stronger moat?
- **Valuation premium/discount**: Justified by growth?

### Step 3: Competitive Dynamics

Assess:
- **Barriers to entry**: Capital, IP, network effects, switching costs
- **Competitive intensity**: Pricing pressure, R&D arms race
- **Market share trends**: Who's gaining/losing?
- **Disruption risks**: New entrants, technology shifts

### Step 4: Strategic Assessment

- **Porter's Five Forces**: Buyer/supplier power, substitutes, rivalry
- **SWOT**: Strengths, Weaknesses, Opportunities, Threats
- **Positioning map**: Price vs. quality, growth vs. profitability
- **Strategic recommendations**: Where to compete, how to win

## Usage Examples

### Example 1: Big Tech Competitive Landscape

```
User: "Map competitive landscape for Apple vs. FAANG"

python3 scripts/fetch_data.py AAPL --competitors MSFT GOOGL META AMZN NVDA --csv

Output:
Market Cap Ranking: 1.AAPL 2.MSFT 3.NVDA 4.GOOGL 5.AMZN 6.META
EV/Revenue: NVDA(30x) > MSFT(13x) > AAPL(8x) > META(7x) > GOOGL(6x) > AMZN(4x)
Gross Margin: MSFT(70%) > META(81%) > GOOGL(58%) > AAPL(46%) > AMZN(47%)
Revenue Growth: NVDA(122%) > META(22%) > GOOGL(14%) > MSFT(13%) > AAPL(2%)
```

### Example 2: EV Competitive Landscape

```
User: "Competitive assessment for Tesla vs. EV peers"

python3 scripts/fetch_data.py TSLA --competitors RIVN LCID NIO XPEV --csv

Analysis:
- Tesla: Only profitable EV pure-play
- Chinese OEMs: Scale advantage in home market
- US startups: Pre-profit, high cash burn
- Valuation: Tesla still commands significant premium
```

### Example 3: Semiconductor Landscape

```
User: "Compare Nvidia to AMD and Intel"

python3 scripts/fetch_data.py NVDA --competitors AMD INTC QCOM TSM

Key insights:
- NVDA leads on margins (55% gross) and growth (122% rev)
- INTC: Turnaround story, underperforming on margins
- AMD: Gaining share in CPU/GPU vs. INTC
- TSM: Foundry leader, different business model
```

## Best Practices

- **Use 4-8 competitors** for meaningful comparison
- **Compare like for like**: Similar stage companies when possible
- **Contextualize outliers**: Explain unusual multiples
- **Update regularly**: Market positions change quickly
- **Include qualitative factors**: Brand, IP, management quality

## Key Outputs

1. **Competitive Data JSON** (from script)
2. **Peer Comparison CSV** (tabular format)
3. **Competitive Positioning Map**
4. **Strategic Assessment Narrative**
5. **Ranking Summary** (Market cap, revenue, margins, valuation)

## Related Skills

- `comparables-analysis` - For detailed valuation multiples
- `initiating-coverage` - For full research report
- `financial-modeling` - For deeper financial analysis
