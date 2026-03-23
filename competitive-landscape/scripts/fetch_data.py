#!/usr/bin/env python3
"""
Competitive Landscape Assessment - Data Fetcher
Fetches key financial and market metrics for a target company and its competitors
using yfinance. Outputs structured data for competitive positioning analysis.

Usage:
    python3 scripts/fetch_data.py AAPL --competitors MSFT GOOGL META AMZN
    python3 scripts/fetch_data.py TSLA --competitors RIVN NIO XPEV BYD --output ev_landscape.json
"""

import sys
import json
import csv
import argparse
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)


def safe_pct(val):
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.1%}"
    except (TypeError, ValueError):
        return "N/A"


def safe_x(val, decimals=1):
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.{decimals}f}x"
    except (TypeError, ValueError):
        return "N/A"


def safe_bn(val):
    if val is None:
        return None
    try:
        return round(float(val) / 1e9, 2)
    except (TypeError, ValueError):
        return None


def fetch_company_profile(ticker_symbol):
    """Fetch comprehensive competitive metrics for a company."""
    print(f"  Fetching {ticker_symbol}...", end=" ", flush=True)
    try:
        tk = yf.Ticker(ticker_symbol)
        info = tk.info

        name = info.get("longName") or info.get("shortName", ticker_symbol)
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        country = info.get("country", "N/A")
        currency = info.get("currency", "USD")
        employees = info.get("fullTimeEmployees")

        # Market position
        market_cap = info.get("marketCap")
        enterprise_value = info.get("enterpriseValue")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        week_52_high = info.get("fiftyTwoWeekHigh")
        week_52_low = info.get("fiftyTwoWeekLow")
        price_vs_52h = round((current_price / week_52_high - 1) * 100, 1) if current_price and week_52_high else None

        # Revenue & scale
        revenue = info.get("totalRevenue")
        ebitda = info.get("ebitda")
        gross_profit = info.get("grossProfits")

        # Valuation multiples
        pe_trailing = info.get("trailingPE")
        pe_forward = info.get("forwardPE")
        pb = info.get("priceToBook")
        ps = info.get("priceToSalesTrailing12Months")
        ev_revenue = info.get("enterpriseToRevenue")
        ev_ebitda = info.get("enterpriseToEbitda")
        peg = info.get("pegRatio")

        # Profitability
        gross_margin = info.get("grossMargins")
        operating_margin = info.get("operatingMargins")
        profit_margin = info.get("profitMargins")
        roe = info.get("returnOnEquity")
        roa = info.get("returnOnAssets")

        # Growth
        revenue_growth = info.get("revenueGrowth")
        earnings_growth = info.get("earningsGrowth")
        earnings_quarterly_growth = info.get("earningsQuarterlyGrowth")

        # Financial health
        current_ratio = info.get("currentRatio")
        quick_ratio = info.get("quickRatio")
        debt_to_equity = info.get("debtToEquity")
        total_debt = info.get("totalDebt")
        cash = info.get("totalCash")
        free_cash_flow = info.get("freeCashflow")

        # Dividend
        dividend_yield = info.get("dividendYield")
        payout_ratio = info.get("payoutRatio")

        # R&D
        rd_expense = None
        try:
            income = tk.financials
            if income is not None and not income.empty:
                col = income.columns[0]
                rd_expense = income[col].get("Research And Development")
        except Exception:
            pass

        print("✓")

        return {
            # Identity
            "ticker": ticker_symbol,
            "company_name": name,
            "sector": sector,
            "industry": industry,
            "country": country,
            "currency": currency,
            "employees": employees,
            # Market
            "price": current_price,
            "market_cap_bn": safe_bn(market_cap),
            "enterprise_value_bn": safe_bn(enterprise_value),
            "52w_vs_high_pct": f"{price_vs_52h}%" if price_vs_52h is not None else "N/A",
            # Scale
            "revenue_bn": safe_bn(revenue),
            "ebitda_bn": safe_bn(ebitda),
            # Valuation
            "trailing_pe": safe_x(pe_trailing),
            "forward_pe": safe_x(pe_forward),
            "pb": safe_x(pb, 2),
            "ps_ttm": safe_x(ps, 2),
            "ev_revenue": safe_x(ev_revenue, 2),
            "ev_ebitda": safe_x(ev_ebitda),
            "peg_ratio": safe_x(peg, 2),
            # Profitability
            "gross_margin": safe_pct(gross_margin),
            "operating_margin": safe_pct(operating_margin),
            "net_margin": safe_pct(profit_margin),
            "roe": safe_pct(roe),
            "roa": safe_pct(roa),
            # Growth
            "revenue_growth_yoy": safe_pct(revenue_growth),
            "earnings_growth_yoy": safe_pct(earnings_growth),
            # Financial Health
            "current_ratio": round(current_ratio, 2) if current_ratio else "N/A",
            "debt_to_equity": round(debt_to_equity / 100, 2) if debt_to_equity else "N/A",
            "net_debt_bn": safe_bn((total_debt or 0) - (cash or 0)),
            "fcf_bn": safe_bn(free_cash_flow),
            # Shareholder Returns
            "dividend_yield": safe_pct(dividend_yield),
            "payout_ratio": safe_pct(payout_ratio),
            # Innovation
            "rd_expense_bn": safe_bn(rd_expense),
        }

    except Exception as e:
        print(f"✗ ({e})")
        return {"ticker": ticker_symbol, "company_name": "ERROR", "error": str(e)}


