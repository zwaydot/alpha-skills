#!/usr/bin/env python3
"""
valuation-matrix: Fetch FCF/EBITDA/EPS/price/analyst targets for multi-method valuation.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py AAPL MSFT GOOGL
    python3 scripts/fetch_data.py NVDA > nvda_valuation.json
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


def fetch_valuation_data(ticker_sym: str) -> dict:
    t = yf.Ticker(ticker_sym)
    info = t.info

    name = info.get("longName") or info.get("shortName", ticker_sym)
    current_price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    market_cap = safe_float(info.get("marketCap"))
    ev = safe_float(info.get("enterpriseValue"))
    shares_outstanding = safe_float(info.get("sharesOutstanding"))
    total_debt = safe_float(info.get("totalDebt", 0))
    cash = safe_float(info.get("totalCash", 0))

    # Analyst targets
    target_mean = safe_float(info.get("targetMeanPrice"))
    target_median = safe_float(info.get("targetMedianPrice"))
    target_high = safe_float(info.get("targetHighPrice"))
    target_low = safe_float(info.get("targetLowPrice"))

    # EPS
    eps_ttm = safe_float(info.get("trailingEps"))
    eps_forward = safe_float(info.get("forwardEps"))

    # P/E
    pe_trailing = safe_float(info.get("trailingPE"))
    pe_forward = safe_float(info.get("forwardPE"))

    # FCF from cashflow statement
    fcf = None
    try:
        cf = t.cashflow
        if cf is not None and not cf.empty:
            # Try most recent year
            col = cf.columns[0]
            ocf = None
            capex = None
            for key in ["Operating Cash Flow", "Total Cash From Operating Activities"]:
                if key in cf.index:
                    ocf = safe_float(cf.loc[key, col])
                    break
            for key in ["Capital Expenditure", "Capital Expenditures"]:
                if key in cf.index:
                    capex = safe_float(cf.loc[key, col])
                    break
            if ocf is not None and capex is not None:
                fcf = ocf + capex  # capex is usually negative
    except Exception:
        pass

    # EBITDA
    ebitda = safe_float(info.get("ebitda"))

    # If EBITDA not in info, try to compute
    if ebitda is None:
        try:
            fin = t.financials
            if fin is not None and not fin.empty:
                col = fin.columns[0]
                ebit = None
                da = None
                for key in ["EBIT", "Operating Income"]:
                    if key in fin.index:
                        ebit = safe_float(fin.loc[key, col])
                        break
                for key in ["Reconciled Depreciation", "Depreciation And Amortization"]:
                    if key in fin.index:
                        da = safe_float(fin.loc[key, col])
                        break
                if ebit and da:
                    ebitda = round(ebit + abs(da), 0)
        except Exception:
            pass

    # FCF per share
    fcf_per_share = round(fcf / shares_outstanding, 4) if fcf and shares_outstanding else None

    # ── Valuation Methods ──────────────────────────────────────────────────────
    valuation_methods = {}

    # 1. FCF Yield method (target: 4–6% FCF yield → price = FCF/share / yield)
    if fcf_per_share and current_price:
        fcf_yield_bear = round(fcf_per_share / 0.06, 2)  # 6% yield = cheapest
        fcf_yield_base = round(fcf_per_share / 0.05, 2)  # 5% yield = fair
        fcf_yield_bull = round(fcf_per_share / 0.04, 2)  # 4% yield = premium
        valuation_methods["fcf_yield"] = {
            "fcf_per_share": fcf_per_share,
            "bear_price": fcf_yield_bear,
            "base_price": fcf_yield_base,
            "bull_price": fcf_yield_bull,
            "method": "FCF/share divided by target yield (4–6%)",
        }

    # 2. EV/EBITDA method
    if ebitda and shares_outstanding and total_debt is not None and cash is not None:
        net_debt = (total_debt or 0) - (cash or 0)
        # Equity value = EBITDA × multiple - net_debt
        ev_base = ebitda * 14  # 14x EBITDA = base
        ev_bear = ebitda * 10
        ev_bull = ebitda * 18
        eq_bear = (ev_bear - net_debt) / shares_outstanding
        eq_base = (ev_base - net_debt) / shares_outstanding
        eq_bull = (ev_bull - net_debt) / shares_outstanding
        valuation_methods["ev_ebitda"] = {
            "ebitda": ebitda,
            "bear_price": round(eq_bear, 2),
            "base_price": round(eq_base, 2),
            "bull_price": round(eq_bull, 2),
            "method": "EV/EBITDA multiple range 10–18x",
        }

    # 3. P/E multiple method
    eps = eps_ttm or eps_forward
    if eps and eps > 0:
        pe_bear = round(eps * 15, 2)  # 15x
        pe_base = round(eps * 20, 2)  # 20x
        pe_bull = round(eps * 25, 2)  # 25x
        valuation_methods["pe_multiple"] = {
            "eps": eps,
            "eps_type": "ttm" if eps_ttm else "forward",
            "bear_price": pe_bear,
            "base_price": pe_base,
            "bull_price": pe_bull,
            "method": "EPS × P/E multiple range 15–25x",
        }

    # 4. Analyst consensus
    if target_median or target_mean:
        target = target_median or target_mean
        valuation_methods["analyst_consensus"] = {
            "target_median": target_median,
            "target_mean": target_mean,
            "target_high": target_high,
            "target_low": target_low,
            "bear_price": target_low,
            "base_price": target,
            "bull_price": target_high,
            "method": "Analyst 12-month price targets",
        }

    # ── Aggregate valuation range ──────────────────────────────────────────────
    bear_prices = [v["bear_price"] for v in valuation_methods.values() if v.get("bear_price")]
    base_prices = [v["base_price"] for v in valuation_methods.values() if v.get("base_price")]
    bull_prices = [v["bull_price"] for v in valuation_methods.values() if v.get("bull_price")]

    def median(lst):
        if not lst:
            return None
        s = sorted(lst)
        n = len(s)
        return round((s[n // 2 - 1] + s[n // 2]) / 2 if n % 2 == 0 else s[n // 2], 2)

    bear_target = median(bear_prices)
    base_target = median(base_prices)
    bull_target = median(bull_prices)

    upside_pct = round((base_target - current_price) / current_price * 100, 1) if base_target and current_price else None

    if upside_pct is not None:
        if upside_pct > 30:
            recommendation = "Strong Buy"
        elif upside_pct > 15:
            recommendation = "Buy"
        elif upside_pct > -15:
            recommendation = "Hold"
        elif upside_pct > -30:
            recommendation = "Reduce"
        else:
            recommendation = "Sell"
    else:
        recommendation = "Insufficient Data"

    return {
        "ticker": ticker_sym.upper(),
        "company_name": name,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "current_price": current_price,
        "market_cap": market_cap,
        "enterprise_value": ev,
        "raw_data": {
            "free_cash_flow": fcf,
            "fcf_per_share": fcf_per_share,
            "ebitda": ebitda,
            "eps_ttm": eps_ttm,
            "eps_forward": eps_forward,
            "pe_trailing": pe_trailing,
            "pe_forward": pe_forward,
            "total_debt": total_debt,
            "cash": cash,
            "shares_outstanding": shares_outstanding,
        },
        "valuation_methods": valuation_methods,
        "valuation_range": {
            "bear": bear_target,
            "base": base_target,
            "bull": bull_target,
        },
        "upside_pct": upside_pct,
        "recommendation": recommendation,
    }


def main():
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL"]
    results = []

    for sym in tickers:
        print(f"Fetching {sym}...", file=sys.stderr)
        result = fetch_valuation_data(sym)
        results.append(result)
        price = result.get("current_price", "N/A")
        base = result.get("valuation_range", {}).get("base", "N/A")
        upside = result.get("upside_pct", "N/A")
        rec = result.get("recommendation", "N/A")
        print(f"  → {sym}: Price=${price} | Base Target=${base} | Upside={upside}% | {rec}", file=sys.stderr)

    output = results[0] if len(results) == 1 else results
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
