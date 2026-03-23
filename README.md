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

## Best Practices

**Be specific about your requirements**
Clearly state the company name, analysis type, and any specific parameters. For example, instead of "analyze this company," try "build a DCF model for Apple using a 10% WACC with 5-year projections and a terminal growth rate of 2.5%."

**Provide context**
Share relevant details upfront — industry, geography, time period, or the specific angle you care about. The more context you give, the more targeted the output. Attach source documents (10-Ks, CIMs, earnings transcripts) directly when available.

**Review and refine**
Treat the first output as a strong draft, not a final deliverable. After the skill generates output, ask for adjustments — tighten assumptions, change the peer set, reframe the investment thesis. Iteration is fast and cheap.

**Leverage multiple skills together**
Many workflows benefit from chaining skills. For example:
- Use `initiating-coverage` to build the research thesis → `dcf-modeling` for valuation → `comparables-analysis` to benchmark the multiple
- Use `due-diligence` to extract financials from a CIM → `financial-modeling` to build the full three-statement model
- Use `earnings-analysis` after results → update your existing `dcf-modeling` model with revised estimates

---

## Contributing

Pull requests welcome. Each skill should include:

- `SKILL.md` — description, usage, and prompt examples
- `scripts/` — supporting Python scripts (if needed)

---

## License

MIT
