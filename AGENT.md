# alpha-skills

Investment analysis toolkit with 6 skills covering the full buy-side workflow. Each skill has a `SKILL.md` with detailed methodology and a `scripts/fetch_data.py` that fetches live market data.

## Skill Routing

Match the user's intent to the right skill. **Read the target skill's `SKILL.md` before running** — it contains methodology, output interpretation, and post-analysis instructions.

| Intent | Skill | Script Example |
|--------|-------|----------------|
| Screen/filter stocks, find candidates, rank by metrics | `stock-screener` | `python3 stock-screener/scripts/fetch_data.py --sector Technology --pe 25` |
| Compare sectors, ETFs, sector rotation, fund allocation | `sector-radar` | `python3 sector-radar/scripts/fetch_data.py XLK XLF XLE XLV XLI XLY XLP XLB XLRE XLU` |
| Assess business quality, moat, profitability durability | `business-quality` | `python3 business-quality/scripts/fetch_data.py AAPL` |
| Compare competitors within an industry | `competitor-analysis` | `python3 competitor-analysis/scripts/fetch_data.py "AAPL MSFT GOOGL"` |
| Fair value, DCF, overvalued/undervalued, price targets | `valuation-matrix` | `python3 valuation-matrix/scripts/fetch_data.py AAPL` |
| Portfolio risk, diversification, benchmark comparison | `portfolio-monitor` | `python3 portfolio-monitor/scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:50"` |

**Common ambiguities:**
- "Is AAPL cheap?" → `valuation-matrix` (single-stock valuation), not `stock-screener`
- "Which tech stocks are cheap?" → `stock-screener` (multi-stock filtering)
- "Compare AAPL vs MSFT" → `competitor-analysis` if about competitive position; `valuation-matrix` with multiple tickers if about valuation
- "Which sector should I overweight?" → `sector-radar`, not `stock-screener`

## Workflow

Skills are designed to chain together:

1. **Idea generation**: `sector-radar` → identify sectors → `stock-screener` → find candidates
2. **Deep research**: `business-quality` + `competitor-analysis` → understand the business
3. **Valuation**: `valuation-matrix` → determine fair value and margin of safety
4. **Portfolio**: `portfolio-monitor` → check fit before buying

## Supported Markets

- **US**: Use ticker directly (e.g., `AAPL`, `NVDA`)
- **HK**: Suffix `.HK` (e.g., `0700.HK`, `9988.HK`)
- **CN A-share**: Suffix `.SS` for Shanghai, `.SZ` for Shenzhen (e.g., `600519.SS`)

## Running Scripts

All scripts run from the project root:

```bash
python3 <skill>/scripts/fetch_data.py [args]
```

Scripts output a Markdown report to stdout and JSON data to stderr. After running, follow the "After Running the Script" section in the skill's `SKILL.md` to synthesize the data into analysis.