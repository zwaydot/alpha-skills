#!/usr/bin/env python3
"""
Integrated Three-Statement Financial Modeling - Data Fetcher
Fetches 3-5 years of historical income statement, balance sheet, and cash flow data
from Yahoo Finance via yfinance. Outputs structured JSON for model building.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py MSFT --years 5 --output msft_3stmt.json
    python3 scripts/fetch_data.py AAPL --quarterly
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


def df_to_dict(df, divisor=1e9):
    """Convert a yfinance financial DataFrame to a clean dict of dicts."""
    if df is None or df.empty:
        return {}
    result = {}
    for col in df.columns:
        col_key = str(col.date()) if hasattr(col, "date") else str(col)
        result[col_key] = {}
        for idx in df.index:
            val = df.loc[idx, col]
            try:
                if pd.isna(val):
                    result[col_key][str(idx)] = None
                else:
                    result[col_key][str(idx)] = round(float(val) / divisor, 4)
            except (TypeError, ValueError):
                result[col_key][str(idx)] = None
    return result


def compute_ratios(income_data, balance_data, cashflow_data):
    """Compute key financial ratios for each period."""
    ratios = {}
    periods = list(income_data.keys())
    for period in periods:
        inc = income_data.get(period, {})
        bal = balance_data.get(period, {})
        cf = cashflow_data.get(period, {})

        revenue = inc.get("Total Revenue")
        gross_profit = inc.get("Gross Profit")
        ebit = inc.get("EBIT") or inc.get("Operating Income")
        ebitda = inc.get("EBITDA")
        net_income = inc.get("Net Income")
        total_assets = bal.get("Total Assets")
        total_equity = bal.get("Stockholders Equity") or bal.get("Common Stock Equity")
        total_debt = bal.get("Total Debt") or bal.get("Long Term Debt")
        cash = bal.get("Cash And Cash Equivalents") or bal.get("Cash Equivalents And Short Term Investments")
        op_cf = cf.get("Operating Cash Flow")
        capex = cf.get("Capital Expenditure")

        def _pct(num, denom):
            if num is not None and denom and denom != 0:
                return f"{num/denom:.1%}"
            return "N/A"

        fcf = round(op_cf + (capex or 0), 4) if op_cf is not None else None

        ratios[period] = {
            "gross_margin": _pct(gross_profit, revenue),
            "ebitda_margin": _pct(ebitda, revenue),
            "ebit_margin": _pct(ebit, revenue),
            "net_margin": _pct(net_income, revenue),
            "roe": _pct(net_income, total_equity),
            "roa": _pct(net_income, total_assets),
            "debt_to_equity": round(total_debt / total_equity, 2) if total_debt and total_equity and total_equity != 0 else "N/A",
            "capex_pct_revenue": _pct(abs(capex) if capex else None, revenue),
            "fcf_margin": _pct(fcf, revenue),
            "cash_bn": cash,
            "net_debt_bn": round((total_debt or 0) - (cash or 0), 4) if total_debt is not None else "N/A",
        }
    return ratios


def compute_revenue_cagr(income_data):
    """Calculate revenue CAGR across available periods."""
    periods = sorted(income_data.keys())
    if len(periods) < 2:
        return "N/A"
    rev_start = income_data[periods[0]].get("Total Revenue")
    rev_end = income_data[periods[-1]].get("Total Revenue")
    n = len(periods) - 1
    if rev_start and rev_end and rev_start > 0 and n > 0:
        cagr = (rev_end / rev_start) ** (1 / n) - 1
        return f"{cagr:.1%}"
    return "N/A"


def fetch_three_statement_data(ticker_symbol, years=5, quarterly=False):
    print(f"\n=== Three-Statement Financial Model Data: {ticker_symbol} ===\n")

    tk = yf.Ticker(ticker_symbol)
    info = tk.info

    company_name = info.get("longName", ticker_symbol)
    currency = info.get("currency", "USD")
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    fiscal_year_end = info.get("fiscalYearEnd", "N/A")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    market_cap = info.get("marketCap")
    shares = info.get("sharesOutstanding")
    enterprise_value = info.get("enterpriseValue")

    print(f"Company: {company_name} | Sector: {sector}")
    print(f"Currency: {currency} | Fiscal Year End: {fiscal_year_end}")
    print(f"Price: {current_price} | Market Cap: {(market_cap or 0)/1e9:.1f}B\n")

    period_label = "quarterly" if quarterly else "annual"

    # --- Income Statement ---
    try:
        if quarterly:
            income_raw = tk.quarterly_financials
        else:
            income_raw = tk.financials
        if income_raw is not None and not income_raw.empty:
            income_raw = income_raw[sorted(income_raw.columns, reverse=True)[:years]]
        income_data = df_to_dict(income_raw)
        print(f"  Income Statement: {len(income_data)} {period_label} periods")
    except Exception as e:
        print(f"  Warning: Income statement error: {e}")
        income_data = {}

    # --- Balance Sheet ---
    try:
        if quarterly:
            balance_raw = tk.quarterly_balance_sheet
        else:
            balance_raw = tk.balance_sheet
        if balance_raw is not None and not balance_raw.empty:
            balance_raw = balance_raw[sorted(balance_raw.columns, reverse=True)[:years]]
        balance_data = df_to_dict(balance_raw)
        print(f"  Balance Sheet: {len(balance_data)} {period_label} periods")
    except Exception as e:
        print(f"  Warning: Balance sheet error: {e}")
        balance_data = {}

    # --- Cash Flow Statement ---
    try:
        if quarterly:
            cashflow_raw = tk.quarterly_cashflow
        else:
            cashflow_raw = tk.cashflow
        if cashflow_raw is not None and not cashflow_raw.empty:
            cashflow_raw = cashflow_raw[sorted(cashflow_raw.columns, reverse=True)[:years]]
        cashflow_data = df_to_dict(cashflow_raw)
        print(f"  Cash Flow Statement: {len(cashflow_data)} {period_label} periods")
    except Exception as e:
        print(f"  Warning: Cash flow statement error: {e}")
        cashflow_data = {}

    # --- Computed Ratios ---
    ratios = compute_ratios(income_data, balance_data, cashflow_data)
    rev_cagr = compute_revenue_cagr(income_data)

    result = {
        "metadata": {
            "ticker": ticker_symbol,
            "company_name": company_name,
            "sector": sector,
            "industry": industry,
            "currency": currency,
            "fiscal_year_end": fiscal_year_end,
            "period_type": period_label,
            "fetched_at": datetime.now().isoformat(),
            "units": "Billions (USD unless otherwise noted)",
        },
        "market_data": {
            "current_price": current_price,
            "market_cap_bn": round(market_cap / 1e9, 2) if market_cap else None,
            "enterprise_value_bn": round(enterprise_value / 1e9, 2) if enterprise_value else None,
            "shares_outstanding": shares,
            "trailing_pe": info.get("trailingPE"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "ev_revenue": info.get("enterpriseToRevenue"),
        },
        "historical_summary": {
            "revenue_cagr": rev_cagr,
            "periods_available": sorted(list(income_data.keys()), reverse=True),
        },
        "key_ratios_by_period": ratios,
        "income_statement": income_data,
        "balance_sheet": balance_data,
        "cash_flow_statement": cashflow_data,
        "model_building_notes": {
            "forecast_drivers": [
                "Revenue growth by segment",
                "Gross margin trajectory",
                "EBITDA margin expansion/compression",
                "CapEx as % of revenue",
                "Working capital days (DSO, DIO, DPO)",
                "D&A schedule tied to PP&E",
            ],
            "key_linkages": [
                "Net Income → Retained Earnings (Balance Sheet)",
                "D&A (Income) → PP&E rollforward → Cash Flow",
                "ΔWorking Capital → Cash from Operations",
                "CapEx → PP&E (Balance Sheet) → Cash from Investing",
                "Net Borrowing → Debt schedule → Cash from Financing",
                "Ending Cash (CFS) = Cash on Balance Sheet",
            ],
            "checks_to_build": [
                "Balance Sheet must balance: Assets = Liabilities + Equity",
                "Cash reconciliation: BeginCash + Net Cash Flow = EndCash",
                "Net Income = Revenue - All expenses (verify bottom-up)",
            ],
        }
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch 3-statement historical data for financial modeling")
    parser.add_argument("ticker", help="Ticker symbol (e.g. AAPL)")
    parser.add_argument("--years", type=int, default=5, help="Number of historical years (default: 5)")
    parser.add_argument("--quarterly", action="store_true", help="Fetch quarterly instead of annual data")
    parser.add_argument("--output", "-o", default=None, help="Output JSON filename")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    suffix = "_quarterly" if args.quarterly else "_annual"
    output_file = args.output or f"{ticker}_3statement{suffix}_{datetime.now().strftime('%Y%m%d')}.json"

    data = fetch_three_statement_data(ticker, args.years, args.quarterly)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Three-statement data saved to: {output_file}")

    # Print summary
    print(f"\n--- Key Ratios Summary ---")
    for period in sorted(data["key_ratios_by_period"].keys(), reverse=True)[:3]:
        r = data["key_ratios_by_period"][period]
        print(f"  {period}: Revenue Growth=N/A | EBITDA Margin={r.get('ebitda_margin')} | "
              f"Net Margin={r.get('net_margin')} | CapEx/Rev={r.get('capex_pct_revenue')}")

    print(f"\n  Historical Revenue CAGR ({data['historical_summary']['periods_available'][-1]} to "
          f"{data['historical_summary']['periods_available'][0]}): {data['historical_summary']['revenue_cagr']}")


if __name__ == "__main__":
    main()
