---
name: Discounted Cash Flow (DCF) modeling
description: Build discounted cash flow valuation models with proper WACC calculations, scenario toggles, and sensitivity tables. Supports FCFF (Free Cash Flow to Firm), FCFE (Free Cash Flow to Equity), and APV (Adjusted Present Value) approaches. Use for intrinsic valuation, M&A target valuation, and investment analysis.
---

# Discounted Cash Flow (DCF) Modeling

Create comprehensive discounted cash flow valuation models.

## Inputs

- **Target company**: Ticker symbol (e.g. `AAPL`) or manual financial data
- **Projection period**: 5–10 years (default: 5)
- **DCF method**: FCFF (default), FCFE, or APV
- **WACC assumptions**: Or let the script estimate from live data
- **Terminal value method**: Perpetuity growth (default) or Exit multiple
- **Scenarios**: Base / Bull / Bear growth assumptions

## Outputs

- **JSON file**: Historical financials + WACC inputs (`<TICKER>_dcf_inputs_YYYYMMDD.json`)
- **Excel Model**: Integrated projections, WACC schedule, sensitivity tables
- **Football field chart**: Valuation range across methods and scenarios

## Data Sources

- **Yahoo Finance** (via `yfinance`): Historical financials, beta, market data
- **SEC EDGAR**: Annual filings for detailed historical data
- **Manual input**: Custom growth and margin assumptions

## Example Usage

```
"Build a 5-year DCF for Apple with 8.5% WACC"
"DCF for a SaaS company growing 30% — use 10-year projection"
"What's the implied WACC if the stock is fairly valued today?"
```

## Quick Start: Fetch Historical Data

```bash
# Fetch historical financials for DCF assumptions
python3 scripts/fetch_data.py AAPL

# Specify number of years
python3 scripts/fetch_data.py MSFT --years 7 --output msft_dcf_inputs.json

# After fetching, open the JSON and fill in dcf_assumptions_template
```

**Script output includes:**
- Revenue, EBITDA, FCF for last 5 years
- CapEx %, D&A, margins per year
- Beta, market cap, net debt
- WACC component estimates (Rf, ERP, Beta → Cost of Equity)
- Revenue CAGR for calibrating growth assumptions

## Overview

This Skill builds:
- **FCFF Model**: Free Cash Flow to Firm → Enterprise Value
- **FCFE Model**: Free Cash Flow to Equity → Equity Value
- **APV Model**: Adjusted Present Value with tax shields

## Key Components

### 1. Cash Flow Projections

**FCFF Formula:**
```
FCFF = EBIT(1 - Tax Rate) + D&A - CapEx - ΔWorking Capital
```

**FCFE Formula:**
```
FCFE = Net Income + D&A - CapEx - ΔWorking Capital + Net Borrowing
```

### 2. WACC Calculation

```
WACC = (E/V × Re) + (D/V × Rd × (1 - T))

Where:
- Re = Cost of Equity (CAPM: Rf + β × ERP)
- Rd = Cost of Debt
- E/V = Equity proportion
- D/V = Debt proportion
- T = Tax rate
```

**Cost of Equity (CAPM):**
- Risk-free rate: 10-year Treasury yield
- Beta: Regression vs. market (fetched via script)
- Equity Risk Premium: ~5% historical

### 3. Terminal Value

**Perpetuity Growth Model:**
```
Terminal Value = FCFF(n) × (1 + g) / (WACC - g)
```

**Exit Multiple Method:**
```
Terminal Value = EBITDA(n) × Industry Multiple
```

## Workflow

### Step 1: Fetch Historical Data

```bash
python3 scripts/fetch_data.py AAPL --years 5
```

This outputs a JSON with revenue, EBITDA, FCF, CapEx, D&A, and WACC inputs.

### Step 2: Build WACC Assumptions

| Component | Input | Source |
|-----------|-------|--------|
| Risk-free rate | 4.2% | 10Y Treasury |
| Beta | Script-fetched | Yahoo Finance |
| Equity risk premium | 5.0% | Historical |
| Cost of debt | 4.5% | Credit rating |
| Tax rate | 21% | Effective rate |
| Target D/E | 0.3 | Industry avg |

### Step 3: Projection Period

Build 5-10 year projections:
- Revenue growth (year-by-year)
- Operating margin evolution
- CapEx and D&A
- Working capital needs

### Step 4: Terminal Value

Choose method:
- **Perpetuity growth**: g = 2-3% (GDP growth)
- **Exit multiple**: Based on trading comps

### Step 5: Calculate Enterprise Value

```
PV of Stage 1: Sum of discounted FCFF (years 1-5)
PV of Terminal Value: TV / (1 + WACC)^n
Enterprise Value = PV Stage 1 + PV Terminal Value
Equity Value = EV - Net Debt
Per Share Value = Equity Value / Shares Outstanding
```

### Step 6: Sensitivity Analysis

Create data tables:
- WACC vs. Terminal Growth Rate
- Revenue CAGR vs. EBITDA Margin
- Exit Multiple vs. WACC

## Usage Examples

### Example 1: Apple DCF

```
User: "Build DCF for AAPL using 5-year projections"

Step 1: python3 scripts/fetch_data.py AAPL
Step 2: Review AAPL_dcf_inputs_*.json — fill in growth assumptions

Inputs:
- Revenue growth: 5%, 4%, 3%, 3%, 3%
- EBIT margin: 30%
- CapEx: 3% of sales
- WACC: 8.5%
- Terminal growth: 3%

Output:
- Implied share price: $185
- Current price: $175
- Upside: 6%
```

### Example 2: High-growth company

```
User: "DCF for a SaaS company growing 30% annually"

python3 scripts/fetch_data.py <TICKER> --years 5

Approach:
- 10-year projection (high growth)
- Gradual margin expansion
- FCFE method (no debt)
- Exit multiple terminal value
```

## Best Practices

- **Use mid-year convention** for discounting
- **Sanity check**: Does implied multiple make sense?
- **Cross-validate**: Compare to comps and precedent transactions
- **Scenario analysis**: Base, Bull, Bear cases
- **Circular reference handling**: Average debt balance

## Key Outputs

1. **Historical Data JSON** (from script)
2. **DCF Model** (Excel)
3. **WACC Calculation** (Detailed breakdown)
4. **Sensitivity Tables**
5. **Football Field Valuation**

## Related Skills

- `financial-modeling` - For 3-statement model
- `comparables-analysis` - For terminal multiple validation
- `initiating-coverage` - For full research report
