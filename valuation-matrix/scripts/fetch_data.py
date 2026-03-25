#!/usr/bin/env python3
"""
valuation-matrix: Multi-method valuation with triangulation.

Methods:
  1. DCF (5-year simplified) — intrinsic value anchor
  2. Reverse DCF — implied growth expectations
  3. P/E Multiple — earnings-based, forward-first
  4. EV/EBITDA Multiple — capital-structure neutral
  5. FCF Yield — cash-flow based
  6. Analyst Consensus — market wisdom

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py NVDA MSFT GOOGL
"""

import sys, json
from datetime import datetime


# ── Market configuration ────────────────────────────────────────────────────

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


MARKET_CONFIGS = {
    "US": {"tax_rate": 0.21, "risk_free_rate": 0.045, "currency": "USD", "label": "United States"},
    "HK": {"tax_rate": 0.165, "risk_free_rate": 0.04, "currency": "HKD", "label": "Hong Kong"},
    "CN": {"tax_rate": 0.25, "risk_free_rate": 0.02, "currency": "CNY", "label": "China A-share"},
    "JP": {"tax_rate": 0.30, "risk_free_rate": 0.01, "currency": "JPY", "label": "Japan"},
    "UK": {"tax_rate": 0.25, "risk_free_rate": 0.04, "currency": "GBP", "label": "United Kingdom"},
    "DE": {"tax_rate": 0.30, "risk_free_rate": 0.03, "currency": "EUR", "label": "Germany"},
    "FR": {"tax_rate": 0.25, "risk_free_rate": 0.03, "currency": "EUR", "label": "France"},
    "NL": {"tax_rate": 0.26, "risk_free_rate": 0.03, "currency": "EUR", "label": "Netherlands"},
}
_DEFAULT_CONFIG = {"tax_rate": 0.21, "risk_free_rate": 0.04, "currency": "USD", "label": "Unknown"}


def get_market_config(market: str) -> dict:
    return MARKET_CONFIGS.get(market, _DEFAULT_CONFIG)


# ── Sector-aware valuation multiples ────────────────────────────────────────
# Format: (bear, base, bull) for pe, ev_ebitda; (bull_yield, base_yield, bear_yield) for fcf_yield

_US_MULTIPLES = {
    "Technology":              {"pe": (20, 30, 40), "ev_ebitda": (15, 22, 30), "fcf_yield": (0.02, 0.03, 0.04)},
    "Communication Services":  {"pe": (15, 22, 30), "ev_ebitda": (10, 16, 22), "fcf_yield": (0.03, 0.04, 0.05)},
    "Consumer Cyclical":       {"pe": (12, 18, 25), "ev_ebitda": (8, 13, 18),  "fcf_yield": (0.04, 0.05, 0.06)},
    "Consumer Defensive":      {"pe": (15, 20, 25), "ev_ebitda": (10, 14, 18), "fcf_yield": (0.04, 0.05, 0.06)},
    "Healthcare":              {"pe": (15, 22, 30), "ev_ebitda": (10, 16, 22), "fcf_yield": (0.03, 0.04, 0.05)},
    "Financial Services":      {"pe": (8, 12, 16),  "ev_ebitda": (6, 9, 12),   "fcf_yield": (0.06, 0.08, 0.10)},
    "Industrials":             {"pe": (12, 18, 24), "ev_ebitda": (8, 12, 16),  "fcf_yield": (0.04, 0.05, 0.07)},
    "Energy":                  {"pe": (6, 10, 14),  "ev_ebitda": (4, 6, 9),    "fcf_yield": (0.06, 0.08, 0.12)},
    "Basic Materials":         {"pe": (8, 13, 18),  "ev_ebitda": (5, 8, 12),   "fcf_yield": (0.05, 0.07, 0.09)},
    "Real Estate":             {"pe": (15, 25, 35), "ev_ebitda": (12, 18, 25), "fcf_yield": (0.04, 0.05, 0.06)},
    "Utilities":               {"pe": (12, 17, 22), "ev_ebitda": (8, 11, 14),  "fcf_yield": (0.05, 0.06, 0.08)},
    "_DEFAULT":                {"pe": (15, 20, 25), "ev_ebitda": (10, 14, 18), "fcf_yield": (0.04, 0.05, 0.06)},
}

