---
name: Integrated Three-Statement Financial Modeling
description: Build integrated three-statement financial models (income statement, balance sheet, cash flow statement) from sellside models, SEC filings, or company reports. Creates proper linkages across all statements with scenario analysis, valuation modules, and sensitivity tables. Use for company valuation, M&A analysis, investment research, and credit analysis.
---

# Integrated Three-Statement Financial Modeling

Build integrated three-statement financial models with proper accounting linkages.

## Inputs

- **Ticker symbol**: For automated data fetching (e.g. `AAPL`, `MSFT`)
- **Period type**: Annual (default) or quarterly
- **Years of history**: 3–5 years (default: 5)
- **Scenario assumptions**: Revenue growth rates, margin targets, CapEx %
- **Optional**: User-provided Excel model or CSV to override fetched data

## Outputs

- **JSON file**: `<TICKER>_3statement_annual_YYYYMMDD.json` — all three statements + ratios
- **Excel Model**: Income statement, balance sheet, cash flow with proper linkages
- **Ratio summary**: Margins, returns, leverage, coverage ratios per year

## Data Sources

- **Yahoo Finance** (via `yfinance`): Annual and quarterly financial statements
- **SEC EDGAR**: 10-K/10-Q filings for US companies (deeper detail)
- **User-provided**: Sellside models, company IR presentations, CSV exports

## Example Usage

```
"Build a three-statement model for Apple"
"Model Tesla's financials for the last 5 years — annual"
"Create projections for NVDA with 25% revenue growth and 55% gross margins"
```

## Quick Start: Fetch Historical Data

```bash
# Fetch 5-year annual financial statements (default)
python3 scripts/fetch_data.py AAPL

# Fetch quarterly data
python3 scripts/fetch_data.py AAPL --quarterly

# Specify years
python3 scripts/fetch_data.py MSFT --years 7 --output msft_3statement.json

# Both annual and quarterly
python3 scripts/fetch_data.py NVDA --output nvda_annual.json
python3 scripts/fetch_data.py NVDA --quarterly --output nvda_quarterly.json
```

**Script output includes:**
- Full income statement (revenue → net income) per year
- Full balance sheet (assets, liabilities, equity) per year
- Full cash flow statement (operating, investing, financing) per year
- Pre-computed ratios: margins, ROE, ROA, CapEx %, leverage
- Historical revenue CAGR
- Model building notes (linkages and checks to implement)

## Overview

This Skill creates comprehensive three-statement financial models by:
1. Extracting historical financial data from filings or yfinance
2. Building forecast drivers and assumptions
3. Creating integrated income statement, balance sheet, and cash flow statement
4. Adding valuation modules and sensitivity analysis

## Workflow

### Step 1: Fetch Historical Data

```bash
python3 scripts/fetch_data.py AAPL --years 5
```

Review the output JSON for:
- Revenue trend and CAGR
- Margin profile (gross, EBITDA, net)
- CapEx as % of revenue
- Working capital patterns
- Leverage and cash position

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

## Usage Examples

### Example 1: Build model for Apple

```
User: "Create a three-statement model for AAPL"

Step 1: python3 scripts/fetch_data.py AAPL --years 5
Step 2: Review AAPL_3statement_annual_*.json
Step 3: Build Excel with historical + 5-year projections

Output: AAPL_Financial_Model.xlsx
```

### Example 2: Quarterly model for earnings tracking

```
User: "Build quarterly model for Nvidia — last 8 quarters"

python3 scripts/fetch_data.py NVDA --quarterly --years 8

Output: NVDA_3statement_quarterly_*.json with 8 quarters
```

### Example 3: Model for Chinese company

```
User: "Build three-statement model for Moutai (sh600519)"

→ Use tencent-finance skill for CN data
→ Claude extracts annual report financials
→ Build model with China accounting standards
```

## Best Practices

- Always include circular reference breaking (average debt balance method)
- Build error checks (Balance Sheet must balance, Cash reconciliation)
- Document assumptions clearly
- Use conservative, base, and optimistic scenarios
- Validate against sellside consensus estimates

## Key Outputs

1. **Historical Data JSON** (from script)
2. **Integrated 3-Statement Model** (Excel)
3. **Valuation Summary** (DCF, Comps, Precedents)
4. **Sensitivity Analysis Dashboard**
5. **Assumptions Documentation**

## Related Skills

- `dcf-modeling` - For detailed DCF valuation
- `comparables-analysis` - For peer benchmarking
- `earnings-analysis` - For quarterly updates to the model
