#!/usr/bin/env python3
"""
business-quality: 5-year profitability, cash flow quality, and moat assessment.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py AAPL MSFT GOOGL JPM
"""

import sys, json
from datetime import datetime


def detect_market(ticker: str) -> str:
    """Detect market from ticker suffix."""
    t = ticker.upper().strip()
    if t.endswith(".HK"): return "HK"
    if t.endswith(".SS") or t.endswith(".SZ"): return "CN"
    if t.endswith(".T"): return "JP"
    if t.endswith(".L"): return "UK"
    if t.endswith(".DE"): return "DE"
    if t.endswith(".PA"): return "FR"
    if t.endswith(".AS"): return "NL"
    return "US"


_TAX_RATES = {
    "US": 0.21, "HK": 0.165, "CN": 0.25, "JP": 0.30,
    "UK": 0.25, "DE": 0.30, "FR": 0.25, "NL": 0.26,
}


def get_tax_rate(market: str) -> float:
    return _TAX_RATES.get(market, 0.21)

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"ERROR: Missing dependency — {e}. Run: pip install yfinance pandas numpy", file=sys.stderr)
    sys.exit(1)


def safe_float(val, default=None):
    try:
        v = float(val)
        return round(v, 4) if pd.notna(v) and np.isfinite(v) else default
    except Exception:
        return default


def compute_trend(values):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return {"direction": "insufficient_data", "cagr_pct": None}
    first, last, n = vals[0], vals[-1], len(vals) - 1
    if not first or first == 0:
        return {"direction": "improving" if (last or 0) > 0 else "declining", "cagr_pct": None}
    try:
        cagr = round((abs(last / first) ** (1 / n) - 1) * 100 * (1 if last >= first else -1), 2)
    except Exception:
        cagr = None
    return {"direction": "improving" if (last or 0) > (first or 0) else "declining", "cagr_pct": cagr}


def score_metric(values, excellent, good):
    vals = [v for v in values if v is not None]
    if not vals:
        return None  # None = unavailable, triggers weight redistribution
    avg = sum(vals) / len(vals)
    floor = good * 0.5
    if avg >= excellent:
        return 1.0
    elif avg >= good:
        return round(0.6 + 0.4 * (avg - good) / (excellent - good), 3)
    elif avg >= floor:
        return round(0.6 * (avg - floor) / (good - floor), 3)
    return 0.0


def score_stability(values):
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    mean = sum(vals) / len(vals)
    if mean == 0:
        return 0.0
    cv = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5 / abs(mean)
    return round(max(0.0, min(1.0, 1.0 - cv * 2)), 3)


def score_inverse(values, excellent, ceiling):
    """Score where lower is better. excellent=best, ceiling=worst acceptable."""
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    avg = sum(vals) / len(vals)
    if avg <= excellent:
        return 1.0
    elif avg <= ceiling:
        return round(1.0 - (avg - excellent) / (ceiling - excellent), 3)
    return 0.0


def extract_row(df, row_names, columns):
    """Try multiple row names, return first match."""
    if df is None or df.empty:
        return {}
    for name in (row_names if isinstance(row_names, list) else [row_names]):
        if name in df.index:
            return {str(c.year) if hasattr(c, "year") else str(c)[:4]: safe_float(df.loc[name, c]) for c in columns}
    return {}