# HK trades at a structural discount to US (lower liquidity, geopolitical risk)
_HK_MULTIPLES = {
    "Technology":              {"pe": (12, 20, 28), "ev_ebitda": (8, 14, 20),  "fcf_yield": (0.03, 0.05, 0.07)},
    "Communication Services":  {"pe": (10, 16, 22), "ev_ebitda": (6, 10, 15),  "fcf_yield": (0.04, 0.06, 0.08)},
    "Consumer Cyclical":       {"pe": (8, 14, 20),  "ev_ebitda": (5, 9, 14),   "fcf_yield": (0.05, 0.07, 0.09)},
    "Consumer Defensive":      {"pe": (10, 16, 22), "ev_ebitda": (7, 11, 15),  "fcf_yield": (0.05, 0.06, 0.08)},
    "Healthcare":              {"pe": (12, 18, 25), "ev_ebitda": (8, 13, 18),  "fcf_yield": (0.04, 0.05, 0.07)},
    "Financial Services":      {"pe": (4, 7, 10),   "ev_ebitda": (4, 6, 9),    "fcf_yield": (0.08, 0.10, 0.14)},
    "Industrials":             {"pe": (6, 10, 15),  "ev_ebitda": (4, 7, 11),   "fcf_yield": (0.06, 0.08, 0.10)},
    "Energy":                  {"pe": (4, 7, 10),   "ev_ebitda": (3, 5, 7),    "fcf_yield": (0.08, 0.10, 0.14)},
    "Basic Materials":         {"pe": (5, 8, 12),   "ev_ebitda": (3, 6, 9),    "fcf_yield": (0.07, 0.09, 0.12)},
    "Real Estate":             {"pe": (5, 10, 16),  "ev_ebitda": (8, 14, 20),  "fcf_yield": (0.05, 0.07, 0.09)},
    "Utilities":               {"pe": (8, 12, 16),  "ev_ebitda": (6, 9, 12),   "fcf_yield": (0.06, 0.07, 0.09)},
    "_DEFAULT":                {"pe": (8, 14, 20),  "ev_ebitda": (6, 10, 15),  "fcf_yield": (0.05, 0.07, 0.09)},
}

# CN (A-share) — higher P/E for consumer/healthcare (scarcity premium), lower for SOE-heavy sectors
_CN_MULTIPLES = {
    "Technology":              {"pe": (15, 25, 35), "ev_ebitda": (10, 18, 25), "fcf_yield": (0.02, 0.04, 0.06)},
    "Consumer Cyclical":       {"pe": (15, 25, 35), "ev_ebitda": (10, 16, 22), "fcf_yield": (0.03, 0.04, 0.06)},
    "Consumer Defensive":      {"pe": (20, 30, 40), "ev_ebitda": (12, 18, 25), "fcf_yield": (0.02, 0.03, 0.05)},
    "Healthcare":              {"pe": (18, 28, 38), "ev_ebitda": (12, 20, 28), "fcf_yield": (0.02, 0.04, 0.06)},
    "Financial Services":      {"pe": (4, 6, 9),    "ev_ebitda": (3, 5, 8),    "fcf_yield": (0.08, 0.12, 0.16)},
    "Energy":                  {"pe": (5, 8, 12),   "ev_ebitda": (3, 5, 8),    "fcf_yield": (0.08, 0.10, 0.14)},
    "Industrials":             {"pe": (8, 14, 20),  "ev_ebitda": (5, 9, 14),   "fcf_yield": (0.05, 0.07, 0.09)},
    "Real Estate":             {"pe": (5, 8, 12),   "ev_ebitda": (4, 7, 10),   "fcf_yield": (0.06, 0.09, 0.12)},
    "Utilities":               {"pe": (10, 14, 18), "ev_ebitda": (6, 9, 12),   "fcf_yield": (0.05, 0.07, 0.09)},
    "_DEFAULT":                {"pe": (10, 18, 25), "ev_ebitda": (8, 12, 18),  "fcf_yield": (0.04, 0.06, 0.08)},
}

_MARKET_SECTOR_MULTIPLES = {
    "US": _US_MULTIPLES,
    "HK": _HK_MULTIPLES,
    "CN": _CN_MULTIPLES,
}


def get_sector_multiples(market: str, sector: str | None) -> dict:
    """Return (bear, base, bull) multiple ranges for a market+sector pair."""
    market_map = _MARKET_SECTOR_MULTIPLES.get(market, _US_MULTIPLES)
    if sector and sector in market_map:
        return market_map[sector]
    return market_map.get("_DEFAULT", _US_MULTIPLES["_DEFAULT"])

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"ERROR: Missing dependency — {e}. Run: pip install yfinance pandas numpy", file=sys.stderr)
    sys.exit(1)


