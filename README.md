# alpha-skills

> A collection of OpenClaw skills for investment research and financial workflows.

Built for investors, analysts, and portfolio managers who want AI-powered financial analysis directly in their workflow — without switching tools.

Inspired by [Claude for Financial Services Skills](https://claude.com/resources/tutorials/claude-for-financial-services-skills).

---

## Skills

| Skill | Description |
|-------|-------------|
| [comparables-analysis](./comparables-analysis) | Peer benchmarking tables with valuation multiples (EV/Revenue, EV/EBITDA, P/E, P/B) that auto-refresh with live data |
| [dcf-modeling](./dcf-modeling) | DCF valuation models with WACC calculations, scenario toggles (base/bull/bear), and sensitivity tables |
| [financial-modeling](./financial-modeling) | Three-statement financial models (income statement, balance sheet, cash flow) with full linkages and scenario analysis |
| [initiating-coverage](./initiating-coverage) | Comprehensive company research — business model, competitive positioning, financial performance, and investment recommendation |
| [due-diligence](./due-diligence) | Process data room documents (CIMs, offering memos) into structured Excel data packs with financials and risk factors |
| [earnings-analysis](./earnings-analysis) | Fast-turnaround earnings update reports — beat/miss analysis, guidance review, estimate revisions, thesis impact |
| [competitive-landscape](./competitive-landscape) | Structured competitive landscape assessments with market positioning and strategic recommendations |

---

## Requirements

- [OpenClaw](https://openclaw.ai) — AI agent runtime
- Python 3.9+
- API keys as needed per skill (see individual SKILL.md files)

---

## Installation

### Install all skills

```bash
git clone https://github.com/zwaydot/alpha-skills.git
cp -r alpha-skills/* ~/.openclaw/workspace/skills/
```

### Install a single skill

```bash
cp -r alpha-skills/dcf-modeling ~/.openclaw/workspace/skills/
```

---

## Usage

Each skill has a `SKILL.md` with detailed instructions. OpenClaw automatically reads these when you reference the skill in conversation.

**Example prompts:**

```
Build a DCF model for Tesla with base/bull/bear scenarios
```

```
Find comparable companies for a SaaS company with $50M ARR
```

```
Generate an earnings update for NVDA Q4 2025 results
```

```
Create a three-statement financial model from this 10-K filing
```

---

## Contributing

Pull requests welcome. Each skill should include:

- `SKILL.md` — description, usage, and prompt examples
- `scripts/` — supporting Python scripts (if needed)

---

## License

MIT