def fetch_quality(ticker_sym):
    t = yf.Ticker(ticker_sym)
    info = t.info
    market = detect_market(ticker_sym)
    tax_rate = get_tax_rate(market)
    name = info.get("longName") or info.get("shortName", ticker_sym)

    try:
        fin = t.financials
        bs = t.balance_sheet
        cf = t.cashflow
    except Exception as e:
        return {"error": str(e), "ticker": ticker_sym}

    if fin is None or fin.empty:
        return {"error": "No financial data", "ticker": ticker_sym}

    cols = fin.columns[:5]
    year_key = lambda c: str(c.year) if hasattr(c, "year") else str(c)[:4]

    # Extract raw data
    revenue = extract_row(fin, "Total Revenue", cols)
    gross_profit = extract_row(fin, "Gross Profit", cols)
    net_income = extract_row(fin, "Net Income", cols)
    ebit = extract_row(fin, ["EBIT", "Operating Income"], cols)
    equity = extract_row(bs, ["Total Equity Gross Minority Interest", "Stockholders Equity"], bs.columns[:5] if bs is not None and not bs.empty else [])
    total_debt = extract_row(bs, "Total Debt", bs.columns[:5] if bs is not None and not bs.empty else [])
    cash = extract_row(bs, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"], bs.columns[:5] if bs is not None and not bs.empty else [])
    ocf = extract_row(cf, ["Operating Cash Flow", "Total Cash From Operating Activities", "Cash Flow From Continuing Operating Activities"], cf.columns[:5] if cf is not None and not cf.empty else [])

    sorted_years = sorted(set(revenue.keys()) | set(net_income.keys()))

    # Compute ratios per year
    roe_s, roic_s, gm_s, nm_s, fcf_s, de_s, rev_s = [], [], [], [], [], [], []
    annual = {}

    for yr in sorted_years:
        rev = revenue.get(yr)
        gp = gross_profit.get(yr)
        ni = net_income.get(yr)
        eq = equity.get(yr)
        eb = ebit.get(yr)
        td = total_debt.get(yr, 0) or 0
        ca = cash.get(yr, 0) or 0
        op = ocf.get(yr)

        roe = round(ni / eq * 100, 2) if ni and eq and eq != 0 else None
        gm = round(gp / rev * 100, 2) if gp and rev and rev != 0 else None
        nm = round(ni / rev * 100, 2) if ni and rev and rev != 0 else None
        de = round(td / eq, 2) if td is not None and eq and eq > 0 else None

        nopat = eb * (1 - tax_rate) if eb else None
        ic = td + (eq or 0) - ca
        roic = round(nopat / ic * 100, 2) if nopat and ic and ic != 0 else None

        fcf_conv = round(op / ni, 2) if op and ni and ni > 0 else None
        rev_b = round(rev / 1e9, 2) if rev else None

        roe_s.append(roe); roic_s.append(roic); gm_s.append(gm); nm_s.append(nm)
        fcf_s.append(fcf_conv); de_s.append(de); rev_s.append(rev)

        annual[yr] = {"roe_pct": roe, "roic_pct": roic, "gross_margin_pct": gm,
                       "net_margin_pct": nm, "fcf_conversion": fcf_conv,
                       "debt_equity": de, "revenue_B": rev_b}

    # Scoring with dynamic weight redistribution
    dimensions = {
        "roe_level":        {"weight": 0.25, "score": score_metric(roe_s, 20, 15)},
        "roic_level":       {"weight": 0.20, "score": score_metric(roic_s, 15, 10)},
        "gross_margin":     {"weight": 0.20, "score": score_metric(gm_s, 50, 30)},
        "fcf_quality":      {"weight": 0.15, "score": score_metric(fcf_s, 1.2, 1.0)},
        "stability":        {"weight": 0.10, "score": score_stability(roe_s)},
        "financial_health": {"weight": 0.10, "score": score_inverse(de_s, 0.3, 2.0)},
    }

    available = {k: v for k, v in dimensions.items() if v["score"] is not None}
    total_w = sum(v["weight"] for v in available.values()) or 1.0
    quality_score = round(sum(v["score"] * v["weight"] / total_w for v in available.values()) * 100, 1)

    # Moat rating — ratio-based, not count-based
    roe_vals = [v for v in roe_s if v is not None]
    avg_roe = sum(roe_vals) / len(roe_vals) if roe_vals else 0
    roe_above_20_ratio = sum(1 for v in roe_vals if v > 20) / len(roe_vals) if roe_vals else 0

    if quality_score >= 75 and (avg_roe >= 20 or roe_above_20_ratio >= 0.75):
        moat_rating = "Wide Moat"
    elif quality_score >= 75 and avg_roe >= 15:
        moat_rating = "Wide Moat"
    elif quality_score >= 55 or (avg_roe >= 15 and quality_score >= 40):
        moat_rating = "Narrow Moat"
    else:
        moat_rating = "No Moat"

    # Flags
    flags = []
    if any(v is not None and v > 100 for v in roe_s):
        flags.append("ROE >100% — likely distorted by share buybacks reducing equity; use ROIC for capital efficiency")
    unavailable = [k for k, v in dimensions.items() if v["score"] is None]
    if unavailable:
        flags.append(f"Metrics unavailable: {', '.join(unavailable)} — weights redistributed to available dimensions")

    # Revenue CAGR
    rev_vals = [v for v in rev_s if v is not None]
    rev_cagr = None
    if len(rev_vals) >= 2 and rev_vals[0] and rev_vals[0] > 0:
        try:
            rev_cagr = round(((rev_vals[-1] / rev_vals[0]) ** (1 / (len(rev_vals) - 1)) - 1) * 100, 2)
        except Exception:
            pass

    scoring_detail = {}
    for k, v in dimensions.items():
        actual_weight = round(v["weight"] / total_w * 100, 1) if v["score"] is not None else 0.0
        scoring_detail[k] = {
            "score": round(v["score"] * 100, 1) if v["score"] is not None else None,
            "weight_pct": actual_weight,
            "contribution": round(v["score"] * v["weight"] / total_w * 100, 1) if v["score"] is not None else 0.0,
        }

    return {
        "ticker": ticker_sym.upper(),
        "company_name": name,
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "quality_score": quality_score,
        "moat_rating": moat_rating,
        "flags": flags,
        "metrics": annual,
        "trends": {
            "roe": compute_trend(roe_s),
            "roic": compute_trend(roic_s),
            "gross_margin": compute_trend(gm_s),
            "net_margin": compute_trend(nm_s),
            "revenue_cagr_pct": rev_cagr,
        },
        "scoring_detail": scoring_detail,
    }


def format_report(results):
    """Format markdown report to stdout."""
    lines = []
    if len(results) > 1:
        lines.append("# Business Quality Comparison")
        lines.append(f"\n_Generated: {datetime.now().strftime('%Y-%m-%d')}_\n")
        lines.append("| # | Ticker | Company | Score | Moat | Avg ROE | Avg ROIC | Rev CAGR | Flags |")
        lines.append("|---|--------|---------|-------|------|---------|----------|----------|-------|")
        for i, r in enumerate(sorted(results, key=lambda x: x.get("quality_score", 0), reverse=True), 1):
            if "error" in r:
                lines.append(f"| {i} | {r['ticker']} | — | ERROR | — | — | — | — | {r['error']} |")
                continue
            roe_vals = [v["roe_pct"] for v in r["metrics"].values() if v.get("roe_pct") is not None]
            roic_vals = [v["roic_pct"] for v in r["metrics"].values() if v.get("roic_pct") is not None]
            avg_roe = f"{sum(roe_vals)/len(roe_vals):.1f}%" if roe_vals else "N/A"
            avg_roic = f"{sum(roic_vals)/len(roic_vals):.1f}%" if roic_vals else "N/A"
            rev_cagr = f"{r['trends']['revenue_cagr_pct']:+.1f}%" if r['trends'].get('revenue_cagr_pct') is not None else "N/A"
            flag_str = "⚠" if r.get("flags") else ""
            lines.append(f"| {i} | **{r['ticker']}** | {r['company_name'][:30]} | {r['quality_score']} | {r['moat_rating']} | {avg_roe} | {avg_roic} | {rev_cagr} | {flag_str} |")
        lines.append("")

    for r in results:
        if "error" in r:
            lines.append(f"## {r['ticker']} — ERROR: {r['error']}\n")
            continue

        lines.append(f"## {r['ticker']} — {r['company_name']}")
        lines.append(f"\n**Quality Score: {r['quality_score']}/100 — {r['moat_rating']}**\n")

        if r.get("flags"):
            for f in r["flags"]:
                lines.append(f"⚠ _{f}_\n")

        # Metrics table
        years = sorted(r["metrics"].keys())
        lines.append("| Year | ROE% | ROIC% | Gross Margin% | Net Margin% | FCF Conv. | D/E | Revenue ($B) |")
        lines.append("|------|------|-------|---------------|-------------|-----------|-----|-------------|")
        for yr in years:
            m = r["metrics"][yr]
            def fmt(v, suffix=""): return f"{v}{suffix}" if v is not None else "—"
            lines.append(f"| {yr} | {fmt(m['roe_pct'])} | {fmt(m['roic_pct'])} | {fmt(m['gross_margin_pct'])} | {fmt(m['net_margin_pct'])} | {fmt(m['fcf_conversion'],'x')} | {fmt(m.get('debt_equity'))} | {fmt(m['revenue_B'])} |")

        # Trends
        t = r["trends"]
        trend_parts = []
        for key, label in [("roe", "ROE"), ("roic", "ROIC"), ("gross_margin", "Gross Margin"), ("net_margin", "Net Margin")]:
            tr = t[key]
            if tr["direction"] != "insufficient_data":
                cagr = f" (CAGR {tr['cagr_pct']:+.1f}%)" if tr.get("cagr_pct") is not None else ""
                trend_parts.append(f"**{label}**: {tr['direction']}{cagr}")
        if t.get("revenue_cagr_pct") is not None:
            trend_parts.append(f"**Revenue growth**: {t['revenue_cagr_pct']:+.1f}% CAGR")
        lines.append("\n**Trends:** " + " | ".join(trend_parts))

        # Scoring breakdown
        lines.append("\n| Dimension | Score | Weight | Contribution |")
        lines.append("|-----------|-------|--------|-------------|")
        for dim, detail in r["scoring_detail"].items():
            s = f"{detail['score']:.0f}" if detail["score"] is not None else "N/A"
            w = f"{detail['weight_pct']:.0f}%" if detail["weight_pct"] else "—"
            c = f"{detail['contribution']:.1f}" if detail["contribution"] else "—"
            lines.append(f"| {dim.replace('_', ' ').title()} | {s} | {w} | {c} |")
        lines.append(f"| **Total** | | | **{r['quality_score']}** |")
        lines.append("")

    return "\n".join(lines)


def main():
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL"]
    results = []

    for sym in tickers:
        print(f"Fetching {sym}...", file=sys.stderr)
        result = fetch_quality(sym)
        results.append(result)
        score = result.get("quality_score", "ERR")
        moat = result.get("moat_rating", "ERR")
        print(f"  → {sym}: Quality={score} | Moat={moat}", file=sys.stderr)

    # Markdown report to stdout
    print(format_report(results))

    # JSON to stderr for programmatic use
    output = results[0] if len(results) == 1 else results
    print(f"\n---JSON---\n{json.dumps(output, indent=2, default=str)}", file=sys.stderr)


if __name__ == "__main__":
    main()