ERP = 0.06  # Equity risk premium (long-run US average)
TERMINAL_GROWTH = 0.025  # 2.5% perpetuity growth
DCF_YEARS = 5

# Weights for composite fair value (adaptive — redistributed if a method is missing)
METHOD_WEIGHTS = {
    "dcf":                0.30,
    "pe_multiple":        0.20,
    "ev_ebitda":          0.20,
    "fcf_yield":          0.15,
    "analyst_consensus":  0.15,
}


def safe_float(val, default=None):
    try:
        v = float(val)
        return round(v, 4) if pd.notna(v) and np.isfinite(v) else default
    except Exception:
        return default


# ── DCF Engine ─────────────────────────────────────────────────────────────

def compute_dcf_ev(fcf, growth_rate, wacc, terminal_growth=TERMINAL_GROWTH, years=DCF_YEARS):
    """5-year DCF → enterprise value via perpetuity growth terminal value."""
    if not fcf or fcf <= 0 or wacc <= terminal_growth:
        return None
    cf = fcf
    pv_sum = 0.0
    for yr in range(1, years + 1):
        cf *= (1 + growth_rate)
        pv_sum += cf / (1 + wacc) ** yr
    # Gordon growth terminal value
    tv = cf * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_sum += tv / (1 + wacc) ** years
    return pv_sum


def dcf_fair_value(fcf, growth_rate, wacc, net_debt, shares):
    """DCF → fair value per share."""
    ev = compute_dcf_ev(fcf, growth_rate, wacc)
    if ev is None or not shares or shares <= 0:
        return None
    equity = ev - (net_debt or 0)
    return round(equity / shares, 2) if equity > 0 else None


def reverse_dcf_growth(market_cap, fcf, wacc, net_debt):
    """Binary search for implied FCF growth rate given current market cap."""
    if not all([market_cap, fcf, wacc]) or fcf <= 0:
        return None
    target_ev = market_cap + (net_debt or 0)
    if target_ev <= 0:
        return None
    low, high = -0.30, 1.00
    for _ in range(200):
        mid = (low + high) / 2
        ev = compute_dcf_ev(fcf, mid, wacc)
        if ev is None:
            return None
        if ev < target_ev:
            low = mid
        else:
            high = mid
        if abs(high - low) < 0.0001:
            break
    return round((low + high) / 2 * 100, 1)


def compute_wacc(beta, risk_free, debt_ratio, tax_rate):
    """WACC from CAPM. Cost of debt approximated as risk-free + 2%."""
    b = beta if beta and beta > 0 else 1.0
    cost_equity = risk_free + b * ERP
    cost_debt = risk_free + 0.02
    dr = debt_ratio if debt_ratio and 0 <= debt_ratio < 1 else 0
    return round(cost_equity * (1 - dr) + cost_debt * (1 - tax_rate) * dr, 4)


# ── Data Fetching ──────────────────────────────────────────────────────────

