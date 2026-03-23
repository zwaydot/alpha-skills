#!/usr/bin/env python3
"""
competitive-dynamics: Compare target company vs. peers on revenue growth and margin trends.

Usage:
    python3 scripts/fetch_data.py NVDA AMD,INTC,QCOM
    python3 scripts/fetch_data.py AAPL MSFT,GOOGL,META
    python3 scripts/fetch_data.py NVDA AMD,INTC > result.json
"""

import sys
import json
from datetime import datetime

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"ERROR: Missing dependency — {e}. Run: pip install yfinance pandas numpy")
    sys.exit(1)


def safe_float(val, default=None):
    try:
        v = float(val)
        if pd.isna(v) or not np.isfinite(v):
            return default
        return round(v, 4)
    except Exception:
        return default


def fetch_company_data(ticker_sym: str) -> dict:
    """Fetch 3-year annual revenue, gross profit, net income for a ticker."""
    t = yf.Ticker(ticker_sym)
    info = t.info
    name = info.get("longName") or info.get("shortName", ticker_sym)

    try:
        fin = t.financials  # annual, columns descending by date
    except Exception as e:
        return {"ticker": ticker_sym, "name": name, "error": str(e)}

    if fin is None or fin.empty:
        return {"ticker": ticker_sym, "name": name, "error": "No financials available"}

    cols = fin.columns[:3]  # last 3 years

    annual = {}
    for col in cols:
        year = str(col.year) if hasattr(col, "year") else str(col)[:4]
        rev = safe_float(fin.loc["Total Revenue", col]) if "Total Revenue" in fin.index else None
        gp = safe_float(fin.loc["Gross Profit", col]) if "Gross Profit" in fin.index else None
        ni = safe_float(fin.loc["Net Income", col]) if "Net Income" in fin.index else None
        rd = None
        for rd_key in ["Research And Development", "Research Development"]:
            if rd_key in fin.index:
                rd = safe_float(fin.loc[rd_key, col])
                break

        annual[year] = {
            "revenue": rev,
            "gross_profit": gp,
            "net_income": ni,
            "rd_expense": rd,
            "gross_margin_pct": round(gp / rev * 100, 2) if gp and rev and rev != 0 else None,
            "net_margin_pct": round(ni / rev * 100, 2) if ni and rev and rev != 0 else None,
            "rd_intensity_pct": round(rd / rev * 100, 2) if rd and rev and rev != 0 else None,
        }

    # Compute revenue CAGR
    sorted_years = sorted(annual.keys())
    revenues = [annual[y]["revenue"] for y in sorted_years if annual[y].get("revenue")]
    rev_cagr = None
    if len(revenues) >= 2:
        try:
            n = len(revenues) - 1
            rev_cagr = round(((revenues[-1] / revenues[0]) ** (1 / n) - 1) * 100, 2)
        except Exception:
            pass

    # Gross margin trend
    gm_vals = [annual[y]["gross_margin_pct"] for y in sorted_years if annual[y].get("gross_margin_pct") is not None]
    nm_vals = [annual[y]["net_margin_pct"] for y in sorted_years if annual[y].get("net_margin_pct") is not None]

    if len(gm_vals) >= 2:
        gm_trend = "improving" if gm_vals[-1] > gm_vals[0] else "stable" if gm_vals[-1] == gm_vals[0] else "declining"
    else:
        gm_trend = "unknown"
    if len(nm_vals) >= 2:
        nm_trend = "improving" if nm_vals[-1] > nm_vals[0] else "stable" if nm_vals[-1] == nm_vals[0] else "declining"
    else:
        nm_trend = "unknown"

    avg_gross_margin = round(sum(gm_vals) / len(gm_vals), 2) if gm_vals else None
    avg_net_margin = round(sum(nm_vals) / len(nm_vals), 2) if nm_vals else None
    avg_rd_intensity = None
    rd_vals = [annual[y]["rd_intensity_pct"] for y in sorted_years if annual[y].get("rd_intensity_pct") is not None]
    if rd_vals:
        avg_rd_intensity = round(sum(rd_vals) / len(rd_vals), 2)

    return {
        "ticker": ticker_sym.upper(),
        "name": name,
        "annual_data": annual,
        "summary": {
            "revenue_cagr_3y_pct": rev_cagr,
            "avg_gross_margin_pct": avg_gross_margin,
            "avg_net_margin_pct": avg_net_margin,
            "avg_rd_intensity_pct": avg_rd_intensity,
            "gross_margin_trend": gm_trend,
            "net_margin_trend": nm_trend,
        },
    }


