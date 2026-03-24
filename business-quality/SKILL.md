---
name: business-quality
description: "Buffett-style business quality analysis for individual companies. Evaluates whether a business has durable competitive advantages by examining capital efficiency (ROE, ROIC), pricing power (gross margin), earnings quality (FCF conversion), profitability consistency, and financial resilience over 5 years. Use this skill whenever the user wants to: assess a company's business quality or competitive moat, evaluate whether profitability is durable, compare quality across companies, check if a business has pricing power or earnings resilience, understand if a company is a 'good business' in the Buffett/Munger sense. Do NOT use for stock screening (stock-screener), sector allocation (sector-radar), or valuation/DCF analysis."
---

# business-quality

**What it does:** Analyzes business quality through the lens of Buffett/Munger's investment framework. Uses 5-year financial history to answer: "Is this a good business with durable competitive advantages?"

**Who it's for:** Investors doing deep research on specific companies — typically after stock-screener identifies candidates, before valuation-matrix prices them.

## Methodology: Buffett/Munger Quality Framework

Buffett and Munger evaluate a business by asking five fundamental questions. Each question has quantitative evidence the script computes, and qualitative judgment the LLM must provide.

### The 5 Business Questions

| # | Business Question | Buffett/Munger Origin | Financial Evidence (Script) | Qualitative Judgment (LLM) |
|---|------------------|----------------------|----------------------------|---------------------------|
| 1 | **Does it earn high returns on capital?** | "The best business is a royalty on the growth of others" | ROE, ROIC levels | Why — moat source (network effects, switching costs, brand, cost advantage, efficient scale) |
| 2 | **Does it have pricing power?** | "The single most important decision in evaluating a business is pricing power" | Gross margin level | Where — which products/segments, vs. competitors |
| 3 | **Are earnings real cash?** | "Owner earnings" = real FCF, not accounting artifacts | OCF / Net Income ratio | Sustainability — capex requirements, working capital dynamics |
| 4 | **Is the profitability consistent?** | "I want businesses with consistent operating history" | ROE coefficient of variation | Source — recurring revenue, contractual cash flows, or cyclical luck |
| 5 | **Can it survive adversity?** | "Only when the tide goes out do you discover who's been swimming naked" | Debt/Equity ratio | Context — industry leverage norms, debt maturity, interest coverage |

The script provides **financial evidence**. The LLM provides **business judgment**. Neither alone is sufficient.

### Academic Backing

| Dimension | Research | Why it matters |
|-----------|----------|----------------|
| ROE | DuPont framework; Buffett's letters | Primary capital efficiency — wide-moat businesses sustain ROE >20% |
| ROIC | McKinsey *Valuation*; Greenwald *Competition Demystified* | Strips leverage from ROE — true operating efficiency. ROIC > WACC = value creation |
| Gross Margin | Novy-Marx (2013) — gross profitability is the best single predictor of stock returns | Captures pricing power before SGA/R&D; most direct moat signal |
| FCF Quality | Sloan (1996) accruals anomaly — high accruals predict low future returns | OCF/NI > 1.0 means earnings are backed by real cash, not accounting |
| Stability | AQR "Quality Minus Junk" (Asness et al., 2019) — low earnings volatility is a quality signal | Consistent returns = durable advantage, not cyclical luck |
| Financial Health | Piotroski F-Score (2000) — 3 of 9 signals are leverage/liquidity | Low leverage = ability to survive downturns and invest counter-cyclically |

### Limitations

- **ROE distortion**: Buybacks reduce equity, inflating ROE (AAPL 197%). The script flags ROE >100% and ROIC compensates.
- **Cyclical businesses**: Trailing metrics score cyclicals high at peak. A semiconductor at 80% gross margin may be at cycle peak.
- **Financial sector**: Banks lack gross margin and meaningful ROIC. Dynamic weight redistribution handles this, but fewer dimensions = lower confidence.
- **Point-in-time**: All data is trailing. Forward estimates not included.

## 6-Dimension Scoring Model (0-100)

| Dimension | Weight | Excellent (100) | Good (60) | Maps to Question |
|-----------|--------|-----------------|-----------|-----------------|
| ROE Level | 25% | avg >20% | avg >15% | #1 Capital efficiency |
| ROIC Level | 20% | avg >15% | avg >10% | #1 True operating efficiency |
| Gross Margin | 20% | avg >50% | avg >30% | #2 Pricing power |
| FCF Quality | 15% | OCF/NI >1.2x | OCF/NI >1.0x | #3 Earnings reality |
| Stability | 10% | Low ROE variance | Moderate variance | #4 Consistency |
| Financial Health | 10% | D/E <0.3 | D/E <2.0 | #5 Resilience |

