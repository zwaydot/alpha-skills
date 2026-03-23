# alpha-skills

> OpenClaw skills for buy-side investment decision-making.

A structured toolkit covering the full investment workflow — from screening candidates to monitoring your portfolio. Supports **US and HK markets**, with an extensible architecture for adding new markets.

---

## Skills

| Stage | Skill | Description |
|-------|-------|-------------|
| Idea Generation | [stock-screener](./stock-screener) | Two-phase server-side screening — filters by sector, P/E, ROE, market cap across US/HK/custom tickers, then scores and ranks candidates |
| Idea Generation | [sector-radar](./sector-radar) | Sector rotation scanner — ranks 10 industry ETFs by momentum, valuation, and relative strength |
| Deep Research | [business-quality](./business-quality) | Moat assessment — 5-year ROE/ROIC/margin trends scored into a business quality rating |
| Deep Research | [competitive-dynamics](./competitive-dynamics) | Competitive landscape — revenue CAGR and margin comparison across a peer group |
| Valuation | [valuation-matrix](./valuation-matrix) | Multi-method valuation — FCF Yield + EV/EBITDA + P/E (sector-aware multiples) + analyst consensus → implied price range |
| Decision Support | [risk-framework](./risk-framework) | Systematic risk scoring — beta, volatility, leverage, liquidity → overall risk rating |
| Portfolio Management | [portfolio-monitor](./portfolio-monitor) | Portfolio analytics — correlation matrix, volatility contributions, concentration risk |
| Portfolio Management | [catalyst-calendar](./catalyst-calendar) | 90-day catalyst calendar — earnings dates, dividend dates, key events |

---

## Supported Markets

| Market | Indices | Sector Radar | Valuation | Notes |
|--------|---------|-------------|-----------|-------|
| 🇺🇸 US | S&P 500, Nasdaq 100, Russell 2000 | 10 SPDR ETFs | Sector-aware multiples | Full support |
| 🇭🇰 HK | Hang Seng, HSTECH | 6 HK ETFs | HK-discount multiples | Full support |
| 🇨🇳 CN | — | — | A-share multiples | Ticker support (`600519.SS`) |
| Others | — | — | US defaults | Any yfinance ticker works |

To add a new market: update `lib/market.py` with tax rate, risk-free rate, and sector multiples.

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
python3 stock-screener/scripts/fetch_data.py --sector Technology --pe 25        # US tech, PE<25
python3 stock-screener/scripts/fetch_data.py --sector Technology --industry Semiconductors  # Sub-industry
python3 stock-screener/scripts/fetch_data.py --index hstech                     # Hang Seng Tech
python3 stock-screener/scripts/fetch_data.py --region hk --sector Technology    # HK tech
python3 stock-screener/scripts/fetch_data.py --tickers AAPL MSFT NVDA --pe 40 --roe 10     # Custom list
python3 stock-screener/scripts/fetch_data.py --sector Technology --pe 0 --roe 0 --top 50   # No filters

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
Find US tech stocks with PE under 25 and strong profitability — what are the best picks?
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