def compute_competitive_insights(target_data, competitor_data_list):
    """Generate competitive positioning insights."""
    all_companies = [target_data] + competitor_data_list

    def _num(val):
        if isinstance(val, str) and val.endswith(("x", "%")):
            try:
                return float(val.rstrip("x%")) / (100 if val.endswith("%") else 1)
            except ValueError:
                return None
        if isinstance(val, (int, float)):
            return val
        return None

    insights = {}

    # Market cap ranking
    mcap_ranked = sorted(
        [(c["ticker"], c.get("market_cap_bn")) for c in all_companies if c.get("market_cap_bn")],
        key=lambda x: x[1] or 0, reverse=True
    )
    insights["market_cap_ranking"] = [{"ticker": t, "market_cap_bn": m} for t, m in mcap_ranked]

    # Revenue ranking
    rev_ranked = sorted(
        [(c["ticker"], c.get("revenue_bn")) for c in all_companies if c.get("revenue_bn")],
        key=lambda x: x[1] or 0, reverse=True
    )
    insights["revenue_ranking"] = [{"ticker": t, "revenue_bn": r} for t, r in rev_ranked]

    # Margin comparison
    margin_data = []
    for c in all_companies:
        gross = _num(c.get("gross_margin"))
        net = _num(c.get("net_margin"))
        margin_data.append({
            "ticker": c["ticker"],
            "gross_margin": c.get("gross_margin"),
            "net_margin": c.get("net_margin"),
            "roe": c.get("roe"),
        })
    insights["profitability_comparison"] = margin_data

    # Valuation comparison
    val_data = []
    for c in all_companies:
        val_data.append({
            "ticker": c["ticker"],
            "ev_revenue": c.get("ev_revenue"),
            "ev_ebitda": c.get("ev_ebitda"),
            "trailing_pe": c.get("trailing_pe"),
            "forward_pe": c.get("forward_pe"),
        })
    insights["valuation_comparison"] = val_data

    # Growth comparison
    growth_data = []
    for c in all_companies:
        growth_data.append({
            "ticker": c["ticker"],
            "revenue_growth_yoy": c.get("revenue_growth_yoy"),
            "earnings_growth_yoy": c.get("earnings_growth_yoy"),
        })
    insights["growth_comparison"] = growth_data

    return insights


def export_csv(all_companies, filename):
    """Export comparison data as CSV."""
    if not all_companies:
        return
    keys = list(all_companies[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        for company in all_companies:
            row = {k: company.get(k, "N/A") for k in keys}
            writer.writerow(row)
    print(f"✅ CSV saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Fetch competitive landscape data")
    parser.add_argument("target", help="Target company ticker (e.g. AAPL)")
    parser.add_argument("--competitors", "-c", nargs="+", required=True,
                        help="Competitor ticker symbols (e.g. MSFT GOOGL META)")
    parser.add_argument("--output", "-o", default=None, help="Output JSON filename")
    parser.add_argument("--csv", action="store_true", help="Also export CSV")
    args = parser.parse_args()

    target = args.target.upper()
    competitors = [c.upper() for c in args.competitors]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = args.output or f"{target}_competitive_landscape_{timestamp}.json"

    print(f"\n=== Competitive Landscape Assessment ===")
    print(f"Target: {target}")
    print(f"Competitors: {', '.join(competitors)}\n")

    # Fetch target
    target_data = fetch_company_profile(target)

    # Fetch competitors
    competitor_data = []
    for ticker in competitors:
        data = fetch_company_profile(ticker)
        competitor_data.append(data)

    # Generate insights
    insights = compute_competitive_insights(target_data, competitor_data)

    result = {
        "metadata": {
            "target": target,
            "competitors": competitors,
            "total_companies": 1 + len(competitors),
            "fetched_at": datetime.now().isoformat(),
        },
        "target_company": target_data,
        "competitors": competitor_data,
        "competitive_insights": insights,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Competitive landscape data saved to: {output_file}")

    # CSV export
    if args.csv:
        csv_file = output_file.replace(".json", ".csv")
        all_companies = [target_data] + competitor_data
        export_csv(all_companies, csv_file)

    # Print summary
    print(f"\n--- Market Cap Ranking ---")
    for item in insights.get("market_cap_ranking", []):
        marker = " ← TARGET" if item["ticker"] == target else ""
        print(f"  {item['ticker']}: ${item['market_cap_bn']}B{marker}")

    print(f"\n--- Valuation Comparison ---")
    header = f"  {'Ticker':<8} {'EV/Rev':>10} {'EV/EBITDA':>12} {'P/E (Trailing)':>15} {'P/E (Fwd)':>12}"
    print(header)
    print("  " + "-" * 57)
    for item in insights.get("valuation_comparison", []):
        marker = " ← TARGET" if item["ticker"] == target else ""
        print(f"  {item['ticker']:<8} {item['ev_revenue']:>10} {item['ev_ebitda']:>12} "
              f"{item['trailing_pe']:>15} {item['forward_pe']:>12}{marker}")

    print(f"\n--- Profitability Comparison ---")
    header2 = f"  {'Ticker':<8} {'Gross Margin':>14} {'Net Margin':>12} {'ROE':>10}"
    print(header2)
    print("  " + "-" * 46)
    for item in insights.get("profitability_comparison", []):
        marker = " ← TARGET" if item["ticker"] == target else ""
        print(f"  {item['ticker']:<8} {item['gross_margin']:>14} {item['net_margin']:>12} {item['roe']:>10}{marker}")


if __name__ == "__main__":
    main()
