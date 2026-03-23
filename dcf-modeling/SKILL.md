---
name: dcf-modeling
description: Build discounted cash flow valuation models with proper WACC calculations, scenario toggles, and sensitivity tables. Supports FCFF (Free Cash Flow to Firm), FCFE (Free Cash Flow to Equity), and APV (Adjusted Present Value) approaches. Use for intrinsic valuation, M&A target valuation, and investment analysis.
---

# DCF Modeling

Create comprehensive discounted cash flow valuation models.

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
- Beta: Regression vs. market or industry average
- Equity Risk Premium: 4-6% historical

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

### Step 1: Input Financial Data

```bash
# Fetch company financials
python3 ~/.openclaw/workspace/skills/financial-services/dcf-modeling/scripts/prepare_dcf.py \
  --ticker AAPL \
  --years 5
```

### Step 2: Build WACC Assumptions

| Component | Input | Source |
|-----------|-------|--------|
| Risk-free rate | 4.2% | 10Y Treasury |
| Beta | 1.15 | Yahoo Finance |
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

## Output Format

**Excel Model** with:
- **Assumptions**: WACC, growth rates, margins
- **Projections**: 5-10 year cash flows
- **Valuation**: Enterprise value, Equity value per share
- **Sensitivities**: Data tables and tornado charts
- **Football field**: Valuation ranges

## Usage Examples

### Example 1: Apple DCF

```
User: "Build DCF for AAPL using 5-year projections"

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

Approach:
- 10-year projection (high growth)
- Gradual margin expansion
- FCFE method (no debt)
- Exit multiple terminal value

Output: High-growth DCF with scenario toggles
```

## Best Practices

- **Use mid-year convention** for discounting
- **Sanity check**: Does implied multiple make sense?
- **Cross-validate**: Compare to comps and precedent transactions
- **Scenario analysis**: Base, Bull, Bear cases
- **Circular reference handling**: Average debt balance

## Key Outputs

1. **DCF Model** (Excel)
2. **WACC Calculation** (Detailed breakdown)
3. **Sensitivity Tables**
4. **Football Field Valuation**
5. **Investment Recommendation**

## Related Skills

- `financial-modeling` - For 3-statement model
- `comparables-analysis` - For terminal multiple validation
- `initiating-coverage` - For full research report