def fetch_valuation_data(ticker_sym):
    t = yf.Ticker(ticker_sym)
    info = t.info

    name = info.get("longName") or info.get("shortName", ticker_sym)
    sector = info.get("sector")
    market = detect_market(ticker_sym)
    mkt_cfg = get_market_config(market)
    risk_free = mkt_cfg["risk_free_rate"]
    tax_rate = mkt_cfg["tax_rate"]

    multiples = get_sector_multiples(market, sector)

    # ── Basic data ───────────────────────────────────────────────────────
    price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice"))
    market_cap = safe_float(info.get("marketCap"))
    shares = safe_float(info.get("sharesOutstanding"))
    total_debt = safe_float(info.get("totalDebt")) or 0
    cash = safe_float(info.get("totalCash")) or 0
    net_debt = total_debt - cash
    beta = safe_float(info.get("beta"))

    eps_ttm = safe_float(info.get("trailingEps"))
    eps_fwd = safe_float(info.get("forwardEps"))
    pe_trailing = safe_float(info.get("trailingPE"))
    pe_forward = safe_float(info.get("forwardPE"))

    ebitda = safe_float(info.get("ebitda"))
    ev_ebitda_current = safe_float(info.get("enterpriseToEbitda"))

    target_mean = safe_float(info.get("targetMeanPrice"))
    target_median = safe_float(info.get("targetMedianPrice"))
    target_high = safe_float(info.get("targetHighPrice"))
    target_low = safe_float(info.get("targetLowPrice"))

    rev_growth_trailing = safe_float(info.get("revenueGrowth"))  # trailing quarter YoY
    earn_growth_trailing = safe_float(info.get("earningsGrowth"))  # trailing quarter YoY

    # ── Forward growth estimates (preferred for DCF) ──────────────────
    # Priority: revenue_estimate next-year growth > EPS implied growth > trailing
    rev_growth_forward = None
    rev_growth_source = None

    # 1. Try analyst revenue estimate (prefer next year, then current year)
    try:
        rev_est = t.revenue_estimate
        if rev_est is not None and not rev_est.empty and "growth" in rev_est.columns:
            # Prefer annual periods: +1y (next year) > 0y (current year)
            for period in ["+1y", "0y"]:
                if period in rev_est.index:
                    val = safe_float(rev_est.loc[period, "growth"])
                    if val is not None and abs(val) < 5:  # sanity: <500%
                        rev_growth_forward = val
                        rev_growth_source = "analyst_revenue_estimate"
                        break
    except Exception:
        pass

    # 2. Fallback: implied growth from forward vs trailing EPS
    if rev_growth_forward is None and eps_fwd and eps_ttm and eps_ttm > 0:
        implied = (eps_fwd / eps_ttm) - 1
        if abs(implied) < 5:  # sanity check
            rev_growth_forward = implied
            rev_growth_source = "implied_eps_growth"

    # 3. Fallback: trailing quarterly revenue growth (what revenueGrowth actually is)
    if rev_growth_forward is None and rev_growth_trailing is not None:
        rev_growth_forward = rev_growth_trailing
        rev_growth_source = "trailing_quarterly"

    # ── FCF from cash flow statement (multi-year average to smooth WC swings) ─
    fcf = None
    is_financial = sector and sector in ("Financial Services", "Financial")
    try:
        cf = t.cashflow
        if cf is not None and not cf.empty:
            fcf_values = []
            for col in cf.columns:
                ocf, capex = None, None
                for key in ["Operating Cash Flow", "Total Cash From Operating Activities"]:
                    if key in cf.index:
                        ocf = safe_float(cf.loc[key, col]); break
                for key in ["Capital Expenditure", "Capital Expenditures"]:
                    if key in cf.index:
                        capex = safe_float(cf.loc[key, col]); break
                if ocf is not None and capex is not None:
                    fcf_values.append(ocf + capex)  # capex is negative
            if fcf_values:
                # Use average of available years (typically 4) to smooth volatility
                fcf = sum(fcf_values) / len(fcf_values)
            # For financials, OCF - CapEx is meaningless (dominated by loan/deposit flows)
            if is_financial:
                fcf = None
    except Exception:
        pass

    # ── Fallback EBITDA from financials ──────────────────────────────────
    if ebitda is None:
        try:
            fin = t.financials
            if fin is not None and not fin.empty:
                col = fin.columns[0]
                ebit, da = None, None
                for key in ["EBIT", "Operating Income"]:
                    if key in fin.index:
                        ebit = safe_float(fin.loc[key, col]); break
                for key in ["Reconciled Depreciation", "Depreciation And Amortization"]:
                    if key in fin.index:
                        da = safe_float(fin.loc[key, col]); break
                if ebit and da:
                    ebitda = round(ebit + abs(da), 0)
        except Exception:
            pass

    # ── Historical revenue CAGR ──────────────────────────────────────────
    historical_cagr = None
    try:
        fin = t.financials
        if fin is not None and not fin.empty and "Total Revenue" in fin.index:
            rev_row = fin.loc["Total Revenue"]
            vals = [(c, safe_float(rev_row[c])) for c in fin.columns
                    if safe_float(rev_row[c]) and safe_float(rev_row[c]) > 0]
            if len(vals) >= 2:
                vals.sort(key=lambda x: x[0])
                n = len(vals) - 1
                historical_cagr = round(((vals[-1][1] / vals[0][1]) ** (1 / n) - 1) * 100, 1)
    except Exception:
        pass

    # ── Growth rate for DCF ──────────────────────────────────────────────
    hist_growth = historical_cagr / 100 if historical_cagr is not None else None

    if rev_growth_forward is not None and rev_growth_forward > -0.5:
        base_growth = rev_growth_forward
        growth_source = rev_growth_source
    elif hist_growth is not None:
        base_growth = hist_growth
        growth_source = "historical_cagr"
    else:
        base_growth = 0.05
        growth_source = "default"
    base_growth = max(-0.10, min(base_growth, 0.50))

    # ── Auto-expand multiple ranges if stock trades outside them ─────────
    # Hardcoded ranges can lag market cycles; use actual multiples as evidence
    if pe_forward and pe_forward > 0:
        pe_lo, pe_mid, pe_hi = multiples["pe"]
        if pe_forward > pe_hi:
            # Market pays more than our bull case — expand range upward
            pe_hi = round(pe_forward * 1.1)
            pe_mid = round((pe_lo + pe_hi) / 2)
            multiples = {**multiples, "pe": (pe_lo, pe_mid, pe_hi)}
        elif pe_forward < pe_lo:
            pe_lo = round(pe_forward * 0.8)
            pe_mid = round((pe_lo + pe_hi) / 2)
            multiples = {**multiples, "pe": (pe_lo, pe_mid, pe_hi)}
    if ev_ebitda_current and ev_ebitda_current > 0:
        ev_lo, ev_mid, ev_hi = multiples["ev_ebitda"]
        if ev_ebitda_current > ev_hi:
            ev_hi = round(ev_ebitda_current * 1.1)
            ev_mid = round((ev_lo + ev_hi) / 2)
            multiples = {**multiples, "ev_ebitda": (ev_lo, ev_mid, ev_hi)}
        elif ev_ebitda_current < ev_lo:
            ev_lo = round(ev_ebitda_current * 0.8)
            ev_mid = round((ev_lo + ev_hi) / 2)
            multiples = {**multiples, "ev_ebitda": (ev_lo, ev_mid, ev_hi)}

    # ── WACC ─────────────────────────────────────────────────────────────
    debt_ratio = total_debt / (market_cap + total_debt) if market_cap and (market_cap + total_debt) > 0 else 0
    wacc = compute_wacc(beta, risk_free, debt_ratio, tax_rate)

    # ── Bear / Base / Bull scenarios ─────────────────────────────────────
    bear_growth = max(base_growth * 0.5, -0.05)
    bull_growth = min(base_growth * 1.5, 0.60)
    bear_wacc = wacc + 0.02
    bull_wacc = max(wacc - 0.01, TERMINAL_GROWTH + 0.01)

    fcf_per_share = round(fcf / shares, 4) if fcf and shares else None

    # ── Valuation Methods ────────────────────────────────────────────────
    methods = {}

    # 1. DCF (5-year, perpetuity terminal value)
    if fcf and fcf > 0 and shares:
        dcf_bear = dcf_fair_value(fcf, bear_growth, bear_wacc, net_debt, shares)
        dcf_base = dcf_fair_value(fcf, base_growth, wacc, net_debt, shares)
        dcf_bull = dcf_fair_value(fcf, bull_growth, bull_wacc, net_debt, shares)
        if dcf_base:
            methods["dcf"] = {
                "bear_price": dcf_bear, "base_price": dcf_base, "bull_price": dcf_bull,
                "growth_bear": round(bear_growth * 100, 1),
                "growth_base": round(base_growth * 100, 1),
                "growth_bull": round(bull_growth * 100, 1),
                "wacc_bear": round(bear_wacc * 100, 1),
                "wacc_base": round(wacc * 100, 1),
                "wacc_bull": round(bull_wacc * 100, 1),
                "method": f"5yr DCF, perpetuity TV @ {TERMINAL_GROWTH*100:.1f}% terminal growth",
            }

    # 2. P/E Multiple (forward EPS preferred)
    pe_mults = multiples["pe"]  # (bear, base, bull)
    eps = eps_fwd or eps_ttm
    eps_type = "forward" if eps_fwd else "trailing"
    if eps and eps > 0:
        methods["pe_multiple"] = {
            "bear_price": round(eps * pe_mults[0], 2),
            "base_price": round(eps * pe_mults[1], 2),
            "bull_price": round(eps * pe_mults[2], 2),
            "eps": round(eps, 2), "eps_type": eps_type,
            "multiple_range": f"{pe_mults[0]}-{pe_mults[2]}x",
            "method": f"{eps_type.title()} EPS × {pe_mults[0]}-{pe_mults[2]}x P/E ({sector or 'default'})",
        }

    # 3. EV/EBITDA
    ev_mults = multiples["ev_ebitda"]  # (bear, base, bull)
    if ebitda and ebitda > 0 and shares and shares > 0:
        for i, scenario in enumerate(["bear_price", "base_price", "bull_price"]):
            eq = (ebitda * ev_mults[i] - net_debt) / shares
            if eq <= 0:
                break
        else:
            methods["ev_ebitda"] = {
                "bear_price": round((ebitda * ev_mults[0] - net_debt) / shares, 2),
                "base_price": round((ebitda * ev_mults[1] - net_debt) / shares, 2),
                "bull_price": round((ebitda * ev_mults[2] - net_debt) / shares, 2),
                "ebitda_B": round(ebitda / 1e9, 2),
                "multiple_range": f"{ev_mults[0]}-{ev_mults[2]}x",
                "method": f"EV/EBITDA {ev_mults[0]}-{ev_mults[2]}x ({sector or 'default'})",
            }

    # 4. FCF Yield
    fcf_yields = multiples["fcf_yield"]  # (bull_yield, base_yield, bear_yield) — lower yield = higher price
    if fcf_per_share and fcf_per_share > 0:
        methods["fcf_yield"] = {
            "bear_price": round(fcf_per_share / fcf_yields[2], 2),
            "base_price": round(fcf_per_share / fcf_yields[1], 2),
            "bull_price": round(fcf_per_share / fcf_yields[0], 2),
            "fcf_per_share": fcf_per_share,
            "yield_range": f"{fcf_yields[0]*100:.0f}-{fcf_yields[2]*100:.0f}%",
            "method": f"FCF/share ÷ {fcf_yields[0]*100:.0f}-{fcf_yields[2]*100:.0f}% yield ({sector or 'default'})",
        }

    # 5. Analyst Consensus
    if target_median or target_mean:
        target = target_median or target_mean
        methods["analyst_consensus"] = {
            "bear_price": target_low, "base_price": target, "bull_price": target_high,
            "target_mean": target_mean, "target_median": target_median,
            "method": "Analyst 12-month price targets",
        }

    # ── Weighted Aggregation (adaptive weights) ──────────────────────────
    total_w = 0
    bear_w, base_w, bull_w = 0.0, 0.0, 0.0
    method_applied = {}

    for mname, weight in METHOD_WEIGHTS.items():
        m = methods.get(mname)
        if m and m.get("bear_price") and m.get("base_price") and m.get("bull_price"):
            bear_w += m["bear_price"] * weight
            base_w += m["base_price"] * weight
            bull_w += m["bull_price"] * weight
            total_w += weight
            method_applied[mname] = round(weight / 1 * 100)  # placeholder, normalized below

    # Normalize weights to actual applied methods
    for mname in method_applied:
        method_applied[mname] = round(METHOD_WEIGHTS[mname] / total_w * 100) if total_w > 0 else 0

    bear_target = round(bear_w / total_w, 2) if total_w > 0 else None
    base_target = round(base_w / total_w, 2) if total_w > 0 else None
    bull_target = round(bull_w / total_w, 2) if total_w > 0 else None

    upside = round((base_target - price) / price * 100, 1) if base_target and price else None

    if upside is not None:
        if upside > 30:    verdict = "Strong Buy"
        elif upside > 15:  verdict = "Buy"
        elif upside > -15: verdict = "Hold"
        elif upside > -30: verdict = "Reduce"
        else:              verdict = "Sell"
    else:
        verdict = "Insufficient Data"

    # ── Reverse DCF ──────────────────────────────────────────────────────
    implied_growth = None
    if fcf and fcf > 0 and market_cap:
        implied_growth = reverse_dcf_growth(market_cap, fcf, wacc, net_debt)

    reverse_dcf = None
    if implied_growth is not None:
        reverse_dcf = {
            "implied_growth_pct": implied_growth,
            "vs_forward_pct": round(rev_growth_forward * 100, 1) if rev_growth_forward is not None else None,
            "vs_historical_pct": historical_cagr,
        }

    return {
        "ticker": ticker_sym.upper(),
        "name": name,
        "sector": sector,
        "market": market,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "price": price,
        "market_cap_B": round(market_cap / 1e9, 2) if market_cap else None,
        "data": {
            "eps_ttm": eps_ttm, "eps_forward": eps_fwd,
            "pe_trailing": pe_trailing, "pe_forward": pe_forward,
            "ebitda_B": round(ebitda / 1e9, 2) if ebitda else None,
            "ev_ebitda": ev_ebitda_current,
            "fcf_B": round(fcf / 1e9, 2) if fcf else None,
            "fcf_per_share": fcf_per_share,
            "net_debt_B": round(net_debt / 1e9, 2),
            "beta": beta,
            "wacc_pct": round(wacc * 100, 1),
            "revenue_growth_forward_pct": round(rev_growth_forward * 100, 1) if rev_growth_forward is not None else None,
            "revenue_growth_trailing_pct": round(rev_growth_trailing * 100, 1) if rev_growth_trailing is not None else None,
            "earnings_growth_trailing_pct": round(earn_growth_trailing * 100, 1) if earn_growth_trailing is not None else None,
            "historical_revenue_cagr_pct": historical_cagr,
            "growth_source": growth_source,
        },
        "methods": methods,
        "method_weights_applied": method_applied,
        "fair_value": {"bear": bear_target, "base": base_target, "bull": bull_target},
        "upside_pct": upside,
        "verdict": verdict,
        "reverse_dcf": reverse_dcf,
    }


