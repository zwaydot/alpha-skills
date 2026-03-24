---
name: competitive-dynamics
description: "Rank competitors within an industry by relative competitive position. Evaluates which company in a peer group has the strongest competitive trajectory by comparing revenue growth, profitability, efficiency, margin momentum, and R&D investment on a rank-based scoring system. Use this skill whenever the user wants to: compare companies competing in the same industry, determine which competitor is gaining or losing ground, analyze competitive positioning within a peer set, decide which company in a sector is most worth investing in, or understand revenue share dynamics among rivals. Do NOT use for single-company quality analysis (business-quality), stock screening across sectors (stock-screener), or valuation/DCF analysis."
---

# competitive-dynamics

**What it does:** Ranks competitors within an industry by relative competitive position. Answers: "Among these rivals, which has the strongest competitive trajectory and why?"

**Who it's for:** Investors who have identified an attractive industry and need to pick the best company within it — typically after stock-screener identifies the sector, before business-quality deep-dives on the winner.

## Methodology: Relative Competitive Positioning

### Why Relative, Not Absolute

business-quality asks "Is this a good business?" using absolute thresholds (ROE >20% = excellent). competitive-dynamics asks "Which competitor is strongest?" using peer-relative ranking. A 15% gross margin is terrible in software but dominant in grocery retail. Absolute thresholds fail across industries; rank-based scoring works universally.

This follows the core insight from Porter's competitive strategy: competitive advantage is meaningful only relative to rivals in the same industry. A company's financials matter not in isolation, but in comparison to the peer set it competes against.

### 5 Competitive Dimensions

| # | Dimension | Weight | What it measures | Higher = Better |
|---|-----------|--------|------------------|-----------------|
| 1 | Revenue Growth | 30% | Revenue CAGR over available years | Yes |
| 2 | Profitability | 25% | Average gross margin % | Yes |
| 3 | Efficiency | 20% | Average net margin % | Yes |
| 4 | Margin Momentum | 15% | Gross margin change (first→last year, pp) | Yes |
| 5 | R&D Investment | 10% | Average R&D as % of revenue | Yes |

**Why these weights:** Revenue growth dominates because gaining share is the clearest signal of competitive strength. Profitability and efficiency capture current positioning. Margin momentum reveals trajectory — a company with expanding margins is strengthening its position. R&D investment is a leading indicator of future competitiveness, weighted lower because R&D-to-revenue varies enormously by industry.

### Rank-Based Scoring

All scoring is relative within the peer set:
- Rank 1 = score 100, Rank N = score 0
- Formula: `score = (N - rank) / (N - 1) × 100`
- Composite score = weighted average of dimension scores

This means scores are only meaningful within the specific comparison. A score of 80 means "dominant in this peer set," not "objectively excellent."

### Additional Context (Not Scored)

- **Revenue Share**: Each company's latest revenue as % of peer set total — shows market concentration
- **ROIC**: Displayed in annual data for capital efficiency context, but not scored (to avoid overlap with business-quality)

### Academic Backing

| Dimension | Research | Why it matters |
|-----------|----------|----------------|
| Revenue Growth | BCG growth-share matrix; McKinsey *Strategy Beyond the Hockey Stick* | Revenue growth relative to peers is the strongest predictor of long-term value creation |
| Gross Margin | Novy-Marx (2013) gross profitability factor | Pricing power relative to industry peers signals competitive advantage |
| Net Margin | DuPont decomposition — profit margin component | Operating leverage and cost discipline vs. peers |
| Margin Momentum | Porter's dynamic competitive analysis | Expanding margins signal strengthening position; contracting margins signal competitive pressure |
| R&D Intensity | Lev & Sougiannis (1996) — R&D capitalization and stock returns | R&D spending relative to peers predicts future competitive position, especially in technology |

### Limitations

- **Peer set selection matters**: Results depend entirely on which companies are compared. Comparing NVDA to AMD/INTC/QCOM produces different insights than comparing NVDA to MSFT/GOOGL/AMZN.
- **Rank compression with few peers**: With only 2 companies, one always scores 100 and the other 0. Minimum 3 peers recommended for meaningful differentiation.
- **R&D not universal**: Consumer staples, utilities, financials often have negligible R&D. The dimension still scores (whoever spends most ranks highest) but carries less analytical weight.
- **Trailing data**: All metrics are historical. A company gaining share today may be doing so unprofitably.

## Script Usage

```bash
python3 scripts/fetch_data.py NVDA AMD INTC QCOM       # Semiconductor peers
python3 scripts/fetch_data.py MSFT GOOGL META           # Big tech comparison
python3 scripts/fetch_data.py 0700.HK 9988.HK 9618.HK  # HK internet peers
```

All tickers are equal peers — no target/peer distinction. Order does not matter.

**Output**: Markdown report (stdout) with ranking table, per-company annual data, and dimension scores. JSON data on stderr.

## After Running the Script

The script answers "who ranks where." Your job is to answer "why, and what does it mean for investment."

### 1. State the Ranking and Key Differentiators

Lead with the competitive ranking, then explain what separates the leader from the pack:

- "NVDA dominates this peer set (score 90): #1 in growth (100% CAGR), profitability (69% GM), and efficiency (44% NM). Only weak spot is R&D intensity (15% vs INTC's 29%), but that's a denominator effect — NVDA's revenue grew 8x while R&D grew 2x."
- "QCOM (48) and AMD (52) are closely matched — AMD leads on growth trajectory while QCOM leads on current profitability. Different competitive strategies, both viable."

### 2. Analyze Competitive Dynamics

Go beyond static rankings to explain the competitive forces at work:

- **Who is gaining share?** Use revenue share + growth rate. "NVDA grew from 15% to 62% of peer-set revenue in 4 years — a historic share gain driven by AI training demand."
- **Who is losing ground?** Negative growth + shrinking share. "INTC's revenue declined 5.7% CAGR while peers grew — structural share loss in both datacenter and client computing."
- **Where is the competitive intensity?** Margin convergence or divergence. "AMD's margins are expanding toward QCOM's level — competitive gap is narrowing in mobile/embedded."

### 3. Identify Moat Sources Behind the Numbers

The script shows the numbers; explain the competitive advantages that produce them:

- Use Pat Dorsey's 5 moat sources: network effects, switching costs, intangible assets (patents, brands), cost advantage, efficient scale
- "NVDA's 69% gross margin comes from CUDA ecosystem lock-in (switching costs) + architectural lead in AI training (intangible assets). AMD's lower margin reflects its challenger position — must price below NVDA to win design wins."

### 4. Assess Competitive Trajectory

Use margin momentum and growth trends to make a directional call:

- **Strengthening**: Growing faster than peers + expanding margins. "NVDA is pulling away — growth accelerating AND margins expanding. Classic winner-take-most dynamics."
- **Stable**: Holding position relative to peers. "QCOM maintains steady 56% GM and 22% NM — defensive moat in mobile baseband, but not gaining ground."
- **Weakening**: Losing share + contracting margins. "INTC's gross margin fell from 43% to 35% while losing revenue — competitive position is deteriorating across segments."

### 5. Investment Implications

Connect competitive position to investment decision:

- Which companies deserve deeper research? Recommend `business-quality` for absolute quality assessment on top-ranked competitors.
- Which companies to eliminate? Bottom-ranked with weakening trajectory can often be screened out.
- What are the risks to the ranking? Identify catalysts that could reshuffle positioning (new product cycles, regulatory changes, M&A).
