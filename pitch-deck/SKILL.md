---
name: pitch-deck
description: Populate investment banking pitch deck templates with data from Excel spreadsheets, CSVs, and source documents. Maps financials and company information to appropriate slides while maintaining template formatting and layout standards. Use for M&A pitches, IPO presentations, capital raising, and advisory mandates.
---

# Pitch Deck Creation

Populate investment banking pitch decks with client data.

## Overview

This Skill automates:
- Pitch deck population from source data
- Financial data mapping to slides
- Market analysis and comps insertion
- Transaction summaries
- Executive summary generation

## Input Requirements

**Source Data:**
- Company financials (Excel/CSV)
- Comparable company data
- Transaction precedents
- Management input (Word/interview notes)
- Template file (.pptx)

**Template Structure:**
- Cover slide
- Executive summary
- Company overview
- Market analysis
- Valuation
- Transaction overview
- Appendix

## Workflow

### Step 1: Template Selection

```bash
# Use standard template or custom
python3 ~/.openclaw/workspace/skills/financial-services/pitch-deck/scripts/populate_pitch.py \
  --template "standard_mna.pptx" \
  --data "company_data.xlsx" \
  --output "Client_Pitch.pptx"
```

Templates available:
- **M&A Sell-side**: For sell-side advisory
- **M&A Buy-side**: For acquisition pitches
- **IPO**: For public offering
- **Capital Raise**: For debt/equity financing
- **Strategic Review**: For general advisory

### Step 2: Data Extraction

Pull from source files:
- **Financial data**: Revenue, EBITDA, margins
- **Historical trends**: 5-year charts
- **Market data**: Comparables, indices
- **Transaction data**: Deal metrics
- **Qualitative info**: Business description, strengths

### Step 3: Slide Population

**Cover Slide:**
- Client name
- Transaction type
- Date

**Executive Summary:**
- Key metrics table
- Investment highlights
- Transaction rationale

**Company Overview:**
- Business description
- Revenue breakdown
- Geographic footprint
- Management team

**Market Analysis:**
- Industry overview
- Competitive landscape
- Growth trends
- TAM/SAM/SOM

**Valuation:**
- Trading comps
- Precedent transactions
- DCF summary
- Football field

**Transaction Overview:**
- Strategic rationale
- Process timeline
- Key considerations
- Next steps

### Step 4: Formatting & QC

- **Match template styling**: Fonts, colors, logos
- **Chart updates**: Data-linked Excel charts
- **Table formatting**: Consistent styling
- **Page numbers**: Update TOC
- **Quality check**: Review for errors

## Output Format

**PowerPoint Presentation** (.pptx):
- Professionally formatted
- Data-linked charts
- Consistent styling
- Print-ready

## Usage Examples

### Example 1: M&A Sell-side Pitch

```
User: "Create pitch deck for ABC Corp sale"

Inputs:
- ABC Corp financials (Excel)
- Industry comps (Bloomberg export)
- Management Q&A notes
- Template: sell-side M&A

Output:
- 25-slide pitch deck
- Executive summary
- Financial summary
- Valuation analysis
- Recommended process
```

### Example 2: IPO Pitch

```
User: "Populate IPO pitch for Tech Startup"

Data:
- Financial projections
- Comparable IPOs
- Management bios
- Use of proceeds

Output: IPO roadshow presentation
```

## Best Practices

- **Use consistent data**: Don't mix sources
- **Check rounding**: Numbers should sum
- **Update charts**: Refresh from source
- **Match branding**: Client/firm colors
- **Review narrative**: Story flows logically

## Key Outputs

1. **Populated Pitch Deck** (.pptx)
2. **Executive Summary** (1-page version)
3. **Backup Slides** (Appendix)
4. **Speaker Notes** (For presentation)
5. **Data Sources Document**

## Related Skills

- `ppt-template-creator` - For custom templates
- `presentation-qc` - For quality checking
- `comparables-analysis` - For valuation slides
- `strip-profile` - For company overview slides

## Note

This Skill populates existing templates. To create custom templates that match your firm's branding, use the `ppt-template-creator` Skill first.
