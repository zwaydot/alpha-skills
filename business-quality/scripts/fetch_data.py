#!/usr/bin/env python3
"""
business-quality: Fetch 5-year ROE/ROIC/gross margin/net margin trends.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py AAPL MSFT GOOGL
    python3 scripts/fetch_data.py AAPL > aapl_quality.json
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


def compute_trend(values: list) -> dict:
    """Compute direction and approximate CAGR for a list of annual values (oldest first)."""
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return {"direction": "insufficient_data", "cagr_pct": None}

    first, last = vals[0], vals[-1]
    n = len(vals) - 1

    if first is None or first == 0:
        direction = "improving" if (last or 0) > 0 else "declining"
        return {"direction": direction, "cagr_pct": None}

    try:
        cagr = (abs(last / first) ** (1 / n) - 1) * 100 * (1 if last >= first else -1)
        cagr = round(cagr, 2)
    except Exception:
        cagr = None

    direction = "improving" if (last or 0) > (first or 0) else "declining"
    return {"direction": direction, "cagr_pct": cagr}


def score_metric(values: list, excellent_threshold: float, good_threshold: float) -> float:
    """Score a metric based on average level. Returns 0.0–1.0."""
    vals = [v for v in values if v is not None]
    if not vals:
        return 0.0
    avg = sum(vals) / len(vals)
    if avg >= excellent_threshold:
        return 1.0
    elif avg >= good_threshold:
        return 0.6
    elif avg >= good_threshold * 0.7:
        return 0.3
    return 0.0


def score_stability(values: list) -> float:
    """Score consistency (low variance = higher score). Returns 0.0–1.0."""
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return 0.5
    mean = sum(vals) / len(vals)
    if mean == 0:
        return 0.0
    cv = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5 / abs(mean)
    # CV < 0.1 = very stable (1.0), CV > 0.5 = very unstable (0.0)
    return round(max(0.0, min(1.0, 1.0 - cv * 2)), 3)


def fetch_quality(ticker_sym: str) -> dict:
    t = yf.Ticker(ticker_sym)
    info = t.info

    name = info.get("longName") or info.get("shortName", ticker_sym)

    # Get annual financials
    try:
        fin = t.financials  # income statement (annual, columns = years desc)
        bs = t.balance_sheet  # balance sheet (annual)
        cf = t.cashflow  # cash flow (annual)
    except Exception as e:
        return {"error": str(e), "ticker": ticker_sym}

    years_data = {}
    if fin is not None and not fin.empty:
        for col in fin.columns[:5]:  # up to 5 years
            year_label = str(col.year) if hasattr(col, "year") else str(col)[:4]
            years_data[year_label] = {}

        # Revenue and income
        for row_name, key in [
            ("Total Revenue", "revenue"),
            ("Gross Profit", "gross_profit"),
            ("Net Income", "net_income"),
        ]:
            if row_name in fin.index:
                for col in fin.columns[:5]:
                    year = str(col.year) if hasattr(col, "year") else str(col)[:4]
                    years_data.setdefault(year, {})[key] = safe_float(fin.loc[row_name, col])

        # Balance sheet items
        if bs is not None and not bs.empty:
            for row_name, key in [
                ("Total Equity Gross Minority Interest", "equity"),
                ("Stockholders Equity", "equity"),
                ("Total Assets", "total_assets"),
                ("Total Debt", "total_debt"),
                ("Cash And Cash Equivalents", "cash"),
            ]:
                if row_name in bs.index:
                    for col in bs.columns[:5]:
                        year = str(col.year) if hasattr(col, "year") else str(col)[:4]
                        if key == "equity" and "equity" in years_data.get(year, {}):
                            continue  # prefer first match
                        years_data.setdefault(year, {})[key] = safe_float(bs.loc[row_name, col])

        # EBIT for ROIC calculation
        for row_name in ["EBIT", "Operating Income"]:
            if row_name in fin.index:
                for col in fin.columns[:5]:
                    year = str(col.year) if hasattr(col, "year") else str(col)[:4]
                    if "ebit" not in years_data.get(year, {}):
                        years_data.setdefault(year, {})["ebit"] = safe_float(fin.loc[row_name, col])

    # Compute ratios per year
    sorted_years = sorted(years_data.keys())
    roe_series = []
    roic_series = []
    gross_margin_series = []
    net_margin_series = []
    annual_metrics = {}

    for year in sorted_years:
        d = years_data[year]
        rev = d.get("revenue")
        gp = d.get("gross_profit")
        ni = d.get("net_income")
        equity = d.get("equity")
        ebit = d.get("ebit")
        total_assets = d.get("total_assets")
        total_debt = d.get("total_debt", 0) or 0
        cash = d.get("cash", 0) or 0

        roe = round(ni / equity * 100, 2) if ni and equity and equity != 0 else None
        gross_margin = round(gp / rev * 100, 2) if gp and rev and rev != 0 else None
        net_margin = round(ni / rev * 100, 2) if ni and rev and rev != 0 else None

        # ROIC = EBIT*(1-tax) / (total_debt + equity - cash)
        tax_rate = 0.21
        nopat = ebit * (1 - tax_rate) if ebit else None
        invested_capital = (total_assets or 0) - (cash or 0) - ((total_assets or 0) - (total_debt or 0) - (equity or 0))
        roic = round(nopat / invested_capital * 100, 2) if nopat and invested_capital and invested_capital != 0 else None

        roe_series.append(roe)
        roic_series.append(roic)
        gross_margin_series.append(gross_margin)
        net_margin_series.append(net_margin)

        annual_metrics[year] = {
            "roe_pct": roe,
            "roic_pct": roic,
            "gross_margin_pct": gross_margin,
            "net_margin_pct": net_margin,
        }

    # Scoring
    roe_level_score = score_metric(roe_series, excellent_threshold=20, good_threshold=15)
    roe_stability_score = score_stability(roe_series)
    roic_level_score = score_metric(roic_series, excellent_threshold=15, good_threshold=10)
    gross_margin_score = score_metric(gross_margin_series, excellent_threshold=50, good_threshold=30)
    net_margin_score = score_metric(net_margin_series, excellent_threshold=15, good_threshold=10)

    # Margin trend bonus
    gm_trend = compute_trend(gross_margin_series)
    nm_trend = compute_trend(net_margin_series)
    margin_trend_score = (
        1.0 if gm_trend["direction"] == "improving" and nm_trend["direction"] == "improving"
        else 0.5 if gm_trend["direction"] == "improving" or nm_trend["direction"] == "improving"
        else 0.0
    )

    quality_score = round(
        (roe_level_score * 0.20
         + roe_stability_score * 0.15
         + roic_level_score * 0.20
         + gross_margin_score * 0.20
         + net_margin_score * 0.15
         + margin_trend_score * 0.10) * 100,
        1
    )

    # Moat rating
    roe_above_20_count = sum(1 for v in roe_series if v is not None and v > 20)
    if quality_score >= 75 and roe_above_20_count >= 4:
        moat_rating = "Wide Moat"
    elif quality_score >= 50:
        moat_rating = "Narrow Moat"
    else:
        moat_rating = "No Moat"

    return {
        "ticker": ticker_sym.upper(),
        "company_name": name,
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "quality_score": quality_score,
        "moat_rating": moat_rating,
        "metrics": annual_metrics,
        "trends": {
            "roe": compute_trend(roe_series),
            "roic": compute_trend(roic_series),
            "gross_margin": compute_trend(gross_margin_series),
            "net_margin": compute_trend(net_margin_series),
        },
        "scoring_detail": {
            "roe_level": round(roe_level_score * 100, 1),
            "roe_stability": round(roe_stability_score * 100, 1),
            "roic_level": round(roic_level_score * 100, 1),
            "gross_margin": round(gross_margin_score * 100, 1),
            "net_margin": round(net_margin_score * 100, 1),
            "margin_trend": round(margin_trend_score * 100, 1),
        },
    }


def main():
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL"]
    results = []

    for sym in tickers:
        print(f"Fetching {sym}...", file=sys.stderr)
        result = fetch_quality(sym)
        results.append(result)
        print(f"  → {sym}: Quality={result.get('quality_score')} | Moat={result.get('moat_rating')}", file=sys.stderr)

    output = results[0] if len(results) == 1 else results
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
