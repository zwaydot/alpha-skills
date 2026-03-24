# alpha-skills

> OpenClaw skills for buy-side investment decision-making.

6 skills covering the full investment workflow — from screening candidates to monitoring your portfolio. Supports **US and HK markets**, with an extensible architecture for adding new markets.

---

## Skills

| Stage | Skill | Description |
|-------|-------|-------------|
| Idea Generation | [stock-screener](./stock-screener) | Two-phase screening — filters by sector, P/E, ROE, market cap across US/HK/custom tickers, then scores and ranks candidates |
| Idea Generation | [sector-radar](./sector-radar) | Sector/ETF momentum scanner — ranks any set of ETFs by momentum, trend acceleration, valuation, and volume |
| Deep Research | [business-quality](./business-quality) | Moat assessment — 5-year ROE/ROIC/margin/FCF trends scored into a Buffett-style quality rating |
| Deep Research | [competitor-analysis](./competitor-analysis) | Rank competitors by relative position — growth, profitability, efficiency, margin momentum, R&D |
| Valuation | [valuation-matrix](./valuation-matrix) | Triangulated valuation — DCF + reverse DCF + P/E + EV/EBITDA + FCF Yield + analyst consensus → fair value range |
| Portfolio Management | [portfolio-monitor](./portfolio-monitor) | Portfolio diagnostics — sector exposure, risk decomposition (Markowitz), benchmark comparison, correlation, concentration |

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
python3 stock-screener/scripts/fetch_data.py --sector Technology --pe 25
python3 stock-screener/scripts/fetch_data.py --tickers AAPL MSFT NVDA --pe 40 --roe 10
python3 stock-screener/scripts/fetch_data.py --index hstech

# Scan sector momentum
python3 sector-radar/scripts/fetch_data.py

# Assess business quality
python3 business-quality/scripts/fetch_data.py AAPL

# Compare competitors
python3 competitor-analysis/scripts/fetch_data.py "AAPL MSFT GOOGL META"

# Run valuation
python3 valuation-matrix/scripts/fetch_data.py AAPL

# Monitor a portfolio
python3 portfolio-monitor/scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:30 GOOGL:20"
python3 portfolio-monitor/scripts/fetch_data.py "0700.HK:40 9988.HK:30 1810.HK:30"
```

**Example prompts:**

```
Find US tech stocks with PE under 25 and strong profitability
```

```
Which sectors have the strongest momentum right now?
```

```
Assess the business quality of AAPL — focus on moat durability
```

```
Compare AAPL, MSFT, and GOOGL — who has the strongest competitive position?
```

```
Build a valuation matrix for NVDA — where does it sit vs fair value?
```

```
Analyze my portfolio: AAPL:25 MSFT:25 NVDA:30 AMZN:20 — is my risk balanced?
```

---

## Best Practices

**Chain skills together** — the full workflow is more powerful than any single skill:
- `sector-radar` → identify a sector → `stock-screener` → find candidates
- `business-quality` + `competitor-analysis` → research → `valuation-matrix` → price it
- `valuation-matrix` → decide → `portfolio-monitor` → track it

**Be specific** — state the ticker, peer set, or portfolio weights upfront.

**Provide context** — "Should I buy more AAPL" gives different output than "compare AAPL's moat to MSFT."

**Iterate** — treat first outputs as drafts. Challenge assumptions, tighten scenarios, pressure-test the valuation.

---

## Contributing

Pull requests welcome. Each skill should include:
- `SKILL.md` — description, inputs, outputs, example prompts
- `scripts/fetch_data.py` — standalone data fetching script

---

## License

MIT
