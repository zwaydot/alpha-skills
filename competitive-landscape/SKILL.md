---
name: competitive-landscape
description: Create structured competitive landscape assessments with market positioning analysis, competitive dynamics evaluation, and strategic recommendations. Use for market entry analysis, strategic planning, investor presentations, and due diligence.
---

# Competitive Landscape Analysis

Analyze competitive positioning and market dynamics.

## Overview

This Skill creates:
- Competitor identification and mapping
- Market positioning analysis
- Competitive dynamics assessment
- Strategic recommendations

## Frameworks

- **2x2 Positioning Matrix**: Price vs. Quality, or other key dimensions
- **Porter's Five Forces**: Industry structure analysis
- **Value Chain Analysis**: Competitive advantage sources
- **SWOT Analysis**: Strengths, Weaknesses, Opportunities, Threats

## Workflow

### Step 1: Competitor Identification

```bash
# Research competitors
python3 ~/.openclaw/workspace/skills/financial-services/competitive-landscape/scripts/find_competitors.py \
  --company "Company Name" \
  --industry "Industry"
```

Identify:
- **Direct competitors**: Same products/services
- **Indirect competitors**: Substitute solutions
- **Potential entrants**: Adjacent players
- **Customer alternatives**: DIY, status quo

### Step 2: Data Collection

For each competitor, gather:
- **Company overview**: Business model, key products
- **Financial metrics**: Revenue, growth, profitability
- **Market position**: Market share, geographic presence
- **Strategic positioning**: Value proposition, target segments
- **Recent developments**: M&A, product launches, partnerships

### Step 3: Positioning Mapping

Create visual positioning maps:
- **Price vs. Performance**: Value positioning
- **Feature comparison**: Product capability matrix
- **Market coverage**: Geographic presence
- **Customer segments**: B2B vs. B2C, enterprise vs. SMB

### Step 4: Competitive Dynamics

Analyze:
- **Market concentration**: CR3, CR5, HHI index
- **Competitive intensity**: Pricing pressure, R&D spending
- **Barriers to entry**: Capital requirements, regulations, brand loyalty
- **Switching costs**: Customer lock-in mechanisms

### Step 5: Strategic Recommendations

Generate insights:
- **Differentiation opportunities**: Underserved segments
- **Partnership targets**: Complementary players
- **Threat assessment**: Who to watch, disruption risks
- **Strategic positioning**: Where to compete

## Output Format

**PowerPoint/Word Report** with:
1. **Executive Summary** (1 page)
2. **Competitor Profiles** (1 page each)
3. **Positioning Maps** (2x2 matrices)
4. **Competitive Matrix** (Feature comparison table)
5. **Market Share Analysis** (Charts)
6. **Strategic Recommendations** (Action items)

## Usage Examples

### Example 1: EV Market

```
User: "Analyze EV competitive landscape in China"

Competitors: BYD, Tesla, NIO, Xpeng, Li Auto, Xiaomi Auto
Analysis:
- Market share evolution
- Price positioning ($15k-$80k)
- Tech differentiation (battery, autonomous)
- Distribution strategy (direct vs. dealers)

Output: EV China landscape report
```

### Example 2: Cloud Computing

```
User: "Map the cloud infrastructure competitive landscape"

Players: AWS, Azure, GCP, Alibaba Cloud, Huawei Cloud
Dimensions: 
- Market share
- Service breadth
- Geographic coverage
- Pricing model

Output: Cloud landscape with strategic recommendations
```

## Best Practices

- **Update quarterly** for fast-moving industries
- **Include both public and private competitors**
- **Use multiple data sources** (financial reports, news, user reviews)
- **Quantify where possible** (market share, growth rates)
- **Highlight strategic moves** (M&A, funding rounds)

## Key Outputs

1. **Competitor Database** (Excel)
2. **Positioning Maps** (Visual)
3. **Competitive Matrix** (Feature comparison)
4. **Market Share Analysis**
5. **Strategic Recommendations Report**

## Related Skills

- `comparables-analysis` - For financial benchmarking
- `initiating-coverage` - For company research reports
- `strip-profile` - For competitor company summaries
