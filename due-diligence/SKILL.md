---
name: due-diligence
description: Process data room documents into structured Excel data packs with financials, customer lists, contract terms, and risk factors. Standardize CIMs, offering memorandums, and due diligence materials into consistent formats. Use for PE/VC investment analysis, M&A due diligence, and transaction execution.
---

# Due Diligence Data Pack Creation

Extract and organize key information from due diligence materials.

## Overview

This Skill processes:
- CIMs (Confidential Information Memorandums)
- Offering memorandums
- Data room documents
- Management presentations

Into standardized data packs for investment analysis.

## Document Types

| Document | Key Data Extracted |
|----------|-------------------|
| CIM | Financial summary, Business overview, Investment highlights |
| Financial Statements | Historical financials, KPIs, Segment data |
| Customer Lists | Revenue concentration, Top customers, Churn |
| Contracts | Key terms, Maturity dates, Revenue recognition |
| Cap Table | Ownership structure, Option pools, Dilution |
| Org Chart | Management team, Key personnel |

## Workflow

### Step 1: Document Ingestion

```bash
# Process DD documents
python3 ~/.openclaw/workspace/skills/financial-services/due-diligence/scripts/process_dd.py \
  --input "/path/to/data-room" \
  --output "DD_Data_Pack.xlsx"
```

Supported formats: PDF, Excel, Word, Images (OCR)

### Step 2: Financial Data Extraction

Extract historical financials (3-5 years):
- **Income Statement**: Revenue, EBITDA, Net Income by segment
- **Balance Sheet**: Assets, Liabilities, Working capital
- **Cash Flow**: Operating, Investing, Financing
- **KPIs**: Unit economics, CAC, LTV, Churn, ARPU

### Step 3: Customer Analysis

```
Customer Data Pack:
- Top 20 customers (revenue, % of total)
- Revenue concentration (HHI index)
- Customer churn analysis
- Contract renewal schedule
- Geographic distribution
```

### Step 4: Contract Summary

Extract key terms:
- **Pricing**: Fixed vs. variable, Escalation clauses
- **Duration**: Contract length, Renewal options
- **Termination**: Notice periods, Exit costs
- **Key clauses**: Change of control, Most favored customer

### Step 5: Risk Factor Compilation

Identify and categorize risks:
- **Business risks**: Customer concentration, Competition
- **Financial risks**: Leverage, Working capital needs
- **Operational risks**: Key person dependency, Supply chain
- **Legal/Regulatory**: Compliance, Litigation, IP

### Step 6: Data Pack Assembly

Create standardized Excel workbook:

**Sheet Structure:**
1. **Executive Summary**: Key metrics, Investment highlights
2. **Financial Summary**: Historical + Projected
3. **Revenue Build**: By segment, By customer, By geography
4. **Cost Structure**: Fixed vs. Variable, Operating leverage
5. **Customer Analysis**: Concentration, Churn, LTV/CAC
6. **Contract Summary**: Key terms, Maturity schedule
7. **Cap Table**: Ownership, Options, Dilution
8. **Management Bios**: Key personnel
9. **Risk Factors**: Categorized list
10. **DD Checklist**: Status tracker

## Output Format

**Excel Data Pack** with:
- Standardized formatting
- Data validation
- Source references (document + page)
- Quality checks (totals, cross-references)

## Usage Examples

### Example 1: PE Buyout DD

```
User: "Create DD data pack for acquisition target"

Documents: CIM, Audited financials, Customer list, Cap table

Output:
- 5-year financial summary
- Top 10 customers (60% of revenue)
- Key contracts (avg 3-year term)
- Management equity: 15%
- Key risks: Customer concentration, Founder dependency
```

### Example 2: VC Series B DD

```
User: "Analyze SaaS startup for Series B investment"

Data: ARR growth, Customer cohorts, Burn rate, Cap table

Output:
- ARR build by quarter
- Net revenue retention: 120%
- CAC payback: 18 months
- Runway: 12 months
- Founders: 45% ownership (post-money)
```

## Best Practices

- **Source every data point** (document + page)
- **Cross-check totals** (do segments sum to total?)
- **Highlight red flags** in red/yellow
- **Include data quality notes**
- **Track DD status** (received, reviewed, complete)

## Key Outputs

1. **DD Data Pack** (Excel)
2. **Executive Summary** (1-page)
3. **Risk Assessment Matrix**
4. **Investment Committee Memo**
5. **DD Checklist Status**

## Related Skills

- `financial-modeling` - For detailed modeling
- `strip-profile` - For company overview
- `comparables-analysis` - For valuation context
