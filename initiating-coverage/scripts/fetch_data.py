#!/usr/bin/env python3
"""
Initiating Coverage Research - Data Fetcher
Fetches comprehensive company data including business overview, financial summary,
price history, and analyst consensus for initiating coverage reports.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py TSLA --output tesla_coverage.json
    python3 scripts/fetch_data.py NVDA --history-years 3
"""

import sys
import json
import argparse
from datetime import datetime, timedelta

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("Error: yfinance / pandas not installed. Run: pip install yfinance pandas")
    sys.exit(1)


def safe_float(val, default=None):
    try:
        f = float(val)
        return None if pd.isna(f) else f
    except (TypeError, ValueError):
        return default


def safe_pct(val):
    v = safe_float(val)
    return f"{v:.1%}" if v is not None else "N/A"


def safe_bn(val):
    v = safe_float(val)
    return round(v / 1e9, 2) if v is not None else None


def fetch_company_overview(info):
    """Extract company overview from yfinance info dict."""
    return {
        "company_name": info.get("longName", "N/A"),
        "ticker": info.get("symbol", "N/A"),
        "exchange": info.get("exchange", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "country": info.get("country", "N/A"),
        "currency": info.get("currency", "USD"),
        "employees": info.get("fullTimeEmployees"),
        "website": info.get("website", "N/A"),
        "description": info.get("longBusinessSummary", "N/A"),
        "address": {
            "city": info.get("city", "N/A"),
            "state": info.get("state", "N/A"),
            "zip": info.get("zip", "N/A"),
            "country": info.get("country", "N/A"),
            "phone": info.get("phone", "N/A"),
        },
        "fiscal_year_end": info.get("fiscalYearEnd", "N/A"),
        "auditor_report": info.get("auditRisk", "N/A"),
        "governance_score": info.get("governanceEpScore", "N/A"),
    }


def fetch_financial_summary(info, tk):
    """Extract comprehensive financial summary."""
    # Market data
    market_cap = info.get("marketCap")
    enterprise_value = info.get("enterpriseValue")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    shares = info.get("sharesOutstanding")

    # Income metrics
    revenue = info.get("totalRevenue")
    ebitda = info.get("ebitda")
    gross_margins = info.get("grossMargins")
    operating_margins = info.get("operatingMargins")
    profit_margins = info.get("profitMargins")

    # Balance sheet
    total_cash = info.get("totalCash")
    total_debt = info.get("totalDebt", 0) or 0
    net_debt = total_debt - (total_cash or 0)
    current_ratio = info.get("currentRatio")
    quick_ratio = info.get("quickRatio")
    debt_to_equity = info.get("debtToEquity")

    # Cash flow
    fcf = info.get("freeCashflow")
    operating_cf = info.get("operatingCashflow")

    # Valuation multiples
    pe_trailing = info.get("trailingPE")
    pe_forward = info.get("forwardPE")
    peg = info.get("pegRatio")
    pb = info.get("priceToBook")
    ps = info.get("priceToSalesTrailing12Months")
    ev_revenue = info.get("enterpriseToRevenue")
    ev_ebitda = info.get("enterpriseToEbitda")

    # Returns
    roe = info.get("returnOnEquity")
    roa = info.get("returnOnAssets")

    # Growth
    revenue_growth = info.get("revenueGrowth")
    earnings_growth = info.get("earningsGrowth")

    # EPS
    trailing_eps = info.get("trailingEps")
    forward_eps = info.get("forwardEps")

    # Dividends
    dividend_yield = info.get("dividendYield")
    payout_ratio = info.get("payoutRatio")

    return {
        "market_data": {
            "price": current_price,
            "market_cap_bn": safe_bn(market_cap),
            "enterprise_value_bn": safe_bn(enterprise_value),
            "shares_outstanding": shares,
            "float_shares": info.get("floatShares"),
            "shares_short": info.get("sharesShort"),
            "short_ratio": info.get("shortRatio"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "50d_avg": info.get("fiftyDayAverage"),
            "200d_avg": info.get("twoHundredDayAverage"),
            "beta": info.get("beta"),
        },
        "income_statement_ttm": {
            "revenue_bn": safe_bn(revenue),
            "ebitda_bn": safe_bn(ebitda),
            "gross_margin": safe_pct(gross_margins),
            "operating_margin": safe_pct(operating_margins),
            "net_margin": safe_pct(profit_margins),
            "trailing_eps": trailing_eps,
            "forward_eps": forward_eps,
        },
        "balance_sheet": {
            "total_cash_bn": safe_bn(total_cash),
            "total_debt_bn": safe_bn(total_debt),
            "net_debt_bn": round(net_debt / 1e9, 2) if net_debt else None,
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "debt_to_equity": round(debt_to_equity / 100, 2) if debt_to_equity else None,
        },
        "cash_flow_ttm": {
            "operating_cf_bn": safe_bn(operating_cf),
            "free_cash_flow_bn": safe_bn(fcf),
            "fcf_margin": safe_pct(safe_float(fcf) / safe_float(revenue)) if fcf and revenue else "N/A",
        },
        "valuation_multiples": {
            "trailing_pe": f"{pe_trailing:.1f}x" if pe_trailing else "N/A",
            "forward_pe": f"{pe_forward:.1f}x" if pe_forward else "N/A",
            "peg_ratio": f"{peg:.2f}x" if peg else "N/A",
            "price_to_book": f"{pb:.2f}x" if pb else "N/A",
            "price_to_sales": f"{ps:.2f}x" if ps else "N/A",
            "ev_to_revenue": f"{ev_revenue:.2f}x" if ev_revenue else "N/A",
            "ev_to_ebitda": f"{ev_ebitda:.1f}x" if ev_ebitda else "N/A",
        },
        "returns_and_growth": {
            "roe": safe_pct(roe),
            "roa": safe_pct(roa),
            "revenue_growth_yoy": safe_pct(revenue_growth),
            "earnings_growth_yoy": safe_pct(earnings_growth),
        },
        "dividends": {
            "dividend_yield": safe_pct(dividend_yield),
            "payout_ratio": safe_pct(payout_ratio),
            "ex_dividend_date": str(info.get("exDividendDate", "N/A")),
        },
    }


def fetch_price_history(tk, years=3):
    """Fetch historical price data and compute key statistics."""
    period_map = {1: "1y", 2: "2y", 3: "3y", 5: "5y"}
    period = period_map.get(years, "3y")
    try:
        hist = tk.history(period=period)
        if hist.empty:
            return {}

        closes = hist["Close"]
        volumes = hist["Volume"]

        # Returns
        total_return = (closes.iloc[-1] / closes.iloc[0] - 1)
        ytd_start = closes[closes.index.year == closes.index[-1].year].iloc[0] if len(closes) > 0 else None
        ytd_return = (closes.iloc[-1] / ytd_start - 1) if ytd_start is not None else None

        # Volatility (annualized)
        daily_returns = closes.pct_change().dropna()
        volatility = daily_returns.std() * (252 ** 0.5)

        # Price stats
        stats = {
            "current_price": round(float(closes.iloc[-1]), 2),
            "start_price": round(float(closes.iloc[0]), 2),
            "period": f"{years} year(s)",
            "total_return": f"{total_return:.1%}",
            "ytd_return": f"{ytd_return:.1%}" if ytd_return else "N/A",
            "annualized_volatility": f"{volatility:.1%}",
            "avg_daily_volume": int(volumes.mean()),
            "high": round(float(closes.max()), 2),
            "low": round(float(closes.min()), 2),
            "data_points": len(closes),
        }

        # Monthly price series (last 24 months for charting)
        monthly = closes.resample("ME").last()
        monthly_series = [
            {"date": str(d.date()), "close": round(float(p), 2)}
            for d, p in monthly.items()
        ]

        stats["monthly_prices"] = monthly_series[-24:]  # last 24 months

        return stats

    except Exception as e:
        print(f"  Warning: Could not fetch price history: {e}")
        return {}


def fetch_analyst_data(info, tk):
    """Fetch analyst recommendations and estimates."""
    analyst_data = {
        "recommendation": info.get("recommendationKey", "N/A"),
        "mean_rating": info.get("recommendationMean"),
        "number_of_analysts": info.get("numberOfAnalystOpinions"),
        "target_price_mean": info.get("targetMeanPrice"),
        "target_price_high": info.get("targetHighPrice"),
        "target_price_low": info.get("targetLowPrice"),
        "current_price": info.get("currentPrice"),
    }

    current = info.get("currentPrice")
    target_mean = info.get("targetMeanPrice")
    if current and target_mean:
        analyst_data["upside_to_target"] = f"{(target_mean/current - 1):.1%}"

    # Analyst upgrades/downgrades (recent)
    try:
        recs = tk.recommendations
        if recs is not None and not recs.empty:
            recent_recs = recs.tail(10).reset_index()
            analyst_data["recent_actions"] = [
                {
                    "date": str(r.get("Date", "") or r.get("index", "")),
                    "firm": r.get("Firm", r.get("firm", "N/A")),
                    "action": r.get("Action", r.get("action", "N/A")),
                    "from_grade": r.get("From Grade", r.get("fromGrade", "N/A")),
                    "to_grade": r.get("To Grade", r.get("toGrade", "N/A")),
                }
                for _, r in recent_recs.iterrows()
            ]
    except Exception:
        pass

    return analyst_data


def fetch_historical_financials(tk, years=5):
    """Fetch multi-year historical financial data."""
    result = {}

    try:
        income = tk.financials
        if income is not None and not income.empty:
            cols = sorted(income.columns, reverse=True)[:years]
            income_summary = {}
            for col in cols:
                year_str = str(col.year) if hasattr(col, "year") else str(col)

                def _g(label):
                    try:
                        v = income[col].get(label)
                        return round(float(v) / 1e9, 3) if v is not None and not pd.isna(v) else None
                    except Exception:
                        return None

                revenue = _g("Total Revenue")
                gross = _g("Gross Profit")
                ebit = _g("EBIT")
                ebitda = _g("EBITDA")
                net = _g("Net Income")

                income_summary[year_str] = {
                    "revenue_bn": revenue,
                    "gross_profit_bn": gross,
                    "ebit_bn": ebit,
                    "ebitda_bn": ebitda,
                    "net_income_bn": net,
                    "gross_margin": f"{gross/revenue:.1%}" if gross and revenue else "N/A",
                    "ebitda_margin": f"{ebitda/revenue:.1%}" if ebitda and revenue else "N/A",
                    "net_margin": f"{net/revenue:.1%}" if net and revenue else "N/A",
                }
            result["income_statement"] = income_summary
    except Exception as e:
        print(f"  Warning: Historical income statement error: {e}")

    try:
        cf = tk.cashflow
        if cf is not None and not cf.empty:
            cols = sorted(cf.columns, reverse=True)[:years]
            cf_summary = {}
            for col in cols:
                year_str = str(col.year) if hasattr(col, "year") else str(col)

                def _g(label):
                    try:
                        v = cf[col].get(label)
                        return round(float(v) / 1e9, 3) if v is not None and not pd.isna(v) else None
                    except Exception:
                        return None

                op_cf = _g("Operating Cash Flow")
                capex = _g("Capital Expenditure")
                fcf = round(op_cf + (capex or 0), 3) if op_cf is not None else None

                cf_summary[year_str] = {
                    "operating_cf_bn": op_cf,
                    "capex_bn": capex,
                    "fcf_bn": fcf,
                    "da_bn": _g("Depreciation And Amortization"),
                }
            result["cash_flow"] = cf_summary
    except Exception as e:
        print(f"  Warning: Historical cash flow error: {e}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch comprehensive data for initiating coverage")
    parser.add_argument("ticker", help="Ticker symbol (e.g. AAPL)")
    parser.add_argument("--output", "-o", default=None, help="Output JSON filename")
    parser.add_argument("--history-years", type=int, default=3, help="Years of price history (default: 3)")
    parser.add_argument("--financial-years", type=int, default=5, help="Years of financial history (default: 5)")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    output_file = args.output or f"{ticker}_coverage_data_{datetime.now().strftime('%Y%m%d')}.json"

    print(f"\n=== Initiating Coverage Data Fetcher: {ticker} ===\n")

    tk = yf.Ticker(ticker)
    info = tk.info

    print(f"Company: {info.get('longName', ticker)}")
    print(f"Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')}\n")

    print("Fetching company overview...")
    overview = fetch_company_overview(info)

    print("Fetching financial summary...")
    financials = fetch_financial_summary(info, tk)

    print(f"Fetching {args.history_years}-year price history...")
    price_history = fetch_price_history(tk, args.history_years)

    print("Fetching analyst data...")
    analyst = fetch_analyst_data(info, tk)

    print(f"Fetching {args.financial_years}-year historical financials...")
    historical = fetch_historical_financials(tk, args.financial_years)

    result = {
        "metadata": {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "fetched_at": datetime.now().isoformat(),
            "report_type": "Initiating Coverage Data Pack",
        },
        "company_overview": overview,
        "financial_summary": financials,
        "price_history": price_history,
        "analyst_consensus": analyst,
        "historical_financials": historical,
        "coverage_initiation_framework": {
            "investment_thesis_components": [
                "Business model and competitive moat",
                "Total addressable market (TAM) and share",
                "Financial performance and trajectory",
                "Valuation vs. peers",
                "Key risks and mitigants",
                "Catalysts for re-rating",
            ],
            "suggested_report_sections": [
                "Executive Summary + Investment Recommendation",
                "Company Overview & Business Model",
                "Industry Analysis & Competitive Positioning",
                "Financial Analysis (historical + projections)",
                "Valuation (DCF + Trading Comps + Precedents)",
                "Risk Factors",
                "Appendix (Detailed Financials, Mgmt Bios)",
            ],
        }
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Coverage data saved to: {output_file}")

    # Quick summary
    mkt = financials.get("market_data", {})
    val = financials.get("valuation_multiples", {})
    ph = price_history
    ac = analyst

    print(f"\n--- Quick Summary: {ticker} ---")
    print(f"  Price: ${mkt.get('price')} | Market Cap: ${mkt.get('market_cap_bn')}B | EV: ${mkt.get('enterprise_value_bn')}B")
    print(f"  EV/Revenue: {val.get('ev_to_revenue')} | EV/EBITDA: {val.get('ev_to_ebitda')} | P/E (Fwd): {val.get('forward_pe')}")
    print(f"  {ph.get('period', '')} Return: {ph.get('total_return', 'N/A')} | YTD: {ph.get('ytd_return', 'N/A')}")
    print(f"  Analyst: {ac.get('recommendation', 'N/A')} | Target: ${ac.get('target_price_mean')} | Upside: {ac.get('upside_to_target', 'N/A')}")
    print(f"  Analysts: {ac.get('number_of_analysts')}")


if __name__ == "__main__":
    main()
