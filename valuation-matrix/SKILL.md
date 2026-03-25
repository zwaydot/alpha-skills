---
name: valuation-matrix
description: "Multi-method valuation framework — triangulates intrinsic value using DCF, reverse DCF, P/E, EV/EBITDA, FCF yield, and analyst consensus with sector-aware multiples. Use this skill whenever the user asks about fair value, intrinsic value, whether a stock is overvalued or undervalued, wants bear/base/bull price targets, wants to know what growth the market is pricing in, or needs a valuation opinion before buying or selling. Do NOT use for screening multiple stocks (stock-screener), business quality assessment (business-quality), or competitive comparison (competitor-analysis)."
---

# valuation-matrix

**What it does:** Triangulates a stock's fair value using 5 independent methods plus a reverse DCF insight. Answers: "What is this stock worth, and what does the market price imply?"

**Who it's for:** Investors who have identified a candidate (via screening or research) and need to determine whether the current price offers a margin of safety — typically the final quantitative step before a buy/sell decision.

## Methodology: Triangulation

No single valuation method is reliable alone. Each captures a different dimension of value:

| Method | Type | Question it answers | Weight |
|--------|------|---------------------|--------|
| DCF (5-year) | Intrinsic | What are the future cash flows worth today? | 30% |
| P/E Multiple | Relative | What do peers pay per dollar of earnings? | 20% |
| EV/EBITDA | Relative | What's the operating business worth, capital-structure neutral? | 20% |
| FCF Yield | Relative | What cash-flow yield does this investment offer? | 15% |
| Analyst Consensus | Market | What does the sell-side expect? | 15% |
| Reverse DCF | Insight | What growth rate justifies the current price? | — (not scored) |

**Why these weights:** DCF gets the highest weight because it's the only method independent of market pricing — it forces explicit assumptions about growth and risk. Multiples (P/E, EV/EBITDA) are widely used but assume the market prices comparable companies correctly. Analyst consensus is a useful sanity check but reflects sell-side bias (typically optimistic). Reverse DCF doesn't produce a fair value — it produces an insight about what the market believes.

**Adaptive weights:** If a method lacks data (e.g., banks have no EBITDA/FCF), its weight is redistributed proportionally to available methods. The script reports the actual weights applied.

### DCF: The Intrinsic Anchor

A simplified but rigorous discounted cash flow model:

1. **Base FCF**: Multi-year average free cash flow (OCF - CapEx, averaged over available years) to smooth working capital volatility
2. **Growth rate**: Analyst next-year revenue growth estimate → implied EPS growth (forward/trailing) → historical CAGR → 5% default
3. **Projection**: 5 years of FCF growth
4. **Terminal value**: Gordon growth model (perpetuity at 2.5% terminal growth)
5. **Discount rate**: WACC from CAPM (risk-free + β × 6% ERP, adjusted for debt)
6. **Fair value**: (PV of projected FCFs + PV of terminal value - net debt) / shares

Three scenarios vary growth and WACC:
- **Bear**: growth × 0.5, WACC + 2pp
- **Base**: growth as estimated, WACC as computed
- **Bull**: growth × 1.5, WACC - 1pp

**Key limitation:** Terminal value typically dominates (60-80% of total). This is inherent to all DCFs — the model is most useful for comparing scenarios, not producing a precise number.

### Reverse DCF: What Does the Market Expect?

Given the current stock price, solve backwards for the implied FCF growth rate:

```
Find g such that: DCF(FCF, g, WACC) = Current Market Cap + Net Debt
```

Then compare implied growth to:
- Analyst revenue growth estimate
- Historical revenue CAGR

This answers whether the market's expectations are reasonable. If implied growth far exceeds analyst estimates, the stock may be pricing in optimism that isn't supported by consensus. If implied growth is below historical CAGR, the market may be too pessimistic.

### Relative Methods: Sector-Aware Multiples

P/E, EV/EBITDA, and FCF Yield use sector-specific (bear, base, bull) multiple ranges defined in the script. This accounts for the fact that Technology trades at structurally higher multiples than Energy, and HK trades at a structural discount to US.

- **P/E**: Uses forward EPS when available (stocks are priced on future earnings), trailing as fallback
- **EV/EBITDA**: Capital-structure neutral — the best single multiple for cross-sector comparison (Damodaran)
- **FCF Yield**: Investor's actual cash return perspective — lower yield = higher valuation

### Aggregation

