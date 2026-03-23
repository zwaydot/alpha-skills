---
name: earnings-analysis
description: Create professional equity research earnings update reports analyzing quarterly results for companies under coverage. Includes beat/miss analysis, guidance review, updated estimates, and thesis impact assessment. Use for equity research, investor communications, and portfolio monitoring.
---

# Earnings Analysis

Create professional earnings update reports.

## Overview

This Skill generates:
- Quarterly earnings summaries
- Beat/miss analysis vs. consensus
- Guidance and management commentary
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
7. **Investment Thesis** (1 page)
8. **Appendix** (Charts, tables)

## Workflow

### Step 1: Data Collection

```bash
# Fetch earnings data
python3 ~/.openclaw/workspace/skills/financial-services/earnings-analysis/scripts/fetch_earnings.py \
  --ticker AAPL \
  --quarter Q1-2026
```

Collect:
- **Actual results**: Revenue, EPS, margins
- **Consensus estimates**: Bloomberg, FactSet
- **Prior year**: YoY comparison
- **Guidance**: Management outlook
- **Call transcript**: Key commentary

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
- **Key metrics**: Unit sales, ARPU

### Step 6: Valuation & Thesis

Update:
- **Price target**: New estimates → new PT
- **Rating**: Buy/Hold/Sell reaffirmation
- **Key risks**: What's changed?
- **Catalysts**: Upcoming events

## Output Format

**Word/PDF Report** with:
- Professional formatting
- Charts and tables
- Executive summary bullets
- Consistent branding

## Usage Examples

### Example 1: Tech Earnings

```
User: "Write earnings update for Apple Q1 2026"

Inputs:
- Actual EPS: $2.18 vs. $2.10 est (+3.8% beat)
- Revenue: $95.2B vs. $93.5B (+1.8% beat)
- iPhone: $52B (+2% YoY)
- Services: $24B (+15% YoY)
- Guidance: Revenue "up low single digits"

Output: 10-page earnings report with updated estimates
```

### Example 2: Chinese Company

```
User: "Earnings summary for 宁德时代 Q4"

Data:
- Revenue, profit vs. expectations
- Battery volume, ASP trends
- Capacity expansion plans
- EV market outlook

Output: Chinese/English bilingual report
```

## Best Practices

- **Lead with key numbers** in executive summary
- **Compare to expectations** (not just YoY)
- **Highlight guidance changes** prominently
- **Update price target** if estimates change materially
- **Note thesis impact**: Does this change the story?

## Key Outputs

1. **Earnings Update Report** (Word/PDF)
2. **Financial Model Update** (Excel)
3. **Consensus Comparison** (Table)
4. **Updated Price Target**
5. **Catalyst Calendar**

## Related Skills

- `financial-modeling` - For estimate updates
- `initiating-coverage` - For full initiation reports
- `comparables-analysis` - For valuation context
