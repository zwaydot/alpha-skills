---
name: Due diligence data pack creation
description: Process data room documents into structured Excel data packs with financials, customer lists, contract terms, and risk factors. Standardize CIMs, offering memorandums, and due diligence materials into consistent formats. Use for PE/VC investment analysis, M&A due diligence, and transaction execution.
---

# Due Diligence Data Pack Creation

Extract and organize key information from due diligence materials.

## Inputs

- **Public company ticker**: For automated SEC EDGAR document retrieval (e.g. `AAPL`)
- **Private company**: Upload CIM, financial statements, customer lists, contracts
- **Data room access**: Folder of documents (PDF, Excel, Word)
- **Form types**: Which SEC filings to retrieve (default: 10-K, 10-Q)

## Outputs

- **JSON file**: `<TICKER>_edgar_YYYYMMDD.json` — filing metadata and document URLs
- **Excel Data Pack**: Structured workbook with financials, customers, contracts, risks
- **DD Checklist**: Itemized status tracker with source references

## Data Sources

- **SEC EDGAR API** (free, no key required): `https://data.sec.gov/submissions/CIK{}.json`
  - 10-K annual reports, 10-Q quarterly reports
  - DEF 14A proxy statements, 8-K material events
  - XBRL structured financial data
- **User-provided documents**: CIM, data room PDFs, Excel exports

## Example Usage

```
"Pull the latest 10-K and 10-Q filings for Apple"
"Create a DD data pack for this SaaS acquisition target — here's the CIM"
"Get all recent SEC filings for Microsoft and summarize key risks from 10-K"
```

## Quick Start: Fetch SEC EDGAR Filings

```bash
# Fetch latest 10-K and 10-Q for a US company
python3 scripts/fetch_data.py AAPL

# Specify which forms to retrieve
python3 scripts/fetch_data.py MSFT --forms 10-K 10-Q DEF14A --limit 5

# Use known CIK directly (Apple = 0000320193)
python3 scripts/fetch_data.py AAPL --cik 0000320193 --output apple_dd.json
```

**Script output includes:**
- Company metadata (CIK, SIC code, state, fiscal year end)
- Links to all recent 10-K and 10-Q filings
- Direct document URLs for reading/downloading
- EDGAR company page and XBRL data links
- DD checklist with key sections per form type

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
| 10-K / Annual Report | Historical financials, KPIs, Segment data, Risk factors |
| 10-Q / Quarterly | Latest quarter results, interim MD&A |
| Customer Lists | Revenue concentration, Top customers, Churn |
| Contracts | Key terms, Maturity dates, Revenue recognition |
| Cap Table | Ownership structure, Option pools, Dilution |
| Org Chart | Management team, Key personnel |

## Workflow

### Step 1: Document Collection

**For public companies:**
```bash
python3 scripts/fetch_data.py AAPL --forms 10-K 10-Q 8-K
```

**For private companies:**
- Upload: CIM, financial statements, customer list, cap table
- Specify: Company name, sector, deal type

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

## Usage Examples

### Example 1: Public company filing review

```
User: "Get Apple's latest 10-K and summarize risks"

python3 scripts/fetch_data.py AAPL --forms 10-K
→ Retrieves filing URL
→ Claude reads and summarizes Item 1A (Risk Factors)
→ Claude extracts MD&A, financial highlights
```

### Example 2: PE Buyout DD

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

### Example 3: VC Series B DD

```
User: "Analyze SaaS startup for Series B investment"

Data: ARR growth, Customer cohorts, Burn rate, Cap table

Output:
- ARR build by quarter
- Net revenue retention: 120%
- CAC payback: 18 months
- Runway: 12 months
```

## Best Practices

- **Source every data point** (document + page)
- **Cross-check totals** (do segments sum to total?)
- **Highlight red flags** in red/yellow
- **Include data quality notes**
- **Track DD status** (received, reviewed, complete)

## Key Outputs

1. **EDGAR Filing Links JSON** (from script)
2. **DD Data Pack** (Excel)
3. **Executive Summary** (1-page)
4. **Risk Assessment Matrix**
5. **DD Checklist Status**

## Related Skills

- `financial-modeling` - For detailed modeling
- `comparables-analysis` - For valuation context
- `initiating-coverage` - For full research report
