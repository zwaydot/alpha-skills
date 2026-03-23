#!/usr/bin/env python3
"""
Company Profile Generator
Create concise 1-2 page company summaries
"""

import json
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class CompanyProfile:
    name: str
    ticker: str
    industry: str
    headquarters: str
    employees: int
    founded: int
    revenue: float  # in millions
    ebitda: float  # in millions
    market_cap: Optional[float]  # in millions
    business_description: str
    key_products: List[str]
    geographic_footprint: str
    recent_developments: List[str]

def generate_profile_html(profile: CompanyProfile) -> str:
    """Generate HTML profile"""
    margin = (profile.ebitda / profile.revenue * 100) if profile.revenue else 0
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{profile.name} - Company Profile</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #1F4E78; color: white; padding: 20px; margin: -40px -40px 30px -40px; }}
        .header h1 {{ margin: 0; }}
        .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
        .section {{ margin-bottom: 25px; }}
        .section h2 {{ color: #1F4E78; border-bottom: 2px solid #1F4E78; padding-bottom: 5px; }}
        .metrics {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .metric-box {{ background: #F2F2F2; padding: 15px; border-radius: 5px; min-width: 150px; }}
        .metric-label {{ font-size: 12px; color: #666; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #1F4E78; }}
        .highlight-box {{ background: #E6F2FF; padding: 15px; border-left: 4px solid #1F4E78; }}
        ul {{ padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{profile.name}</h1>
        <p>{profile.ticker} | {profile.industry} | {profile.headquarters}</p>
    </div>
    
    <div class="section">
        <div class="metrics">
            <div class="metric-box">
                <div class="metric-label">Revenue</div>
                <div class="metric-value">${profile.revenue:,.0f}M</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">EBITDA</div>
                <div class="metric-value">${profile.ebitda:,.0f}M</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">EBITDA Margin</div>
                <div class="metric-value">{margin:.1f}%</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Employees</div>
                <div class="metric-value">{profile.employees:,}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Business Overview</h2>
        <p>{profile.business_description}</p>
    </div>
    
    <div class="section">
        <h2>Key Products & Services</h2>
        <ul>
"""
    for product in profile.key_products:
        html += f"            <li>{product}</li>\n"
    
    html += f"""        </ul>
    </div>
    
    <div class="section">
        <h2>Geographic Footprint</h2>
        <p>{profile.geographic_footprint}</p>
    </div>
"""
    
    if profile.recent_developments:
        html += f"""
    <div class="section">
        <h2>Recent Developments</h2>
        <ul>
"""
        for dev in profile.recent_developments:
            html += f"            <li>{dev}</li>\n"
        html += """        </ul>
    </div>
"""
    
    html += f"""
    <div class="highlight-box">
        <strong>Investment Highlights</strong><br>
        • Leading position in {profile.industry}<br>
        • ${profile.revenue:,.0f}M revenue with {margin:.1f}% EBITDA margin<br>
        • Established presence with {profile.employees:,} employees worldwide<br>
        • Founded in {profile.founded} with headquarters in {profile.headquarters}
    </div>
    
    <div style="margin-top: 40px; font-size: 11px; color: #666; border-top: 1px solid #ddd; padding-top: 10px;">
        Generated on {datetime.now().strftime('%Y-%m-%d')} | For informational purposes only
    </div>
</body>
</html>
"""
    return html

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--example':
        profile = CompanyProfile(
            name="TechGrowth Inc",
            ticker="TGI",
            industry="Enterprise Software",
            headquarters="San Francisco, CA",
            employees=2500,
            founded=2010,
            revenue=500.0,
            ebitda=125.0,
            market_cap=2500.0,
            business_description="TechGrowth Inc is a leading provider of cloud-based enterprise software solutions serving mid-market and enterprise customers globally. The company's SaaS platform enables businesses to streamline operations, improve productivity, and drive digital transformation.",
            key_products=[
                "Cloud ERP Platform",
                "Business Intelligence Suite",
                "Workflow Automation Tools",
                "Analytics Dashboard"
            ],
            geographic_footprint="Operations in North America (60% of revenue), Europe (25%), and Asia-Pacific (15%). Headquarters in San Francisco with regional offices in London, Singapore, and New York.",
            recent_developments=[
                "Launched AI-powered analytics module in Q4 2025",
                "Acquired DataSync Inc for $50M in January 2026",
                "Expanded partnership with major cloud providers",
                "Achieved 120% net revenue retention rate"
            ]
        )
        
        html = generate_profile_html(profile)
        
        output_file = 'company_profile.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Generated: {output_file}")
        print(f"\nCompany: {profile.name}")
        print(f"Revenue: ${profile.revenue:,.0f}M")
        print(f"EBITDA: ${profile.ebitda:,.0f}M ({profile.ebitda/profile.revenue*100:.1f}% margin)")
        print(f"Employees: {profile.employees:,}")
    
    else:
        print("Company Profile Generator")
        print("\nUsage:")
        print("  profile_generator.py --example    # Generate example profile")
        print("\nTo use in code:")
        print("  from profile_generator import CompanyProfile, generate_profile_html")
        print("  profile = CompanyProfile(...)")
        print("  html = generate_profile_html(profile)")

if __name__ == '__main__':
    main()
