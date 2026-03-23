#!/usr/bin/env python3
"""
Comps Analysis - Data Fetcher
Fetches valuation multiples and operating metrics for a list of tickers using yfinance.
Outputs a CSV with P/E, EV/EBITDA, EV/Revenue, P/B, Revenue, EBITDA, Market Cap, etc.

Usage:
    python3 scripts/fetch_data.py AAPL MSFT GOOGL META AMZN
    python3 scripts/fetch_data.py TSLA RIVN LCID NIO --output ev_comps.csv
"""

import sys
import csv
import json
import argparse
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)


def safe_get(d, *keys, default=None):
    """Safely get nested dict value."""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d if d is not None else default


def format_billions(val):
    if val is None:
        return "N/A"
    try:
        return f"{float(val)/1e9:.2f}B"
    except (ValueError, TypeError):
        return "N/A"


def fetch_ticker_metrics(ticker_symbol):
    """Fetch key valuation and operating metrics for a single ticker."""
    print(f"  Fetching {ticker_symbol}...", end=" ", flush=True)
    try:
        tk = yf.Ticker(ticker_symbol)
        info = tk.info

        # Basic info
        name = info.get("longName") or info.get("shortName", ticker_symbol)
        currency = info.get("currency", "USD")
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")

        # Market data
        market_cap = info.get("marketCap")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")

        # Valuation multiples
        trailing_pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        price_to_book = info.get("priceToBook")
        ev_to_revenue = info.get("enterpriseToRevenue")
        ev_to_ebitda = info.get("enterpriseToEbitda")
        enterprise_value = info.get("enterpriseValue")

        # Revenue & EBITDA
        revenue_ttm = info.get("totalRevenue")
        ebitda_ttm = info.get("ebitda")
        gross_margins = info.get("grossMargins")
        operating_margins = info.get("operatingMargins")
        profit_margins = info.get("profitMargins")

        # Growth
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")

        # Returns
        roe = info.get("returnOnEquity")
        roa = info.get("returnOnAssets")

        # Leverage
        debt_to_equity = info.get("debtToEquity")
        total_debt = info.get("totalDebt")
        free_cash_flow = info.get("freeCashflow")

        print("✓")

        return {
            "Ticker": ticker_symbol,
            "Company Name": name,
            "Sector": sector,
            "Industry": industry,
            "Currency": currency,
            "Price": f"{current_price:.2f}" if current_price else "N/A",
            "Market Cap ($B)": format_billions(market_cap),
            "Enterprise Value ($B)": format_billions(enterprise_value),
            "Revenue TTM ($B)": format_billions(revenue_ttm),
            "EBITDA TTM ($B)": format_billions(ebitda_ttm),
            "Trailing P/E": f"{trailing_pe:.1f}x" if trailing_pe else "N/A",
            "Forward P/E": f"{forward_pe:.1f}x" if forward_pe else "N/A",
            "P/B": f"{price_to_book:.2f}x" if price_to_book else "N/A",
            "EV/Revenue": f"{ev_to_revenue:.2f}x" if ev_to_revenue else "N/A",
            "EV/EBITDA": f"{ev_to_ebitda:.1f}x" if ev_to_ebitda else "N/A",
            "Gross Margin": f"{gross_margins:.1%}" if gross_margins else "N/A",
            "Operating Margin": f"{operating_margins:.1%}" if operating_margins else "N/A",
            "Net Margin": f"{profit_margins:.1%}" if profit_margins else "N/A",
            "Revenue Growth YoY": f"{revenue_growth:.1%}" if revenue_growth else "N/A",
            "Earnings Growth YoY": f"{earnings_growth:.1%}" if earnings_growth else "N/A",
            "ROE": f"{roe:.1%}" if roe else "N/A",
            "ROA": f"{roa:.1%}" if roa else "N/A",
            "Debt/Equity": f"{debt_to_equity:.2f}" if debt_to_equity else "N/A",
            "Free Cash Flow ($B)": format_billions(free_cash_flow),
        }

    except Exception as e:
        print(f"✗ ({e})")
        return {
            "Ticker": ticker_symbol,
            "Company Name": "ERROR",
            "Error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Fetch valuation comps data for a list of tickers"
    )
    parser.add_argument("tickers", nargs="+", help="One or more ticker symbols (e.g. AAPL MSFT GOOGL)")
    parser.add_argument("--output", "-o", default=None, help="Output CSV filename (default: comps_<date>.csv)")
    parser.add_argument("--json", action="store_true", help="Also output JSON file")
    args = parser.parse_args()

    tickers = [t.upper() for t in args.tickers]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = args.output or f"comps_{timestamp}.csv"

    print(f"\n=== Comps Analysis - Data Fetcher ===")
    print(f"Tickers: {', '.join(tickers)}")
    print(f"Output:  {output_file}\n")

    rows = []
    for ticker in tickers:
        row = fetch_ticker_metrics(ticker)
        rows.append(row)

    if not rows:
        print("No data fetched.")
        sys.exit(1)

    # Write CSV
    all_keys = list(rows[0].keys())
    # Ensure all rows have all keys
    for row in rows:
        for key in all_keys:
            if key not in row:
                row[key] = "N/A"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Saved {len(rows)} companies to {output_file}")

    # Print summary table
    print("\n--- Summary ---")
    header = f"{'Ticker':<8} {'EV/Revenue':>12} {'EV/EBITDA':>12} {'P/E (Trailing)':>15} {'P/B':>8} {'Rev Growth':>12}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(f"{row['Ticker']:<8} {row.get('EV/Revenue', 'N/A'):>12} {row.get('EV/EBITDA', 'N/A'):>12} "
              f"{row.get('Trailing P/E', 'N/A'):>15} {row.get('P/B', 'N/A'):>8} {row.get('Revenue Growth YoY', 'N/A'):>12}")

    # Optionally write JSON
    if args.json:
        json_file = output_file.replace(".csv", ".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON saved to {json_file}")


if __name__ == "__main__":
    main()