# ── Markdown Report ────────────────────────────────────────────────────────

def _fmt(v, suffix="", prefix=""):
    return f"{prefix}{v}{suffix}" if v is not None else "—"


def format_report(results):
    lines = []
    for r in results:
        tk = r["ticker"]
        lines.append(f"# Valuation Analysis — {tk}")
        lines.append(f"\n_{r['date']} | {r['name']} | {r.get('sector') or 'N/A'} | {r['market']} Market_\n")

        # ── Fair Value Summary ───────────────────────────────────────────
        fv = r["fair_value"]
        lines.append("## Fair Value Summary\n")
        lines.append("| | Bear | Base | Bull |")
        lines.append("|---|------|------|------|")
        lines.append(f"| **Composite Fair Value** | {_fmt(fv.get('bear'), prefix='$')} | {_fmt(fv.get('base'), prefix='$')} | {_fmt(fv.get('bull'), prefix='$')} |")
        lines.append(f"| **Current Price** | {_fmt(r.get('price'), prefix='$')} | | |")

        if r.get("price") and fv.get("bear") and fv.get("base") and fv.get("bull"):
            p = r["price"]
            bear_up = round((fv["bear"] - p) / p * 100, 1)
            base_up = round((fv["base"] - p) / p * 100, 1)
            bull_up = round((fv["bull"] - p) / p * 100, 1)
            lines.append(f"| **Upside / Downside** | {bear_up:+.1f}% | {base_up:+.1f}% | {bull_up:+.1f}% |")

        if r.get("upside_pct") is not None:
            lines.append(f"\n**Verdict: {r['verdict']}** — Base upside: {r['upside_pct']:+.1f}%\n")
        else:
            lines.append(f"\n**Verdict: {r['verdict']}**\n")

        # ── Method Comparison ────────────────────────────────────────────
        lines.append("## Method Comparison\n")
        lines.append("| Method | Weight | Bear | Base | Bull | Notes |")
        lines.append("|--------|--------|------|------|------|-------|")

        weights_applied = r.get("method_weights_applied", {})
        for mname, _ in METHOD_WEIGHTS.items():
            if mname not in r["methods"]:
                continue
            m = r["methods"][mname]
            w = weights_applied.get(mname, 0)

            label = {
                "dcf": "DCF (5yr)",
                "pe_multiple": f"P/E ({m.get('eps_type', '').title()})",
                "ev_ebitda": "EV/EBITDA",
                "fcf_yield": "FCF Yield",
                "analyst_consensus": "Analyst Consensus",
            }.get(mname, mname)

            if mname == "dcf":
                notes = f"g={m.get('growth_base')}%, WACC={m.get('wacc_base')}%"
            elif mname == "pe_multiple":
                notes = f"EPS ${m.get('eps')} × {m.get('multiple_range')}"
            elif mname == "ev_ebitda":
                notes = f"EBITDA ${m.get('ebitda_B')}B × {m.get('multiple_range')}"
            elif mname == "fcf_yield":
                notes = f"FCF/sh ${m.get('fcf_per_share')} ÷ {m.get('yield_range')}"
            elif mname == "analyst_consensus":
                notes = "12-month targets"
            else:
                notes = ""

            bear = _fmt(m.get("bear_price"), prefix="$")
            base = _fmt(m.get("base_price"), prefix="$")
            bull = _fmt(m.get("bull_price"), prefix="$")
            lines.append(f"| {label} | {w}% | {bear} | {base} | {bull} | {notes} |")

        # ── Reverse DCF ─────────────────────────────────────────────────
        if r.get("reverse_dcf"):
            rdcf = r["reverse_dcf"]
            lines.append("\n## Reverse DCF — Market Expectations\n")
            lines.append(f"**Implied FCF growth: {rdcf['implied_growth_pct']}% CAGR** over {DCF_YEARS} years\n")
            if rdcf.get("vs_forward_pct") is not None:
                lines.append(f"- vs. Forward growth estimate: {rdcf['vs_forward_pct']}% ({r['data'].get('growth_source', '')})")
            if rdcf.get("vs_historical_pct") is not None:
                lines.append(f"- vs. Historical revenue CAGR: {rdcf['vs_historical_pct']}%")

        # ── DCF Assumptions ──────────────────────────────────────────────
        if "dcf" in r["methods"]:
            d = r["methods"]["dcf"]
            lines.append("\n## DCF Assumptions\n")
            lines.append("| Parameter | Bear | Base | Bull |")
            lines.append("|-----------|------|------|------|")
            lines.append(f"| FCF Growth | {d['growth_bear']}% | {d['growth_base']}% | {d['growth_bull']}% |")
            lines.append(f"| WACC | {d['wacc_bear']}% | {d['wacc_base']}% | {d['wacc_bull']}% |")
            lines.append(f"| Terminal Growth | {TERMINAL_GROWTH*100:.1f}% | {TERMINAL_GROWTH*100:.1f}% | {TERMINAL_GROWTH*100:.1f}% |")

        # ── Key Data ─────────────────────────────────────────────────────
        data = r["data"]
        lines.append("\n## Key Data\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| EPS (TTM / Forward) | {_fmt(data.get('eps_ttm'), prefix='$')} / {_fmt(data.get('eps_forward'), prefix='$')} |")
        lines.append(f"| P/E (Trailing / Forward) | {_fmt(data.get('pe_trailing'), suffix='x')} / {_fmt(data.get('pe_forward'), suffix='x')} |")
        lines.append(f"| EBITDA | {_fmt(data.get('ebitda_B'), suffix='B', prefix='$')} |")
        lines.append(f"| EV/EBITDA | {_fmt(data.get('ev_ebitda'), suffix='x')} |")
        lines.append(f"| FCF | {_fmt(data.get('fcf_B'), suffix='B', prefix='$')} |")
        lines.append(f"| FCF per Share | {_fmt(data.get('fcf_per_share'), prefix='$')} |")
        lines.append(f"| Net Debt | {_fmt(data.get('net_debt_B'), suffix='B', prefix='$')} |")
        lines.append(f"| Beta | {_fmt(data.get('beta'))} |")
        lines.append(f"| WACC | {_fmt(data.get('wacc_pct'), suffix='%')} |")
        lines.append(f"| Revenue Growth (forward est.) | {_fmt(data.get('revenue_growth_forward_pct'), suffix='%')} |")
        lines.append(f"| Revenue Growth (trailing qtr) | {_fmt(data.get('revenue_growth_trailing_pct'), suffix='%')} |")
        lines.append(f"| Revenue CAGR (historical) | {_fmt(data.get('historical_revenue_cagr_pct'), suffix='%')} |")
        lines.append(f"| Growth Source (DCF) | {data.get('growth_source', 'N/A')} |")
        lines.append("")

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fetch_data.py TICKER [TICKER2 ...]", file=sys.stderr)
        sys.exit(1)

    tickers = [t.upper() for t in sys.argv[1:]]
    results = []

    for sym in tickers:
        print(f"Fetching {sym}...", file=sys.stderr)
        r = fetch_valuation_data(sym)
        results.append(r)
        fv = r["fair_value"]
        print(f"  → Price=${r.get('price')} | Base=${fv.get('base')} | Upside={r.get('upside_pct')}% | {r['verdict']}", file=sys.stderr)

    # Markdown report → stdout
    print(format_report(results))

    # JSON → stderr
    output = results[0] if len(results) == 1 else results
    print(f"\n---JSON---\n{json.dumps(output, indent=2, default=str)}", file=sys.stderr)


if __name__ == "__main__":
    main()