The composite fair value is a weighted average (not median) of all available methods' bear/base/bull prices. This produces smoother ranges than median and properly reflects the relative importance of each method.

### Academic Backing

| Method | Research | Key insight |
|--------|----------|-------------|
| DCF | Damodaran (2012) *Investment Valuation* | Only truly intrinsic method; forces explicit assumptions |
| Reverse DCF | Rappaport & Mauboussin (2001) *Expectations Investing* | Reframes valuation as expectations analysis |
| P/E | Liu, Nissim & Thomas (2002) — earnings-based multiples | Forward P/E is the most accurate single multiple for equity valuation |
| EV/EBITDA | Damodaran — preferred for cross-sector comparison | Removes capital structure and tax distortions |
| FCF Yield | Lev & Thiagarajan (1993) — cash flow signals | Cash-based metrics less susceptible to accounting manipulation |

### Limitations

- **DCF sensitivity**: Small changes in growth or WACC produce large changes in fair value. The bear/bull range captures this, but interpret with caution.
- **Sector multiples**: Base ranges in the script are starting points. The script auto-expands them when the stock's actual P/E or EV/EBITDA falls outside the range (×1.1 above, ×0.8 below), but the hardcoded center may still lag market regime shifts.
- **Financial sector**: Banks' OCF-CapEx "FCF" is meaningless (dominated by loan/deposit flows), so DCF and FCF Yield are excluded. Valuation relies on P/E + Analyst consensus.
- **High-growth companies**: If FCF is negative, DCF and FCF Yield are unavailable. P/E + EV/EBITDA + Analyst carry the analysis.
- **Low FCF-to-earnings conversion**: Some businesses (e.g., KO) structurally convert less earnings to FCF due to working capital intensity. FCF-based methods will give lower valuations than earnings-based ones — this is a feature, not a bug, but interpret the divergence.

## Script Usage

```bash
python3 scripts/fetch_data.py AAPL              # Single stock
python3 scripts/fetch_data.py NVDA MSFT GOOGL    # Multiple stocks
python3 scripts/fetch_data.py 0700.HK            # HK market (auto-detected)
python3 scripts/fetch_data.py 600519.SS           # CN A-share
```

**Output**: Markdown report (stdout) with fair value summary, method comparison table, reverse DCF insight, DCF assumptions, and key data. JSON data on stderr.

## After Running the Script

The script computes the numbers. Your job is to synthesize them into a valuation opinion.

### 1. Lead with the Verdict

State the composite fair value range and whether the stock is cheap, fair, or expensive:

- "AAPL trades at $220, base fair value $225 — roughly fairly valued. The bear case ($165) assumes growth slows to 4%; the bull case ($310) requires sustained 15% growth."
- "NVDA at $130 vs base fair value $180 — 38% upside. Even the bear case ($95) only requires growth to slow to half the current rate."

### 2. Explain Method Divergence

When methods disagree significantly, the divergence itself is informative:

- "DCF ($135) is well below P/E ($280) because AAPL's FCF growth (1.8% historical CAGR) is much lower than what the P/E multiple implies. This gap suggests the market is pricing in a growth re-acceleration that hasn't materialized in cash flows yet."
- "Analyst consensus ($300) is above all other methods — sell-side may be anchoring on recent momentum."

### 3. Interpret the Reverse DCF

This is the most differentiated insight. Frame it as an expectations check:

- "The market is pricing in 32% FCF growth for 5 years. Analyst estimate is 16%, historical is 2%. The implied growth is 2× analyst consensus — this is aggressive pricing."
- "Implied growth of 8% vs 15% analyst estimate — the market is skeptical. If the company delivers anywhere near consensus, there's meaningful upside."

### 4. Flag Assumptions That Matter Most

Identify which DCF assumption drives the biggest swing:

- For high-beta stocks: "WACC is 19% due to β=2.4 — a 2% change in WACC swings fair value by 40%. If you believe NVDA's beta will normalize as it matures, the base case shifts significantly higher."
- For mature companies: "Terminal value is 75% of DCF — the 2.5% perpetuity growth assumption dominates. For a company with pricing power like AAPL, this may be conservative."

### 5. Investment Implication

Connect to a decision framework:

- Recommend `business-quality` to assess whether the growth assumptions are achievable (moat durability)
- Recommend `risk-framework` to size the position appropriately
- Flag if the stock is in a valuation no-man's-land (not cheap enough to buy, not expensive enough to sell)
