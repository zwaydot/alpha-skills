---
name: Earnings Analysis
description: Create professional equity research earnings update reports analyzing quarterly results for companies under coverage. Includes beat/miss analysis, guidance review, updated estimates, and thesis impact assessment. Use for equity research, investor communications, and portfolio monitoring.
---

# Earnings Analysis

Create professional earnings update reports for companies under coverage.

## Inputs

- **Ticker symbol**: The company to analyze (e.g. `AAPL`, `TSLA`)
- **Quarter**: Quarter being reported (e.g. Q1 2026) — for labeling
- **Actual results**: Revenue and EPS (if script data is insufficient)
- **Guidance**: Management's forward outlook (from earnings call/release)
- **Prior estimates**: Consensus or internal model estimates

## Outputs

- **JSON file**: `<TICKER>_earnings_YYYYMMDD.json` — structured earnings data
- **Earnings Update Report** (Word/PDF, 8–12 pages)
- **Updated financial model estimates** (Excel)
- **Beat/miss table**: Actuals vs. consensus

## Data Sources

- **Yahoo Finance** (via `yfinance`): EPS history, quarterly financials, forward estimates, analyst consensus
- **User-provided**: Management guidance, earnings call transcript, press release

## Example Usage

```
"Write an earnings update for Apple Q1 2026"
"Did Tesla beat or miss last quarter? Pull the data and summarize"
"Update my Apple model — they just reported: EPS $2.18 vs $2.10 est, Revenue $95.2B vs $93.5B est"
```

## Quick Start: Fetch Earnings Data

```bash
# Fetch comprehensive earnings data for a ticker
python3 scripts/fetch_data.py AAPL

# Save to a named file
python3 scripts/fetch_data.py TSLA --output tsla_q1_earnings.json
```

**Script output includes:**
- EPS actual vs. estimate for last 8 quarters (beat/miss history)
- Quarterly revenue, gross profit, net income, FCF
- YoY comparisons for most recent quarter
- Forward EPS and revenue estimates (analyst consensus)
- Analyst rating, target price, number of analysts
- Current valuation snapshot (P/E trailing/forward, EV/EBITDA)

## Overview

This Skill generates:
- Quarterly earnings summaries
- Beat/miss analysis vs. consensus
- Guidance and management commentary review
- Updated financial estimates
- Investment thesis impact

## Report Structure

**Standard Earnings Update (8-12 pages):**
1. **Executive Summary** (1 page)
2. **Financial Results** (2 pages)
3. **Segment Performance** (1-2 pages)
4. **Guidance & Commentary** (1 page)
5. **Estimate Changes** (1 page)
6. **Valuation Update** (1 page)
7. **Investment Thesis Impact** (1 page)
8. **Appendix** (Charts, tables)

## Workflow

### Step 1: Fetch Earnings Data

```bash
python3 scripts/fetch_data.py AAPL
```

This retrieves:
- Historical EPS beats/misses
- Quarterly income statement + cash flow data
- Analyst consensus estimates (forward EPS, revenue)
- Current analyst rating and price target

### Step 2: Beat/Miss Analysis

Compare actual vs. estimates:

| Metric | Actual | Consensus | Beat/Miss |
|--------|--------|-----------|-----------|
| Revenue | $95.2B | $93.5B | +1.8% ⬆️ |
| EPS | $2.18 | $2.10 | +3.8% ⬆️ |
| Gross Margin | 45.5% | 45.2% | +30bps ⬆️ |

### Step 3: Segment Analysis

Break down by business unit:
- **iPhone**: Units, ASP, Growth
- **Services**: Revenue, Margins
- **Mac/iPad**: Performance
- **Geography**: Regional trends

### Step 4: Guidance Assessment

Analyze management guidance:
- **Revenue outlook**: Q2 and Full year
- **Margin expectations**: Gross, Operating
- **Key drivers**: Growth initiatives, headwinds
- **Confidence level**: Tone assessment

### Step 5: Estimate Updates

Revise forward estimates:
- **Revenue**: FY2026, FY2027
- **EBITDA**: Operating leverage
- **EPS**: Tax rate, share count

### Step 6: Valuation & Thesis

Update:
- **Price target**: New estimates → new PT
- **Rating**: Buy/Hold/Sell reaffirmation
- **Key risks**: What's changed?
- **Catalysts**: Upcoming events

## Usage Examples

### Example 1: Tech Earnings

```
User: "Write earnings update for Apple Q1 2026"

Step 1: python3 scripts/fetch_data.py AAPL

Then provide guidance data:
- EPS actual: $2.18 vs. $2.10 est (+3.8% beat)
- Revenue: $95.2B vs. $93.5B (+1.8% beat)
- iPhone: $52B (+2% YoY)
- Services: $24B (+15% YoY)
- Q2 guidance: Revenue "up low single digits"

Output: 10-page earnings report with updated estimates
```

### Example 2: Quick Beat/Miss Summary

```
User: "Did Nvidia beat last quarter?"

python3 scripts/fetch_data.py NVDA
→ Shows last 4 quarters of EPS actuals vs. estimates
→ Revenue beat/miss with % surprises
→ Analyst consensus and price targets
```

## Best Practices

- **Lead with key numbers** in executive summary
- **Compare to expectations** (not just YoY)
- **Highlight guidance changes** prominently
- **Update price target** if estimates change materially
- **Note thesis impact**: Does this change the story?

## Key Outputs

1. **Earnings Data JSON** (from script)
2. **Earnings Update Report** (Word/PDF)
3. **Consensus Comparison Table**
4. **Updated Price Target**
5. **Catalyst Calendar**

## Related Skills

- `financial-modeling` - For estimate updates
- `initiating-coverage` - For full initiation reports
- `comparables-analysis` - For valuation context
