---
name: Initiating coverage research
description: Conduct comprehensive company research for initiating coverage, including business model analysis, competitive positioning, financial performance review, and valuation. Produces thorough research reports with investment recommendations. Use for equity research initiations, investment committee memos, and strategic assessments.
---

# Initiating Coverage Research

Create comprehensive initiation reports for new coverage.

## Inputs

- **Ticker symbol**: The company to initiate coverage on (e.g. `AAPL`, `TSLA`, `NVDA`)
- **Investment recommendation**: Buy / Hold / Sell with price target
- **Coverage scope**: Full initiation (20-40 pages) or summary memo (5-8 pages)
- **Comparable peers**: For valuation benchmarking
- **Years of history**: For financial analysis (default: 3 price history, 5 financial history)

## Outputs

- **JSON data pack**: `<TICKER>_coverage_data_YYYYMMDD.json` — all research inputs
- **Initiation Report** (PDF/Word, 20-40 pages)
- **Financial Model** (Excel)
- **Valuation Summary** (Football field)

## Data Sources

- **Yahoo Finance** (via `yfinance`): Business overview, financials, price history, analyst consensus, management data
- **SEC EDGAR**: 10-K/10-Q for detailed financials and risk factors
- **Web research**: Industry reports, news, competitive landscape

## Example Usage

```
"Initiate coverage on Tesla with a $250 price target — Overweight"
"Write a coverage initiation memo for NVIDIA"
"Start coverage on BYD (hk01211) with a Buy rating"
```

## Quick Start: Fetch Coverage Data

```bash
# Fetch comprehensive data for coverage initiation
python3 scripts/fetch_data.py AAPL

# Customize history periods
python3 scripts/fetch_data.py TSLA --history-years 3 --financial-years 5

# Save to named output
python3 scripts/fetch_data.py NVDA --output nvda_coverage.json
```

**Script output includes:**
- Company overview (business description, sector, employees, website)
- Financial summary (market cap, EV, revenue, EBITDA, margins, FCF)
- Valuation multiples (P/E, EV/EBITDA, EV/Revenue, P/S, PEG)
- Returns and growth metrics (ROE, ROA, revenue growth, earnings growth)
- 3-year price history with monthly prices, total return, YTD, volatility
- Analyst consensus (rating, price target, upside, # of analysts)
- Recent analyst upgrades/downgrades
- 5-year historical income statement and cash flow

## Overview

This Skill produces:
- 20-40 page initiation reports
- Investment recommendation and price target
- Business model deep-dive
- Competitive positioning
- Financial model and valuation
- Risk assessment

## Report Structure

**Standard Initiation Report:**

1. **Executive Summary** (2-3 pages)
   - Investment thesis
   - Recommendation and PT
   - Key metrics snapshot
   - Bull/Bear scenarios

2. **Company Overview** (3-4 pages)
   - Business model
   - Revenue breakdown
   - Geographic footprint
   - Management team

3. **Industry Analysis** (2-3 pages)
   - TAM/SAM/SOM
   - Industry trends
   - Regulatory environment
   - Competitive landscape

4. **Competitive Positioning** (3-4 pages)
   - Peer comparison
   - Competitive advantages
   - Market share
   - SWOT analysis

5. **Financial Analysis** (4-5 pages)
   - Historical performance
   - Margin analysis
   - Cash flow profile
   - Balance sheet strength

6. **Financial Model** (2-3 pages)
   - Key assumptions
   - 5-year projections
   - Scenario analysis

7. **Valuation** (2-3 pages)
   - DCF valuation
   - Trading comps
   - Precedent transactions
   - Football field

8. **Investment Risks** (1-2 pages)
   - Key risk factors
   - Mitigation factors
   - Sensitivity analysis

9. **Appendix** (3-5 pages)
   - Detailed financials
   - Management bios
   - Glossary

## Workflow

### Step 1: Fetch Research Data

```bash
python3 scripts/fetch_data.py AAPL --history-years 3 --financial-years 5
```

Collect:
- **Business overview**: Description, sector, employees, website
- **Financial summary**: All key metrics in one JSON
- **Price history**: 3-year monthly price data + stats
- **Analyst data**: Consensus rating, price targets, recent changes

### Step 2: Business Model Analysis

Document:
- **What they do**: Products/services
- **How they make money**: Revenue streams
- **Who pays**: Customer segments
- **Competitive moat**: Differentiation

### Step 3: Industry & Competition

- **Market sizing**: TAM, growth rate
- **Industry structure**: Fragmented vs. concentrated
- **Key trends**: Growth drivers, headwinds
- **Competitive dynamics**: Pricing, R&D intensity

### Step 4: Financial Model

Build integrated model:
- **Historical**: 5-year analysis
- **Projections**: 5-year forecast
- **Assumptions**: Growth, margins, capital needs
- **Scenarios**: Bull, Base, Bear

### Step 5: Valuation

Triangulate value:
- **DCF**: Intrinsic value
- **Comps**: Market multiples
- **Precedents**: M&A premiums

### Step 6: Write Report

Generate structured document with:
- Clear thesis statement
- Supporting evidence
- Charts and tables
- Professional formatting

## Usage Examples

### Example 1: Tech Coverage Initiation

```
User: "Initiate coverage on Tesla with $250 PT — Overweight"

Step 1: python3 scripts/fetch_data.py TSLA --history-years 3
Step 2: Review tesla_coverage_data_*.json
Step 3: Claude writes 35-page report

Sections:
1. Investment thesis: EV market leadership + energy business optionality
2. Financial model: 5-year projections
3. Valuation: DCF $220 + Comps $280 → PT $250
4. Risks: Competition, execution, valuation
```

### Example 2: Chinese Company Initiation

```
User: "Initiate on BYD"

Focus areas:
- EV market leadership in China
- Vertical integration (battery tech)
- Global expansion strategy
- Competition with Tesla
- Valuation vs. growth

Output: Bilingual initiation report
```

### Example 3: Quick Coverage Memo

```
User: "Write a 5-page coverage memo on Nvidia"

python3 scripts/fetch_data.py NVDA

Output:
- 1-page thesis: AI infrastructure supercycle
- Financial highlights + growth trajectory
- Valuation: Premium justified by moat
- Rating: Overweight / $900 PT
```

## Best Practices

- **Strong thesis**: Clear buy/sell argument
- **Differentiated view**: What's the market missing?
- **Rigorous model**: Transparent assumptions
- **Balanced risks**: Acknowledge uncertainties
- **Catalysts**: What drives the stock?

## Key Outputs

1. **Coverage Data Pack JSON** (from script)
2. **Initiation Report** (PDF/Word)
3. **Financial Model** (Excel)
4. **Valuation Summary**
5. **Investment Committee Presentation**

## Related Skills

- `financial-modeling` - For detailed projections
- `dcf-modeling` - For valuation
- `comparables-analysis` - For peer benchmarking
- `competitive-landscape` - For industry analysis
