---
name: financial-modeling
description: Build integrated three-statement financial models (income statement, balance sheet, cash flow statement) from sellside models, SEC filings, or company reports. Creates proper linkages across all statements with scenario analysis, valuation modules, and sensitivity tables. Use for company valuation, M&A analysis, investment research, and credit analysis.
---

# 3-Statement Financial Modeling

Build integrated three-statement financial models with proper accounting linkages.

## Overview

This Skill creates comprehensive three-statement financial models by:
1. Extracting historical financial data from filings or reports
2. Building forecast drivers and assumptions
3. Creating integrated income statement, balance sheet, and cash flow statement
4. Adding valuation modules and sensitivity analysis

## Data Sources

- **SEC Filings**: 10-K, 10-Q from EDGAR (US companies)
- **Company Reports**: Annual reports, investor presentations
- **Third-party data**: Yahoo Finance, tencent-finance (for A-shares/HK)
- **User-provided**: Excel models, CSV data exports

## Workflow

### Step 1: Data Collection

```bash
# For US stocks
python3 ~/.openclaw/workspace/skills/financial-services/financial-modeling/scripts/fetch_sec.py <ticker>

# For A-shares
python3 ~/.openclaw/workspace/skills/financial-services/financial-modeling/scripts/fetch_cn.py <stock_code>

# For HK stocks
python3 ~/.openclaw/workspace/skills/financial-services/financial-modeling/scripts/fetch_hk.py <stock_code>
```

### Step 2: Model Structure Setup

Create Excel template with:
- **Assumptions tab**: Growth rates, margins, working capital days, CapEx
- **Income Statement**: Revenue down to Net Income
- **Balance Sheet**: Assets, Liabilities, Equity with balancing checks
- **Cash Flow Statement**: Operating, Investing, Financing activities
- **Supporting Schedules**: PP&E rollforward, Debt schedule, Equity schedule
- **Checks**: Balance sheet balancing, Cash reconciliation

### Step 3: Historical Data Population

Extract 3-5 years of historical data:
- Revenue by segment (if available)
- Cost structure (COGS, OpEx breakdown)
- Working capital components
- PP&E and depreciation
- Debt and interest expense
- Tax rates and NOLs

### Step 4: Forecast Drivers

Build forecast assumptions:
- **Revenue growth**: Organic growth, M&A, segment breakdown
- **Margins**: Gross margin, EBITDA margin, Operating margin trends
- **Working capital**: Days sales outstanding, inventory days, payables days
- **CapEx**: Maintenance vs. growth CapEx as % of sales
- **Capital structure**: Debt/Equity ratio, interest rates

### Step 5: Model Linkages

Ensure proper accounting flows:
1. Net Income → Retained Earnings (Balance Sheet)
2. Depreciation → PP&E schedule → Cash Flow
3. Working capital changes → Cash Flow from Operations
4. CapEx → PP&E → Cash Flow from Investing
5. Debt issuance/repayment → Cash Flow from Financing
6. Cash from Cash Flow Statement → Balance Sheet Cash

### Step 6: Valuation Module

Add valuation outputs:
- **DCF valuation**: FCFF/FCFE projections, WACC calculation
- **Trading comps**: EV/Revenue, EV/EBITDA, P/E multiples
- **Precedent transactions**: M&A premiums analysis

### Step 7: Sensitivity Analysis

Create data tables for:
- Revenue growth vs. EBITDA margin
- WACC vs. Terminal growth rate
- CapEx intensity vs. Working capital efficiency

## Output Format

**Excel File** with:
- Color-coded cells (blue for inputs, black for formulas, green for checks)
- Clear section headers
- Error checking formulas
- Print-ready summary pages

## Usage Examples

### Example 1: Build model for Apple

```
User: "Create a three-statement model for AAPL using their latest 10-K"

1. Fetch AAPL 10-K data from SEC EDGAR
2. Extract 5-year historical financials
3. Build assumptions based on historical trends
4. Create 5-year projections
5. Add DCF valuation with WACC calculation
6. Include sensitivity tables
7. Output: AAPL_Financial_Model.xlsx
```

### Example 2: Model for Chinese company

```
User: "Build three-statement model for 茅台 (sh600519)"

1. Use tencent-finance to fetch historical data
2. Extract annual report financials
3. Build model with Chinese accounting standards
4. Add sensitivity to alcohol consumption trends
5. Output: Moutai_Financial_Model.xlsx
```

## Best Practices

- Always include circular reference breaking (average debt balance method)
- Build error checks (Balance Sheet must balance, Cash reconciliation)
- Document assumptions clearly
- Use conservative, base, and optimistic scenarios
- Validate against sellside consensus estimates

## Key Outputs

1. **Integrated 3-Statement Model** (Excel)
2. **Valuation Summary** (DCF, Comps, Precedents)
3. **Sensitivity Analysis Dashboard**
4. **Assumptions Documentation** (separate sheet)
5. **Executive Summary** (key metrics and ratios)

## Related Skills

- `dcf-modeling` - For detailed DCF valuation
- `comparables-analysis` - For peer benchmarking
- `earnings-analysis` - For quarterly updates to the model
