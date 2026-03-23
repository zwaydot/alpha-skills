---
name: initiating-coverage
description: Conduct comprehensive company research for initiating coverage, including business model analysis, competitive positioning, financial performance review, and valuation. Produces thorough research reports with investment recommendations. Use for equity research initiations, investment committee memos, and strategic assessments.
---

# Initiating Coverage Research

Create comprehensive initiation reports for new coverage.

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

### Step 1: Research & Data Collection

```bash
# Gather all source materials
python3 ~/.openclaw/workspace/skills/financial-services/initiating-coverage/scripts/research_prep.py \
  --ticker AAPL \
  --output "research_data.json"
```

Collect:
- **SEC Filings**: 10-K, 10-Q, Proxy statements
- **Earnings**: Transcripts, Presentations
- **Industry**: Research reports, News
- **Competitors**: Peer financials
- **Management**: Backgrounds, Track record

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

## Output Format

**PDF/Word Report** (20-40 pages):
- Title page with stock info
- Table of contents
- Section headers
- Page numbers
- Professional styling

## Usage Examples

### Example 1: Tech Coverage Initiation

```
User: "Initiate coverage on Tesla with $250 PT"

Process:
1. Research: 10-Ks, earnings calls, competitor analysis
2. Model: 5-year financial projections
3. Valuation: DCF + Comps → $250 PT
4. Rating: Overweight (bullish on EV adoption)
5. Risks: Competition, execution, valuation

Output: 35-page initiation report
```

### Example 2: Chinese Company Initiation

```
User: "Initiate on 比亚迪 (BYD)"

Focus areas:
- EV market leadership in China
- Vertical integration (battery tech)
- Global expansion strategy
- Competition with Tesla
- Valuation vs. growth

Output: Bilingual initiation report
```

## Best Practices

- **Strong thesis**: Clear buy/sell argument
- **Differentiated view**: What's the market missing?
- **Rigorous model**: Transparent assumptions
- **Balanced risks**: Acknowledge uncertainties
- **Catalysts**: What drives the stock?

## Key Outputs

1. **Initiation Report** (PDF/Word)
2. **Financial Model** (Excel)
3. **Valuation Summary**
4. **Investment Committee Presentation**
5. **Catalyst Calendar**

## Related Skills

- `financial-modeling` - For detailed projections
- `dcf-modeling` - For valuation
- `comparables-analysis` - For peer benchmarking
- `competitive-landscape` - For industry analysis
