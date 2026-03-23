#!/usr/bin/env python3
"""
DCF Valuation Calculator
Supports FCFF (Firm) and FCFE (Equity) approaches
"""

import json
import sys
from dataclasses import dataclass
from typing import List

@dataclass
class DCFInputs:
    revenue: float
    growth_rates: List[float]  # 5-year growth rates
    ebitda_margin: float
    depreciation_pct: float
    capex_pct: float
    nwc_pct: float
    tax_rate: float
    wacc: float
    terminal_growth: float
    net_debt: float
    shares_outstanding: float

def calculate_wacc(cost_of_equity, cost_of_debt, debt_ratio, tax_rate):
    """Calculate WACC"""
    equity_ratio = 1 - debt_ratio
    after_tax_debt = cost_of_debt * (1 - tax_rate)
    return equity_ratio * cost_of_equity + debt_ratio * after_tax_debt

def calculate_cost_of_equity(risk_free, beta, market_premium):
    """CAPM calculation"""
    return risk_free + beta * market_premium

def dcf_valuation(inputs: DCFInputs):
    """Run DCF valuation"""
    
    # Project cash flows
    fcffs = []
    revenues = [inputs.revenue]
    
    for i, growth in enumerate(inputs.growth_rates):
        revenue = revenues[-1] * (1 + growth)
        revenues.append(revenue)
        
        ebitda = revenue * inputs.ebitda_margin
        depreciation = revenue * inputs.depreciation_pct
        ebit = ebitda - depreciation
        tax = ebit * inputs.tax_rate if ebit > 0 else 0
        nopat = ebit - tax
        
        capex = revenue * inputs.capex_pct
        nwc_change = (revenue - revenues[-2]) * inputs.nwc_pct if i > 0 else 0
        
        fcff = nopat + depreciation - capex - nwc_change
        fcffs.append({
            'year': i + 1,
            'revenue': revenue,
            'ebitda': ebitda,
            'nopat': nopat,
            'fcff': fcff
        })
    
    # Calculate PV of explicit period
    pv_explicit = sum(
        f['fcff'] / ((1 + inputs.wacc) ** (i + 1))
        for i, f in enumerate(fcffs)
    )
    
    # Terminal value (perpetuity growth)
    terminal_fcff = fcffs[-1]['fcff'] * (1 + inputs.terminal_growth)
    terminal_value = terminal_fcff / (inputs.wacc - inputs.terminal_growth)
    pv_terminal = terminal_value / ((1 + inputs.wacc) ** len(inputs.growth_rates))
    
    # Enterprise and Equity value
    enterprise_value = pv_explicit + pv_terminal
    equity_value = enterprise_value - inputs.net_debt
    value_per_share = equity_value / inputs.shares_outstanding if inputs.shares_outstanding > 0 else 0
    
    return {
        'projections': fcffs,
        'pv_explicit_period': pv_explicit,
        'terminal_value': terminal_value,
        'pv_terminal': pv_terminal,
        'enterprise_value': enterprise_value,
        'net_debt': inputs.net_debt,
        'equity_value': equity_value,
        'shares_outstanding': inputs.shares_outstanding,
        'value_per_share': value_per_share,
        'wacc_used': inputs.wacc,
        'terminal_growth': inputs.terminal_growth
    }

def format_currency(value):
    """Format large numbers"""
    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.0f}"

def main():
    # Example usage
    if len(sys.argv) > 1 and sys.argv[1] == '--example':
        inputs = DCFInputs(
            revenue=1_000_000_000,  # $1B
            growth_rates=[0.15, 0.12, 0.10, 0.08, 0.06],
            ebitda_margin=0.25,
            depreciation_pct=0.05,
            capex_pct=0.07,
            nwc_pct=0.02,
            tax_rate=0.21,
            wacc=0.10,
            terminal_growth=0.03,
            net_debt=200_000_000,
            shares_outstanding=100_000_000
        )
        
        result = dcf_valuation(inputs)
        
        print("=" * 60)
        print("DCF VALUATION RESULTS")
        print("=" * 60)
        print(f"\nProjections:")
        for p in result['projections']:
            print(f"  Year {p['year']}: Revenue {format_currency(p['revenue'])}, "
                  f"FCFF {format_currency(p['fcff'])}")
        
        print(f"\nValuation Summary:")
        print(f"  PV of Explicit Period (5 years): {format_currency(result['pv_explicit_period'])}")
        print(f"  Terminal Value: {format_currency(result['terminal_value'])}")
        print(f"  PV of Terminal Value: {format_currency(result['pv_terminal'])}")
        print(f"  Enterprise Value: {format_currency(result['enterprise_value'])}")
        print(f"  Less: Net Debt: {format_currency(result['net_debt'])}")
        print(f"  Equity Value: {format_currency(result['equity_value'])}")
        print(f"  Value Per Share: ${result['value_per_share']:.2f}")
        print(f"\nAssumptions:")
        print(f"  WACC: {result['wacc_used']:.1%}")
        print(f"  Terminal Growth: {result['terminal_growth']:.1%}")
        
    else:
        print("DCF Valuation Calculator")
        print("\nUsage:")
        print("  dcf_calculator.py --example    # Run example valuation")
        print("\nTo use in code:")
        print("  from dcf_calculator import DCFInputs, dcf_valuation")
        print("  inputs = DCFInputs(...)")
        print("  result = dcf_valuation(inputs)")

if __name__ == '__main__':
    main()
