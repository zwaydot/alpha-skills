#!/usr/bin/env python3
"""
Earnings Analysis - Data Fetcher
Fetches latest quarterly earnings data (EPS actual vs. estimate, Revenue actual vs. estimate)
and outputs structured JSON for earnings update report generation.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py TSLA --output tsla_earnings.json
"""

import sys
import json
import argparse
from datetime import datetime

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


def fetch_earnings_data(ticker_symbol):
    """Fetch comprehensive earnings data for a ticker."""
    print(f"\n=== Earnings Analysis Data Fetcher: {ticker_symbol} ===\n")

    tk = yf.Ticker(ticker_symbol)
    info = tk.info

    company_name = info.get("longName", ticker_symbol)
    currency = info.get("currency", "USD")
    sector = info.get("sector", "N/A")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    market_cap = info.get("marketCap")
    shares = info.get("sharesOutstanding")
    fiscal_year_end = info.get("fiscalYearEnd", "N/A")

    print(f"Company: {company_name} ({ticker_symbol})")
    print(f"Price: {current_price} {currency} | Market Cap: {(market_cap or 0)/1e9:.1f}B")

    # --- EPS History (actual vs. estimate) ---
    earnings_history = []
    try:
        eh = tk.earnings_history
        if eh is not None and not eh.empty:
            for _, row in eh.iterrows():
                quarter = str(row.get("quarterEnded") or row.name)
                eps_act = safe_float(row.get("epsActual"))
                eps_est = safe_float(row.get("epsEstimate"))
                surprise = safe_float(row.get("surprisePercent"))

                beat_miss = "N/A"
                if eps_act is not None and eps_est is not None:
                    diff = eps_act - eps_est
                    beat_miss = f"+{diff:.3f} beat" if diff > 0 else f"{diff:.3f} miss"

                earnings_history.append({
                    "quarter": quarter,
                    "eps_actual": eps_act,
                    "eps_estimate": eps_est,
                    "eps_surprise": beat_miss,
                    "surprise_pct": f"{surprise:.1f}%" if surprise else "N/A",
                })
        print(f"  EPS history: {len(earnings_history)} quarters")
    except Exception as e:
        print(f"  Warning: Could not fetch EPS history: {e}")

    # --- Quarterly Financials ---
    quarterly_results = []
    try:
        qf = tk.quarterly_financials
        qcf = tk.quarterly_cashflow
        qb = tk.quarterly_balance_sheet

        if qf is not None and not qf.empty:
            for col in sorted(qf.columns, reverse=True)[:8]:
                quarter_str = col.strftime("%Y-Q%q") if hasattr(col, "strftime") else str(col)
                try:
                    quarter_str = f"{col.year}-Q{(col.month-1)//3+1}"
                except Exception:
                    pass

                def _get(df, label):
                    try:
                        if df is not None and not df.empty and col in df.columns:
                            v = df[col].get(label)
                            return safe_float(v)
                    except Exception:
                        pass
                    return None

                revenue = _get(qf, "Total Revenue")
                gross_profit = _get(qf, "Gross Profit")
                ebit = _get(qf, "EBIT")
                net_income = _get(qf, "Net Income")
                operating_cf = _get(qcf, "Operating Cash Flow")
                capex = _get(qcf, "Capital Expenditure")

                gross_margin = round(gross_profit / revenue, 4) if gross_profit and revenue else None
                ebit_margin = round(ebit / revenue, 4) if ebit and revenue else None
                net_margin = round(net_income / revenue, 4) if net_income and revenue else None
                fcf = round(operating_cf + (capex or 0), 3) if operating_cf is not None else None

                quarterly_results.append({
                    "quarter": quarter_str,
                    "date": str(col),
                    "revenue_bn": round(revenue / 1e9, 3) if revenue else None,
                    "gross_profit_bn": round(gross_profit / 1e9, 3) if gross_profit else None,
                    "ebit_bn": round(ebit / 1e9, 3) if ebit else None,
                    "net_income_bn": round(net_income / 1e9, 3) if net_income else None,
                    "operating_cf_bn": round(operating_cf / 1e9, 3) if operating_cf else None,
                    "capex_bn": round(capex / 1e9, 3) if capex else None,
                    "fcf_bn": round(fcf / 1e9, 3) if fcf else None,
                    "gross_margin": f"{gross_margin:.1%}" if gross_margin else "N/A",
                    "ebit_margin": f"{ebit_margin:.1%}" if ebit_margin else "N/A",
                    "net_margin": f"{net_margin:.1%}" if net_margin else "N/A",
                })
        print(f"  Quarterly results: {len(quarterly_results)} quarters")
    except Exception as e:
        print(f"  Warning: Could not fetch quarterly financials: {e}")

    # --- Forward Estimates ---
    forward_estimates = {}
    try:
        # Annual estimates
        ae = tk.earnings_estimate
        if ae is not None and not ae.empty:
            for period in ae.index.tolist():
                row = ae.loc[period]
                forward_estimates[str(period)] = {
                    "eps_avg": safe_float(row.get("avg")),
                    "eps_low": safe_float(row.get("low")),
                    "eps_high": safe_float(row.get("high")),
                    "number_of_analysts": safe_float(row.get("numberOfAnalysts")),
                    "growth": safe_float(row.get("growth")),
                }
    except Exception as e:
        print(f"  Warning: Could not fetch forward estimates: {e}")

    # --- Revenue Estimates ---
    revenue_estimates = {}
    try:
        re = tk.revenue_estimate
        if re is not None and not re.empty:
            for period in re.index.tolist():
                row = re.loc[period]
                revenue_estimates[str(period)] = {
                    "revenue_avg_bn": round(safe_float(row.get("avg")) / 1e9, 2) if safe_float(row.get("avg")) else None,
                    "revenue_low_bn": round(safe_float(row.get("low")) / 1e9, 2) if safe_float(row.get("low")) else None,
                    "revenue_high_bn": round(safe_float(row.get("high")) / 1e9, 2) if safe_float(row.get("high")) else None,
                    "number_of_analysts": safe_float(row.get("numberOfAnalysts")),
                    "growth": safe_float(row.get("growth")),
                }
    except Exception as e:
        print(f"  Warning: Could not fetch revenue estimates: {e}")

    # --- Analyst Recommendations ---
    recommendation = {
        "current": info.get("recommendationKey", "N/A"),
        "mean_rating": info.get("recommendationMean"),
        "number_of_analysts": info.get("numberOfAnalystOpinions"),
        "target_price_mean": info.get("targetMeanPrice"),
        "target_price_high": info.get("targetHighPrice"),
        "target_price_low": info.get("targetLowPrice"),
    }

    # --- YoY comparison for most recent quarter ---
    yoy_comparison = {}
    if len(quarterly_results) >= 5:
        latest = quarterly_results[0]
        year_ago = quarterly_results[4]
        if latest.get("revenue_bn") and year_ago.get("revenue_bn"):
            yoy_comparison["revenue_yoy"] = f"{(latest['revenue_bn']/year_ago['revenue_bn'] - 1):.1%}"
        if latest.get("net_income_bn") and year_ago.get("net_income_bn"):
            yoy_comparison["net_income_yoy"] = f"{(latest['net_income_bn']/year_ago['net_income_bn'] - 1):.1%}"

    result = {
        "metadata": {
            "ticker": ticker_symbol,
            "company_name": company_name,
            "sector": sector,
            "currency": currency,
            "fiscal_year_end": fiscal_year_end,
            "fetched_at": datetime.now().isoformat(),
        },
        "current_snapshot": {
            "price": current_price,
            "market_cap_bn": round(market_cap / 1e9, 2) if market_cap else None,
            "shares_outstanding": shares,
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "trailing_eps": info.get("trailingEps"),
            "forward_eps": info.get("forwardEps"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
        },
        "analyst_consensus": recommendation,
        "eps_history": earnings_history,
        "quarterly_financials": quarterly_results,
        "yoy_latest_quarter": yoy_comparison,
        "forward_eps_estimates": forward_estimates,
        "forward_revenue_estimates": revenue_estimates,
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch earnings data for analysis")
    parser.add_argument("ticker", help="Ticker symbol (e.g. AAPL)")
    parser.add_argument("--output", "-o", default=None, help="Output JSON filename")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    output_file = args.output or f"{ticker}_earnings_{datetime.now().strftime('%Y%m%d')}.json"

    data = fetch_earnings_data(ticker)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Earnings data saved to: {output_file}")

    # Quick print of latest EPS history
    if data.get("eps_history"):
        print("\n--- Recent EPS History ---")
        for q in data["eps_history"][:4]:
            print(f"  {q['quarter']}: Actual={q['eps_actual']} | Est={q['eps_estimate']} | {q['eps_surprise']}")

    if data.get("quarterly_financials"):
        print("\n--- Recent Quarterly Revenue ---")
        for q in data["quarterly_financials"][:4]:
            print(f"  {q['quarter']}: Revenue={q['revenue_bn']}B | Net Income={q['net_income_bn']}B | Net Margin={q['net_margin']}")

    if data.get("analyst_consensus"):
        ac = data["analyst_consensus"]
        print(f"\n--- Analyst Consensus ---")
        print(f"  Rating: {ac['current']} | Mean: {ac['mean_rating']} | Analysts: {ac['number_of_analysts']}")
        print(f"  Target: ${ac['target_price_mean']} (Low: ${ac['target_price_low']}, High: ${ac['target_price_high']})")


if __name__ == "__main__":
    main()