def rank_companies(companies: list, metric_key: str, higher_is_better: bool = True) -> dict:
    """Rank companies by a summary metric. Returns {ticker: rank}."""
    scored = [(c["ticker"], c["summary"].get(metric_key)) for c in companies if c.get("summary")]
    scored = [(t, v) for t, v in scored if v is not None]
    scored.sort(key=lambda x: x[1], reverse=higher_is_better)
    return {ticker: rank + 1 for rank, (ticker, _) in enumerate(scored)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fetch_data.py TARGET PEER1,PEER2,...", file=sys.stderr)
        sys.exit(1)

    target_sym = sys.argv[1].upper()
    peer_syms = [p.upper() for p in sys.argv[2].split(",")] if len(sys.argv) > 2 else []

    all_syms = [target_sym] + peer_syms
    print(f"Fetching data for: {', '.join(all_syms)}", file=sys.stderr)

    all_data = {}
    for sym in all_syms:
        print(f"  → {sym}...", file=sys.stderr)
        all_data[sym] = fetch_company_data(sym)

    companies = list(all_data.values())

    # Rankings
    rev_cagr_ranks = rank_companies(companies, "revenue_cagr_3y_pct")
    gm_ranks = rank_companies(companies, "avg_gross_margin_pct")
    nm_ranks = rank_companies(companies, "avg_net_margin_pct")

    # Competitive position (average rank)
    positions = {}
    for sym in all_syms:
        ranks = [
            rev_cagr_ranks.get(sym),
            gm_ranks.get(sym),
            nm_ranks.get(sym),
        ]
        valid_ranks = [r for r in ranks if r is not None]
        positions[sym] = round(sum(valid_ranks) / len(valid_ranks), 2) if valid_ranks else None

    # Share dynamics (who has highest revenue CAGR)
    share_leaders = sorted(
        [(sym, all_data[sym]["summary"].get("revenue_cagr_3y_pct")) for sym in all_syms if "summary" in all_data[sym]],
        key=lambda x: (x[1] or -999),
        reverse=True,
    )

    result = {
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "target": target_sym,
        "companies": all_data,
        "competitive_position": {
            sym: {"overall_avg_rank": positions.get(sym), "revenue_cagr_rank": rev_cagr_ranks.get(sym),
                  "gross_margin_rank": gm_ranks.get(sym), "net_margin_rank": nm_ranks.get(sym)}
            for sym in all_syms
        },
        "share_dynamics": {
            "revenue_growth_leaders": [{"ticker": sym, "cagr_pct": cagr} for sym, cagr in share_leaders],
            "margin_leaders": {
                "gross_margin": sorted(
                    [(sym, all_data[sym]["summary"].get("avg_gross_margin_pct")) for sym in all_syms if "summary" in all_data[sym]],
                    key=lambda x: (x[1] or -999), reverse=True
                )[0][0] if all_syms else None,
                "net_margin": sorted(
                    [(sym, all_data[sym]["summary"].get("avg_net_margin_pct")) for sym in all_syms if "summary" in all_data[sym]],
                    key=lambda x: (x[1] or -999), reverse=True
                )[0][0] if all_syms else None,
            },
        },
    }

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
