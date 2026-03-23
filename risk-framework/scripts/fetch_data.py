#!/usr/bin/env python3
"""
risk-framework: Fetch beta/volatility/leverage/liquidity metrics and output risk scorecard.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py AAPL TSLA AMZN
    python3 scripts/fetch_data.py NVDA > nvda_risk.json
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
try:
    from market import detect_market, get_risk_free_rate
except ImportError:
    def detect_market(ticker): return "US"
    def get_risk_free_rate(market): return 0.045

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


def compute_volatility(ticker_sym: str, days: int = 252) -> float | None:
    """Compute annualized realized volatility from daily returns."""
    try:
        t = yf.Ticker(ticker_sym)
        end = datetime.today()
        start = end - timedelta(days=days + 30)
        hist = t.history(start=start, end=end)
        if hist.empty or len(hist) < 20:
            return None
        returns = hist["Close"].pct_change().dropna()
        vol = returns.std() * (252 ** 0.5) * 100  # annualized %
        return round(float(vol), 2)
    except Exception:
        return None


def score_market_risk(beta: float | None, vol: float | None) -> tuple[float, list[str]]:
    """Returns (score 0-100, risk_flags). Higher score = higher risk."""
    risks = []
    score = 0.0

    if beta is not None:
        if beta > 2.0:
            score += 40; risks.append(f"Very high beta ({beta:.2f})")
        elif beta > 1.5:
            score += 30; risks.append(f"High beta ({beta:.2f})")
        elif beta > 1.2:
            score += 20
        elif beta > 0.8:
            score += 10
        else:
            score += 0  # low beta = safe
    else:
        score += 20  # unknown = moderate penalty

    if vol is not None:
        if vol > 60:
            score += 60; risks.append(f"Extreme volatility ({vol:.1f}% annualized)")
        elif vol > 40:
            score += 40; risks.append(f"High volatility ({vol:.1f}%)")
        elif vol > 25:
            score += 25
        elif vol > 15:
            score += 10
        else:
            score += 0
    else:
        score += 20

    return min(100, score), risks


def score_leverage_risk(de_ratio: float | None, interest_coverage: float | None, debt_ebitda: float | None) -> tuple[float, list[str]]:
    """Returns (score 0-100, risk_flags)."""
    risks = []
    score = 0.0

    if de_ratio is not None:
        if de_ratio > 3.0:
            score += 40; risks.append(f"Very high D/E ratio ({de_ratio:.2f}x)")
        elif de_ratio > 2.0:
            score += 30; risks.append(f"High D/E ratio ({de_ratio:.2f}x)")
        elif de_ratio > 1.0:
            score += 20
        elif de_ratio > 0.5:
            score += 10
        else:
            score += 0
    else:
        score += 15

    if interest_coverage is not None:
        if interest_coverage < 1.5:
            score += 50; risks.append(f"Critical interest coverage ({interest_coverage:.1f}x)")
        elif interest_coverage < 3.0:
            score += 35; risks.append(f"Low interest coverage ({interest_coverage:.1f}x)")
        elif interest_coverage < 5.0:
            score += 20
        elif interest_coverage < 10.0:
            score += 10
        else:
            score += 0
    else:
        score += 15

    if debt_ebitda is not None:
        if debt_ebitda > 5.0:
            score += 10; risks.append(f"High Debt/EBITDA ({debt_ebitda:.1f}x)")
        elif debt_ebitda > 3.0:
            score += 5
        else:
            score += 0

    return min(100, score), risks


def score_liquidity_risk(current_ratio: float | None, quick_ratio: float | None) -> tuple[float, list[str]]:
    """Returns (score 0-100, risk_flags)."""
    risks = []
    score = 0.0

    if current_ratio is not None:
        if current_ratio < 0.5:
            score += 70; risks.append(f"Critical current ratio ({current_ratio:.2f})")
        elif current_ratio < 1.0:
            score += 50; risks.append(f"Low current ratio ({current_ratio:.2f})")
        elif current_ratio < 1.5:
            score += 25
        elif current_ratio < 2.0:
            score += 10
        else:
            score += 0
    else:
        score += 20

    if quick_ratio is not None:
        if quick_ratio < 0.5:
            score += 30; risks.append(f"Low quick ratio ({quick_ratio:.2f})")
        elif quick_ratio < 0.8:
            score += 15
        else:
            score += 0

    return min(100, score), risks


def score_earnings_quality(ticker_sym: str, info: dict) -> tuple[float, list[str]]:
    """Evaluate earnings quality via accruals ratio and FCF/Net Income ratio. Returns (score 0-100, risk_flags)."""
    risks = []
    score = 0.0

    t = yf.Ticker(ticker_sym)

    # FCF / Net Income ratio — high-quality earnings are backed by cash flow
    fcf_ni_ratio = None
    try:
        cf = t.cashflow
        fin = t.financials
        if cf is not None and not cf.empty and fin is not None and not fin.empty:
            col_cf = cf.columns[0]
            col_fin = fin.columns[0]

            ocf = None
            for key in ["Operating Cash Flow", "Total Cash From Operating Activities"]:
                if key in cf.index:
                    ocf = safe_float(cf.loc[key, col_cf])
                    break
            capex = None
            for key in ["Capital Expenditure", "Capital Expenditures"]:
                if key in cf.index:
                    capex = safe_float(cf.loc[key, col_cf])
                    break

            ni = None
            if "Net Income" in fin.index:
                ni = safe_float(fin.loc["Net Income", col_fin])

            if ocf is not None and capex is not None and ni and ni != 0:
                fcf = ocf + capex  # capex is usually negative
                fcf_ni_ratio = round(fcf / ni, 2)
    except Exception:
        pass

    if fcf_ni_ratio is not None:
        if fcf_ni_ratio < 0:
            score += 60
            risks.append(f"Negative FCF despite positive earnings (FCF/NI: {fcf_ni_ratio:.2f})")
        elif fcf_ni_ratio < 0.5:
            score += 40
            risks.append(f"Low cash conversion (FCF/NI: {fcf_ni_ratio:.2f})")
        elif fcf_ni_ratio < 0.8:
            score += 20
        elif fcf_ni_ratio < 1.2:
            score += 0  # healthy
        else:
            score += 0  # FCF > NI is fine (conservative accounting)
    else:
        score += 25  # unknown = moderate penalty

    # Accruals ratio — high accruals signal lower earnings quality
    # Accruals = Net Income - Operating Cash Flow; ratio = Accruals / Total Assets
    accruals_ratio = None
    try:
        cf = t.cashflow
        fin = t.financials
        bs = t.balance_sheet
        if all(x is not None and not x.empty for x in [cf, fin, bs]):
            col = cf.columns[0]
            ocf = None
            for key in ["Operating Cash Flow", "Total Cash From Operating Activities"]:
                if key in cf.index:
                    ocf = safe_float(cf.loc[key, col])
                    break
            ni = safe_float(fin.loc["Net Income", fin.columns[0]]) if "Net Income" in fin.index else None
            total_assets = None
            for key in ["Total Assets"]:
                if key in bs.index:
                    total_assets = safe_float(bs.loc[key, bs.columns[0]])
                    break

            if ocf is not None and ni is not None and total_assets and total_assets != 0:
                accruals = ni - ocf
                accruals_ratio = round(accruals / total_assets, 4)
    except Exception:
        pass

    if accruals_ratio is not None:
        abs_accruals = abs(accruals_ratio)
        if abs_accruals > 0.10:
            score += 40
            risks.append(f"High accruals ratio ({accruals_ratio:.2%} of assets)")
        elif abs_accruals > 0.05:
            score += 20
        elif abs_accruals > 0.03:
            score += 10
        else:
            score += 0  # low accruals = good
    else:
        score += 15

    return min(100, score), risks


def fetch_risk_data(ticker_sym: str) -> dict:
    t = yf.Ticker(ticker_sym)
    info = t.info
    name = info.get("longName") or info.get("shortName", ticker_sym)

    # Market risk metrics
    beta = safe_float(info.get("beta"))
    vol = compute_volatility(ticker_sym)

    # Financial leverage
    de_ratio = safe_float(info.get("debtToEquity"))  # often in % form (e.g., 150 = 1.5x)
    if de_ratio and de_ratio > 10:
        de_ratio = round(de_ratio / 100, 4)  # normalize to ratio

    # Try to compute interest coverage from financials
    interest_coverage = None
    debt_ebitda = None
    try:
        fin = t.financials
        if fin is not None and not fin.empty:
            col = fin.columns[0]
            ebit = None
            interest = None
            for key in ["EBIT", "Operating Income"]:
                if key in fin.index:
                    ebit = safe_float(fin.loc[key, col])
                    break
            for key in ["Interest Expense", "Interest And Debt Expense"]:
                if key in fin.index:
                    interest = safe_float(fin.loc[key, col])
                    break
            if ebit and interest and interest != 0:
                interest_coverage = round(ebit / abs(interest), 2)

        ebitda = safe_float(info.get("ebitda"))
        total_debt = safe_float(info.get("totalDebt"))
        if ebitda and total_debt and ebitda != 0:
            debt_ebitda = round(total_debt / ebitda, 2)
    except Exception:
        pass

    # Liquidity
    current_ratio = safe_float(info.get("currentRatio"))
    quick_ratio = safe_float(info.get("quickRatio"))

    # Earnings quality
    eq_score, eq_risks = score_earnings_quality(ticker_sym, info)

    # Score each dimension
    mkt_score, mkt_risks = score_market_risk(beta, vol)
    lev_score, lev_risks = score_leverage_risk(de_ratio, interest_coverage, debt_ebitda)
    liq_score, liq_risks = score_liquidity_risk(current_ratio, quick_ratio)

    # Weighted overall score
    overall = round(mkt_score * 0.30 + lev_score * 0.30 + liq_score * 0.20 + eq_score * 0.20, 1)

    if overall <= 25:
        risk_level = "Low"
    elif overall <= 50:
        risk_level = "Medium"
    elif overall <= 75:
        risk_level = "High"
    else:
        risk_level = "Very High"

    all_risks = mkt_risks + lev_risks + liq_risks + eq_risks
    key_risks = all_risks[:3]

    return {
        "ticker": ticker_sym.upper(),
        "company_name": name,
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "risk_score": overall,
        "risk_level": risk_level,
        "dimensions": {
            "market_risk": {"score": round(mkt_score, 1), "weight": "30%"},
            "leverage_risk": {"score": round(lev_score, 1), "weight": "30%"},
            "liquidity_risk": {"score": round(liq_score, 1), "weight": "20%"},
            "earnings_quality_risk": {"score": round(eq_score, 1), "weight": "20%"},
        },
        "raw_metrics": {
            "beta": beta,
            "annualized_volatility_pct": vol,
            "debt_to_equity": de_ratio,
            "interest_coverage": interest_coverage,
            "debt_to_ebitda": debt_ebitda,
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
        },
        "key_risks": key_risks,
        "position_sizing_guidance": {
            "Low": "Up to 10% of portfolio",
            "Medium": "Up to 7% of portfolio",
            "High": "Up to 4% of portfolio",
            "Very High": "Up to 2% of portfolio",
        }.get(risk_level, "Unknown"),
    }


def main():
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL"]
    results = []

    for sym in tickers:
        print(f"Fetching {sym}...", file=sys.stderr)
        result = fetch_risk_data(sym)
        results.append(result)
        print(f"  → {sym}: Risk Score={result.get('risk_score')} | Level={result.get('risk_level')}", file=sys.stderr)

    output = results[0] if len(results) == 1 else results
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