**Dynamic weight redistribution**: When dimensions are unavailable (banks: no gross margin, no ROIC), weights redistribute proportionally to available dimensions. JPM scored on 4 of 6 dimensions is still a fair assessment.

### Moat Rating

| Rating | Criteria |
|--------|----------|
| **Wide Moat** | Score >= 75 AND (avg ROE >= 20% OR 75%+ of years ROE >20%) |
| **Wide Moat** | Score >= 75 AND avg ROE >= 15% |
| **Narrow Moat** | Score >= 55 OR (avg ROE >= 15% AND score >= 40) |
| **No Moat** | Below all thresholds |

## Script Usage

```bash
python3 scripts/fetch_data.py AAPL              # Single company
python3 scripts/fetch_data.py AAPL MSFT JPM NVDA # Comparison
python3 scripts/fetch_data.py 0700.HK 9988.HK   # HK market
```

**Output**: Markdown report (stdout) with metrics table, trends, scoring breakdown. JSON data on stderr.

## After Running the Script

The script answers "what are the numbers." Your job is to answer the 5 business questions.

### 1. State the Verdict and Score Drivers

Lead with the quality score and moat rating, then break down which dimensions drove the score up or down:

- "MSFT scores 91.2 (Wide Moat): ROE 35% and ROIC 29% reflect exceptional capital efficiency. Gross margin 69% is the financial signature of software economics. FCF conversion 1.3x confirms earnings are real cash."
- "JPM scores 58.1 (Narrow Moat): scored on 4 of 6 dimensions (no gross margin/ROIC for banks). Strong ROE stability (CV 0.08) but financial_health scores low due to inherent banking leverage."

### 2. Answer the 5 Business Questions

This is where you add the most value. For each company, answer the questions the script cannot:

- **Q1 (Capital efficiency)** — Where does the high ROE come from? Identify the Dorsey moat source: "MSFT's 35% ROE comes from **switching costs** (M365 + Azure + Teams ecosystem lock-in) and **network effects** (developer platform)."
- **Q2 (Pricing power)** — What gives this business pricing power? "NVDA's 73% gross margin comes from near-monopoly in AI training GPUs. But AMD MI300X and custom ASICs from Google/Amazon are emerging alternatives."
- **Q3 (Earnings quality)** — Is the FCF sustainable? "AAPL's 1.2x FCF conversion reflects capital-light hardware + services model with negative working capital cycle."
- **Q4 (Consistency)** — Is the stability structural or circumstantial? "MSFT's low ROE variance reflects recurring enterprise subscriptions (80%+ of revenue). NVDA's high variance reflects GPU demand cyclicality."
- **Q5 (Resilience)** — Can it survive a downturn? "AAPL has $60B net cash — fortress balance sheet. JPM's high D/E is structural for banking but 15% ROE through credit cycles shows resilience."

Use your own knowledge for well-known companies. Only web search for unfamiliar businesses.

### 3. Assess Moat Trend

The score is a snapshot. The trend tells you where the moat is heading. Use ROIC trend and margin trend from the script as evidence, then make a directional call:

- **Widening**: ROIC and margins both improving — competitive advantage is strengthening. "AAPL's ROIC rose from 59% to 77% while gross margin expanded from 43% to 47% — Services mix shift is widening the moat."
- **Stable**: Metrics flat or mixed — moat intact but not growing. "MSFT's margins are rock-steady at 69% but ROIC is declining from 32% to 27% — moat is stable, diluted by Activision acquisition, not by competition."
- **Narrowing**: ROIC or margins declining due to competitive pressure — moat under threat. "If NVDA's gross margin falls below 65% while AMD gains share, that signals moat erosion, not just cycle normalization."

### 4. Flag Distortions

- ROE >100% from buyback-reduced equity (AAPL, SBUX)
- Cyclical peak inflating margins (semiconductors, commodities at peak)
- Missing dimensions reducing confidence (banks, pre-profit companies)

### 5. Recommend Next Steps

- `stock-screener` to find comparable companies in the same sector
- `valuation-matrix` for DCF or comparable valuation on companies with strong quality
- For comparisons, highlight which deserve deeper research vs. which to eliminate
