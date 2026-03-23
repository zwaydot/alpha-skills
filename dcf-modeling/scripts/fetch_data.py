#!/usr/bin/env python3
"""
DCF Modeling - Historical Financial Data Fetcher
Fetches revenue, EBITDA, FCF, CapEx, D&A, and other inputs needed to populate DCF assumptions.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py MSFT --years 5 --output msft_dcf_inputs.json
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


def safe_val(series, index, divisor=1e9):
    """Safely extract a value from a pandas Series by index label."""
    try:
        val = series.loc[index]
        if pd.isna(val):
            return None
        return round(float(val) / divisor, 3)
    except (KeyError, TypeError):
        return None


def fetch_dcf_data(ticker_symbol, years=5):
    """Fetch historical financials for DCF modeling."""
    print(f"\n=== DCF Data Fetcher: {ticker_symbol} ===\n")

    tk = yf.Ticker(ticker_symbol)
    info = tk.info

    # --- Company Info ---
    company_name = info.get("longName", ticker_symbol)
    sector = info.get("sector", "N/A")
    currency = info.get("currency", "USD")
    shares_outstanding = info.get("sharesOutstanding")
    current_price = info.get("currentPrice") or info.get("regularMarketPrice")
    beta = info.get("beta")

    # --- Market / Capital Structure ---
    market_cap = info.get("marketCap")
    total_debt = info.get("totalDebt", 0) or 0
    cash = info.get("totalCash", 0) or 0
    enterprise_value = info.get("enterpriseValue")
    tax_rate = info.get("effectiveTaxRateHistory") or 0.21  # fallback to 21%

    # --- Current Multiples (for sanity check) ---
    ev_to_ebitda = info.get("enterpriseToEbitda")
    ev_to_revenue = info.get("enterpriseToRevenue")
    trailing_pe = info.get("trailingPE")

    print(f"Company: {company_name} | Sector: {sector}")
    print(f"Price: {current_price} {currency} | Shares: {shares_outstanding:,.0f}" if shares_outstanding else "")
    print(f"Beta: {beta} | Market Cap: {(market_cap or 0)/1e9:.1f}B | Net Debt: {(total_debt - cash)/1e9:.1f}B\n")

    # --- Historical Income Statement ---
    try:
        income = tk.financials  # annual, columns = fiscal year dates
        income = income[sorted(income.columns, reverse=True)[:years]]
    except Exception as e:
        print(f"Warning: Could not fetch income statement: {e}")
        income = pd.DataFrame()

    # --- Historical Cash Flow ---
    try:
        cashflow = tk.cashflow
        cashflow = cashflow[sorted(cashflow.columns, reverse=True)[:years]]
    except Exception as e:
        print(f"Warning: Could not fetch cashflow: {e}")
        cashflow = pd.DataFrame()

    # --- Historical Balance Sheet ---
    try:
        balance = tk.balance_sheet
        balance = balance[sorted(balance.columns, reverse=True)[:years]]
    except Exception as e:
        print(f"Warning: Could not fetch balance sheet: {e}")
        balance = pd.DataFrame()

    # --- Extract Key Metrics ---
    historical = []
    col_dates = sorted(income.columns, reverse=True) if not income.empty else []

    for col in col_dates[:years]:
        year_str = str(col.year) if hasattr(col, "year") else str(col)

        revenue = safe_val(income[col], "Total Revenue") if not income.empty else None
        gross_profit = safe_val(income[col], "Gross Profit") if not income.empty else None
        ebit = safe_val(income[col], "EBIT") if not income.empty else None
        ebitda = safe_val(income[col], "EBITDA") if not income.empty else None
        net_income = safe_val(income[col], "Net Income") if not income.empty else None
        interest_expense = safe_val(income[col], "Interest Expense") if not income.empty else None

        # Cash flow items
        operating_cf = safe_val(cashflow[col], "Operating Cash Flow") if not cashflow.empty and col in cashflow.columns else None
        capex = safe_val(cashflow[col], "Capital Expenditure") if not cashflow.empty and col in cashflow.columns else None
        da = safe_val(cashflow[col], "Depreciation And Amortization") if not cashflow.empty and col in cashflow.columns else None

        # FCF
        fcf = None
        if operating_cf is not None and capex is not None:
            fcf = round(operating_cf + capex, 3)  # CapEx is usually negative

        # Derived margins
        gross_margin = round(gross_profit / revenue, 4) if gross_profit and revenue else None
        ebitda_margin = round(ebitda / revenue, 4) if ebitda and revenue else None
        ebit_margin = round(ebit / revenue, 4) if ebit and revenue else None
        net_margin = round(net_income / revenue, 4) if net_income and revenue else None
        capex_pct = round(abs(capex or 0) / revenue, 4) if capex and revenue else None
        fcf_margin = round(fcf / revenue, 4) if fcf and revenue else None

        historical.append({
            "fiscal_year": year_str,
            "revenue_bn": revenue,
            "gross_profit_bn": gross_profit,
            "ebit_bn": ebit,
            "ebitda_bn": ebitda,
            "net_income_bn": net_income,
            "interest_expense_bn": interest_expense,
            "operating_cash_flow_bn": operating_cf,
            "capex_bn": capex,
            "da_bn": da,
            "fcf_bn": fcf,
            "margins": {
                "gross_margin": f"{gross_margin:.1%}" if gross_margin else "N/A",
                "ebitda_margin": f"{ebitda_margin:.1%}" if ebitda_margin else "N/A",
                "ebit_margin": f"{ebit_margin:.1%}" if ebit_margin else "N/A",
                "net_margin": f"{net_margin:.1%}" if net_margin else "N/A",
                "capex_pct_revenue": f"{capex_pct:.1%}" if capex_pct else "N/A",
                "fcf_margin": f"{fcf_margin:.1%}" if fcf_margin else "N/A",
            }
        })

    # --- Revenue CAGR (if enough data) ---
    rev_cagr = None
    if len(historical) >= 2:
        rev_start = historical[-1].get("revenue_bn")
        rev_end = historical[0].get("revenue_bn")
        n = len(historical) - 1
        if rev_start and rev_end and rev_start > 0:
            rev_cagr = round((rev_end / rev_start) ** (1 / n) - 1, 4)

    # --- WACC Inputs ---
    risk_free_rate = 0.042  # ~10Y UST as of 2024
    erp = 0.05  # Damodaran estimate
    cost_of_equity = None
    if beta:
        cost_of_equity = round(risk_free_rate + beta * erp, 4)

    result = {
        "metadata": {
            "ticker": ticker_symbol,
            "company_name": company_name,
            "sector": sector,
            "currency": currency,
            "fetched_at": datetime.now().isoformat(),
            "data_years": years,
        },
        "market_data": {
            "current_price": current_price,
            "shares_outstanding": shares_outstanding,
            "market_cap_bn": round(market_cap / 1e9, 2) if market_cap else None,
            "total_debt_bn": round(total_debt / 1e9, 2) if total_debt else None,
            "cash_bn": round(cash / 1e9, 2) if cash else None,
            "net_debt_bn": round((total_debt - cash) / 1e9, 2) if total_debt else None,
            "enterprise_value_bn": round(enterprise_value / 1e9, 2) if enterprise_value else None,
            "current_ev_ebitda": ev_to_ebitda,
            "current_ev_revenue": ev_to_revenue,
            "current_trailing_pe": trailing_pe,
        },
        "wacc_inputs": {
            "beta": beta,
            "risk_free_rate": f"{risk_free_rate:.1%}",
            "equity_risk_premium": f"{erp:.1%}",
            "cost_of_equity_estimate": f"{cost_of_equity:.2%}" if cost_of_equity else "N/A",
            "suggested_tax_rate": "21%",
            "note": "Add cost of debt and capital structure to complete WACC calculation",
        },
        "revenue_cagr_historical": f"{rev_cagr:.1%}" if rev_cagr else "N/A",
        "historical_financials": historical,
        "dcf_assumptions_template": {
            "projection_years": 5,
            "revenue_growth_rates": ["Enter Year 1-5 growth rates here"],
            "ebitda_margin_target": "Enter target EBITDA margin",
            "da_pct_revenue": "Derive from historical",
            "capex_pct_revenue": "Derive from historical",
            "nwc_pct_revenue": "Estimate from balance sheet",
            "terminal_growth_rate": "2.5%",
            "wacc": "Calculate using inputs above",
        }
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch historical financials for DCF modeling")
    parser.add_argument("ticker", help="Ticker symbol (e.g. AAPL)")
    parser.add_argument("--years", type=int, default=5, help="Number of historical years (default: 5)")
    parser.add_argument("--output", "-o", default=None, help="Output JSON filename")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    output_file = args.output or f"{ticker}_dcf_inputs_{datetime.now().strftime('%Y%m%d')}.json"

    data = fetch_dcf_data(ticker, args.years)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ DCF input data saved to: {output_file}")
    print(f"\n--- Historical Revenue & FCF ---")
    for yr in data["historical_financials"]:
        rev = yr.get("revenue_bn")
        fcf = yr.get("fcf_bn")
        ebitda = yr.get("ebitda_bn")
        print(f"  {yr['fiscal_year']}: Revenue={rev}B | EBITDA={ebitda}B | FCF={fcf}B | "
              f"EBITDA Margin={yr['margins']['ebitda_margin']}")

    print(f"\n  Historical Revenue CAGR: {data['revenue_cagr_historical']}")
    print(f"\nNext step: Review {output_file} and fill in 'dcf_assumptions_template' to build projections.")


if __name__ == "__main__":
    main()
