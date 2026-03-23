#!/usr/bin/env python3
"""
Comparables Analysis Calculator
Calculate valuation multiples and benchmark against peers
"""

import json
import sys
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Company:
    name: str
    ticker: str
    market_cap: float  # in millions
    enterprise_value: float  # in millions
    revenue: float  # in millions, TTM
    ebitda: float  # in millions, TTM
    net_income: float  # in millions, TTM
    book_value: float  # in millions
    shares_outstanding: float  # in millions

def calculate_multiples(company: Company) -> Dict:
    """Calculate valuation multiples for a company"""
    multiples = {}
    
    # Equity multiples
    if company.net_income and company.net_income != 0:
        multiples['P/E'] = company.market_cap / company.net_income
    if company.book_value and company.book_value != 0:
        multiples['P/B'] = company.market_cap / company.book_value
    if company.revenue and company.revenue != 0:
        multiples['P/S'] = company.market_cap / company.revenue
    
    # Enterprise multiples
    if company.ebitda and company.ebitda != 0:
        multiples['EV/EBITDA'] = company.enterprise_value / company.ebitda
    if company.revenue and company.revenue != 0:
        multiples['EV/Revenue'] = company.enterprise_value / company.revenue
    
    return multiples

def analyze_comps(target: Company, peers: List[Company]):
    """Run comparables analysis"""
    all_companies = [target] + peers
    
    results = []
    for company in all_companies:
        comps = calculate_multiples(company)
        results.append({
            'name': company.name,
            'ticker': company.ticker,
            'market_cap_m': company.market_cap,
            'ev_m': company.enterprise_value,
            'multiples': comps
        })
    
    # Calculate statistics for each multiple
    stats = {}
    for multiple in ['P/E', 'P/B', 'P/S', 'EV/EBITDA', 'EV/Revenue']:
        values = [r['multiples'].get(multiple) for r in results[1:]]  # Exclude target
        values = [v for v in values if v is not None and v > 0]
        if values:
            stats[multiple] = {
                'min': min(values),
                'max': max(values),
                'median': sorted(values)[len(values)//2],
                'mean': sum(values) / len(values)
            }
    
    # Implied valuation
    target_ev = target.enterprise_value
    target_ebitda = target.ebitda
    
    implied = {}
    if 'EV/EBITDA' in stats and target_ebitda:
        for metric in ['min', 'max', 'median', 'mean']:
            implied[f'EV_{metric}'] = stats['EV/EBITDA'][metric] * target_ebitda
    
    return {
        'companies': results,
        'statistics': stats,
        'target': {
            'name': target.name,
            'ticker': target.ticker,
            'current_ev': target_ev
        },
        'implied_valuation': implied
    }

def format_multiple(value):
    """Format multiple value"""
    if value is None:
        return 'N/A'
    return f"{value:.1f}x"

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--example':
        # Example: Tech company comparables
        target = Company(
            name="TargetCo",
            ticker="TGT",
            market_cap=10_000,
            enterprise_value=11_000,
            revenue=5_000,
            ebitda=1_250,
            net_income=800,
            book_value=4_000,
            shares_outstanding=100
        )
        
        peers = [
            Company("Peer A", "PA", 15_000, 16_000, 6_000, 1_800, 1_200, 6_000, 150),
            Company("Peer B", "PB", 8_000, 9_000, 4_000, 800, 400, 3_000, 80),
            Company("Peer C", "PC", 20_000, 21_000, 8_000, 2_400, 1_600, 8_000, 200),
            Company("Peer D", "PD", 12_000, 13_000, 5_500, 1_375, 880, 5_500, 110),
        ]
        
        result = analyze_comps(target, peers)
        
        print("=" * 80)
        print("COMPARABLES ANALYSIS")
        print("=" * 80)
        
        print(f"\nTarget: {result['target']['name']} ({result['target']['ticker']})")
        print(f"Current EV: ${result['target']['current_ev']:,.0f}M")
        
        print("\nPeer Comparison:")
        print(f"{'Company':<12} {'Ticker':<8} {'Market Cap':<12} {'EV/EBITDA':<10} {'P/E':<8} {'EV/Revenue':<10}")
        print("-" * 80)
        for c in result['companies']:
            m = c['multiples']
            print(f"{c['name']:<12} {c['ticker']:<8} ${c['market_cap_m']:>8,.0f}M   "
                  f"{format_multiple(m.get('EV/EBITDA')):<10} "
                  f"{format_multiple(m.get('P/E')):<8} "
                  f"{format_multiple(m.get('EV/Revenue')):<10}")
        
        print("\nMultiple Statistics (Peers Only):")
        print(f"{'Multiple':<12} {'Min':<10} {'Max':<10} {'Median':<10} {'Mean':<10}")
        print("-" * 60)
        for mult, stat in result['statistics'].items():
            print(f"{mult:<12} {format_multiple(stat['min']):<10} "
                  f"{format_multiple(stat['max']):<10} "
                  f"{format_multiple(stat['median']):<10} "
                  f"{format_multiple(stat['mean']):<10}")
        
        if result['implied_valuation']:
            print("\nImplied Valuation (based on peer multiples):")
            for key, val in result['implied_valuation'].items():
                print(f"  {key}: ${val:,.0f}M")
    
    else:
        print("Comparables Analysis Calculator")
        print("\nUsage:")
        print("  comps_calculator.py --example    # Run example analysis")
        print("\nTo use in code:")
        print("  from comps_calculator import Company, analyze_comps")
        print("  target = Company(...)")
        print("  peers = [Company(...), ...]")
        print("  result = analyze_comps(target, peers)")

if __name__ == '__main__':
    main()
