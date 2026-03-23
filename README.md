# alpha-skills

> OpenClaw skills for buy-side investment decision-making.

A structured toolkit covering the full investment workflow — from screening candidates to monitoring your portfolio.

---

## Skills

| Stage | Skill | Description |
|-------|-------|-------------|
| 找标的 | [stock-screener](./stock-screener) | Multi-factor screening across any universe (S&P 500, Nasdaq 100, sector ETFs, or custom tickers) — filters by P/E, ROE, revenue growth, market cap |
| 找标的 | [sector-radar](./sector-radar) | Sector rotation scanner — ranks 10 industry ETFs by momentum, valuation, and relative strength |
| 研究公司 | [business-quality](./business-quality) | Moat assessment — 5-year ROE/ROIC/margin trends scored into a business quality rating |
| 研究公司 | [competitive-dynamics](./competitive-dynamics) | Competitive landscape — revenue CAGR and margin comparison across a peer group |
| 估值 | [valuation-matrix](./valuation-matrix) | Multi-method valuation — DCF + EV/EBITDA + P/FCF + P/E cross-check → implied price range |
| 决策支持 | [risk-framework](./risk-framework) | Systematic risk scoring — beta, volatility, leverage, liquidity → overall risk rating |
| 持仓管理 | [portfolio-monitor](./portfolio-monitor) | Portfolio analytics — correlation matrix, volatility contributions, concentration risk |
| 持仓管理 | [catalyst-calendar](./catalyst-calendar) | 90-day catalyst calendar — earnings dates, dividend dates, key events |

---

## Requirements

- [OpenClaw](https://openclaw.ai) — AI agent runtime
- Python 3.9+
- `yfinance` — `pip install yfinance`

---

## Installation

```bash
git clone https://github.com/zwaydot/alpha-skills.git
cp -r alpha-skills/* ~/.openclaw/workspace/skills/
```

Or install a single skill:

```bash
cp -r alpha-skills/valuation-matrix ~/.openclaw/workspace/skills/
```

---

## Usage

Each skill has a `SKILL.md` with detailed instructions. OpenClaw reads these automatically.

Data scripts run independently — fetch real market data before analysis:

```bash
# Screen for quality stocks
python3 stock-screener/scripts/fetch_data.py                    # S&P 500 default
python3 stock-screener/scripts/fetch_data.py --index nasdaq100  # Nasdaq 100
python3 stock-screener/scripts/fetch_data.py --sector XLK       # Tech sector
python3 stock-screener/scripts/fetch_data.py --tickers AAPL MSFT NVDA  # Custom

# Assess business quality
python3 business-quality/scripts/fetch_data.py AAPL

# Run valuation
python3 valuation-matrix/scripts/fetch_data.py AAPL

# Monitor a portfolio
python3 portfolio-monitor/scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:30 GOOGL:20"

# Check upcoming catalysts
python3 catalyst-calendar/scripts/fetch_data.py "AAPL MSFT NVDA TSLA"
```

**Example prompts:**

```
Run the stock screener and identify the top 10 quality candidates from today's results
```

```
Assess the business quality of AAPL — focus on moat durability and capital allocation
```

```
Build a valuation matrix for NVDA and tell me where it sits vs. fair value
```

```
Score the risks for TSLA across fundamental, valuation, execution, and macro dimensions
```

```
Analyze my portfolio: AAPL:25 MSFT:25 NVDA:30 AMZN:20
```

---

## Best Practices

**Be specific about your requirements**
State the ticker, time period, peer set, or portfolio weights upfront. The more precise the input, the more actionable the output.

**Provide context**
Share your investment thesis or what you're trying to decide. "Should I buy more AAPL" gives very different context than "compare AAPL's moat to MSFT."

**Review and refine**
Treat first outputs as structured drafts. Ask follow-up questions — tighten assumptions, challenge the risk score, pressure-test the valuation.

**Chain skills together**
The full workflow is more powerful than any single skill:
- `sector-radar` → identify a sector → `stock-screener` → find candidates
- `business-quality` + `competitive-dynamics` → research → `valuation-matrix` → price it
- `risk-framework` → size the position → `portfolio-monitor` → track it

---

## Contributing

Pull requests welcome. Each skill should include:
- `SKILL.md` — description, inputs, outputs, example prompts
- `scripts/fetch_data.py` — standalone data fetching script

---

## License

MIT
