# alpha-skills

> A collection of OpenClaw skills for investment research and financial workflows.

Built for investors, analysts, and portfolio managers who want AI-powered financial analysis directly in their workflow — without switching tools.

---

## Skills

| Skill | Description |
|-------|-------------|
| [stock-analysis](./stock-analysis) | Stock & crypto analysis with 8-dimension scoring, portfolio tracking, watchlists, dividend analysis, hot scanner |
| [financial-modeling](./financial-modeling) | Three-statement financial models (income statement, balance sheet, cash flow) with scenario analysis |
| [dcf-modeling](./dcf-modeling) | DCF valuation with WACC, FCFF/FCFE/APV approaches and sensitivity tables |
| [comparables-analysis](./comparables-analysis) | Peer benchmarking with EV/Revenue, EV/EBITDA, P/E, P/B multiples |
| [competitive-landscape](./competitive-landscape) | Market positioning assessment and competitive dynamics evaluation |
| [earnings-analysis](./earnings-analysis) | Earnings update reports — beat/miss analysis, guidance review, estimate revisions |
| [initiating-coverage](./initiating-coverage) | Initiating coverage research — business model, competitive positioning, valuation |
| [due-diligence](./due-diligence) | Data room processing — financials, customer lists, contract terms, risk factors |
| [pitch-deck](./pitch-deck) | Populate investment banking pitch deck templates with financial data |
| [strip-profile](./strip-profile) | Concise 1-2 page company summaries for pitch books and buyer lists |
| [tecent-finance](./tecent-finance) | Real-time stock quotes via Tencent Finance API (US, A-shares, HK) — no API key needed |
| [competitive-landscape](./competitive-landscape) | Structured competitive landscape assessments with strategic recommendations |

---

## Requirements

- [OpenClaw](https://openclaw.ai) — AI agent runtime
- Python 3.9+
- API keys as needed per skill (see individual SKILL.md files)

---

## Installation

### Install all skills

```bash
# Clone the repo
git clone https://github.com/zwaydot/alpha-skills.git

# Copy skills to your OpenClaw workspace
cp -r alpha-skills/* ~/.openclaw/workspace/skills/
```

### Install a single skill

```bash
cp -r alpha-skills/stock-analysis ~/.openclaw/workspace/skills/
```

---

## Usage

Each skill has a `SKILL.md` with detailed instructions. OpenClaw automatically reads these when you reference the skill in conversation.

**Example prompts:**

```
Analyze $AAPL with 8-dimension scoring
```

```
Build a DCF model for Tesla with base/bull/bear scenarios
```

```
Find comparable companies for a SaaS company with $50M ARR
```

```
Generate an earnings update for NVDA Q4 2025 results
```

---

## Contributing

Pull requests welcome. Each skill should include:

- `SKILL.md` — description, usage, and prompt examples
- `scripts/` — supporting Python scripts (if needed)

---

## License

MIT
