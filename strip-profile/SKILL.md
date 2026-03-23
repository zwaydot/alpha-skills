---
name: strip-profile
description: Create concise 1-2 page company summaries for pitch books and buyer lists with key metrics and investment highlights. Generates professional company profiles with executive summaries, business overviews, financial summaries, and supporting appendices. Use for buyer lists, pitch books, teasers, and quick reference materials.
---

# Strip Profile / Business Overview Creation

Create concise company summaries for pitch materials.

## Overview

This Skill generates:
- 1-2 page company profiles
- Executive summaries
- Business overviews
- Investment highlights
- Key metrics

**Use cases:**
- Buyer lists (M&A)
- Pitch books (investment banking)
- Teasers (confidential marketing)
- Quick reference guides

## Profile Structure

**Standard Strip Profile (1-2 pages):**

### Page 1: Overview

**Header:**
- Company name
- Industry/Sector
- Location
- Ownership (Public/Private)

**Executive Summary:**
- 3-4 bullet investment highlights
- Key financial metrics
- Strategic rationale

**Business Overview:**
- What they do (2-3 sentences)
- Products/Services
- Key customers
- Geographic footprint

**Key Metrics Table:**
| Metric | Value |
|--------|-------|
| Revenue | $XXXM |
| EBITDA | $XXM |
| EBITDA Margin | XX% |
| Employees | X,XXX |
| Years in Business | XX |

### Page 2: Details

**Financial Summary:**
- 3-5 year financial snapshot
- Growth trends
- Margin evolution

**Ownership Structure:**
- Shareholders/Cap table
- Management stake
- Recent funding/transactions

**Investment Highlights:**
- Growth opportunities
- Competitive advantages
- Market position

**Recent Developments:**
- M&A activity
- New products
- Management changes

## Workflow

### Step 1: Data Collection

```bash
# Gather company data
python3 ~/.openclaw/workspace/skills/financial-services/strip-profile/scripts/create_profile.py \
  --company "Company Name" \
  --ticker TICKER \
  --output "Company_Profile.pdf"
```

Sources:
- **Website**: Business description
- **LinkedIn**: Employees, management
- **Filings**: Financial data (public companies)
- **News**: Recent developments
- **User input**: Private company data

### Step 2: Information Extraction

Extract key facts:
- **Company basics**: Founded, HQ, Employees
- **Business model**: Revenue streams
- **Financials**: Revenue, EBITDA, Growth
- **Market**: Industry, Competition
- **Ownership**: Structure, Investors
- **Recent news**: Last 12 months

### Step 3: Draft Profile

Generate structured content:

**Executive Summary (3-4 bullets):**
- Strong market position in [segment]
- $XXXM revenue growing at XX% annually
- Proven management team with XX years experience
- Attractive margin profile (XX% EBITDA)

**Business Description:**
"[Company] is a leading provider of [products/services] serving [customer base]. The company operates [X] facilities across [geographies] and employs approximately [X,XXX] people."

**Key Metrics:**
- Revenue: $XXXM
- EBITDA: $XXM
- Employees: X,XXX
- Founded: 20XX

### Step 4: Format Output

**PDF/Word format:**
- Professional layout
- Company logo (if available)
- Clean tables
- Consistent styling

## Output Formats

### Format 1: Single Page (Teaser)
- Condensed 1-page version
- Key highlights only
- For confidential marketing

### Format 2: Two Page (Standard)
- Full profile
- Financial details
- For buyer lists

### Format 3: Slide Format
- PowerPoint 1-2 slides
- For pitch books

## Usage Examples

### Example 1: M&A Buyer List

```
User: "Create profiles for 10 potential buyers"

Targets: Strategic acquirers in tech sector

Output:
- 10 one-page profiles
- Key metrics for each
- Acquisition rationale
- Contact info (if available)

Format: PDF for distribution
```

### Example 2: Company Teaser

```
User: "Create confidential teaser for sale process"

Data:
- Company: XYZ Corp (private)
- Revenue: $50M
- EBITDA: $10M
- Industry: Software

Output:
- 1-page anonymous teaser
- Investment highlights
- Financial summary
- No company name (blind)

For: CIM distribution
```

### Example 3: Pitch Book Insert

```
User: "Create profile slide for comparable company"

Target: Comparable to client

Output:
- 1 PowerPoint slide
- Key metrics table
- Investment highlights
- Strategic fit notes

For: Pitch deck appendix
```

## Best Practices

- **Lead with value**: Investment highlights first
- **Keep it concise**: 1-2 pages max
- **Cite sources**: Footnote data sources
- **Update regularly**: Refresh quarterly
- **Customize**: Tailor for specific audiences

## Key Outputs

1. **Company Profile** (PDF/Word/PPT)
2. **Executive Summary** (1-page)
3. **Key Metrics Table**
4. **Comparison Table** (if multiple companies)
5. **Contact Sheet** (for buyer lists)

## Related Skills

- `pitch-deck` - Uses profiles in presentations
- `comparables-analysis` - For peer data
- `competitive-landscape` - For market context
- `due-diligence` - For deeper analysis

## Template Variations

| Type | Length | Use Case |
|------|--------|----------|
| Teaser | 1 page | Confidential marketing |
| Profile | 1-2 pages | Buyer lists |
| Overview | 2 pages | Pitch books |
| Slide | 1 slide | Board materials |
