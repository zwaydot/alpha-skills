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

## Eval Test Cases

Verified prompts from skill development — each tested with quantitative assertions and human review.

| Skill | Test Case | Prompt |
|-------|-----------|--------|
| stock-screener | US tech value | I want to find some US tech stocks that are not too expensive and have solid profitability. PE under 25, ROE at least 20%. What are the best picks right now? |
| stock-screener | HK tech index | Help me look at the Hang Seng Tech index — which stocks in it have good fundamentals? I care about profitability and valuation being reasonable. |
| stock-screener | Custom tickers | I'm watching these stocks: AAPL MSFT NVDA TSLA META AMZN GOOGL JPM. Which ones are actually good value right now? Filter out anything with PE over 40 or ROE below 10%. |
| stock-screener | High growth | Find me high-growth US tech stocks. I don't mind paying up for growth — PE up to 50 is fine, ROE at least 10%. |
| sector-radar | US rotation | 帮我看看美股各板块的轮动情况，哪些板块有动量优势 |
| sector-radar | Tech sub-sectors | I want to compare tech sub-sectors — semiconductors vs software vs cybersecurity vs cloud. Which has the best momentum right now? |
| sector-radar | Global markets | Compare US, Japan, Germany, and China equity markets. Where should I be overweight? |
| sector-radar | HK sectors | 港股各板块现在怎么样？科技、金融、地产、消费哪个强 |
| business-quality | AAPL moat | 苹果的护城河还在吗？最近感觉创新不行了，帮我看看它的business quality |
| business-quality | Big tech comparison | 帮我对比一下微软、谷歌和Meta的business quality，我想知道哪家的生意质量最好 |
| business-quality | Bank quality | 想买点银行股，JPM的基本面怎么样？是不是好生意？ |
| business-quality | NVDA cyclical | 英伟达质量分很高但我总觉得它是周期股，帮我分析一下到底算不算好生意 |
| competitor-analysis | Semiconductors | Compare NVDA, AMD, INTC, and QCOM — which semiconductor company has the strongest competitive position right now? |
| competitor-analysis | Cloud computing | I want to invest in cloud computing. Compare AMZN, MSFT, and GOOGL — who is winning? |
| competitor-analysis | HK internet | 港股互联网公司对比：0700.HK 腾讯、9988.HK 阿里、9618.HK 京东，哪个竞争力最强？ |
| competitor-analysis | US banks | Compare JPM, BAC, and WFC — which US bank is most competitive? |
| valuation-matrix | NVDA fair value | Build a valuation matrix for NVDA and tell me where it sits vs. fair value |
| valuation-matrix | MSFT valuation | Is Microsoft overvalued or undervalued based on its fundamentals? |
| valuation-matrix | Tencent HK | 腾讯 0700.HK 现在值多少钱？给我一个合理的估值区间 |
| valuation-matrix | JPM valuation | What's the fair value for JPM? I'm considering adding it to my portfolio. |
| portfolio-monitor | Tech concentrated | Analyze my portfolio: AAPL:30 MSFT:20 NVDA:50 — is my risk well-balanced? |
| portfolio-monitor | Diversified US | I'm building a diversified portfolio: AAPL:25 MSFT:25 JPM:25 XOM:25 — how well-diversified is it really? |
| portfolio-monitor | HK portfolio | Check my HK portfolio: 0700.HK:40 9988.HK:30 1810.HK:30 — how is it doing vs the Hang Seng? |
| portfolio-monitor | Broad balanced | Analyze my portfolio: AAPL:10 MSFT:10 GOOGL:10 AMZN:10 META:10 JPM:10 V:10 UNH:10 XOM:10 PG:10 — is this well-balanced? |
| portfolio-monitor | Cross-market | I have a mixed US/HK portfolio: AAPL:20 MSFT:20 0700.HK:30 9988.HK:15 JPM:15 — analyze the cross-market risks |
| portfolio-monitor | Defensive income | Analyze my defensive portfolio: JNJ:20 PG:20 XOM:20 VZ:20 PFE:20 — I built this for stability. Is the risk profile what I'd expect? |

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
