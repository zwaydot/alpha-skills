#!/usr/bin/env python3
"""
stock-screener: Multi-factor stock screening using yfinance.
Fetches the full S&P 500 constituent list from Wikipedia and screens by:
  - P/E < 20
  - ROE > 15%
  - Market Cap > $1B

Usage:
    python3 scripts/fetch_data.py               # Full S&P 500 from Wikipedia
    python3 scripts/fetch_data.py AAPL MSFT NVDA  # Custom tickers

Env vars:
    PE_MAX           Maximum P/E ratio (default: 20)
    ROE_MIN          Minimum ROE % (default: 15)
    MARKET_CAP_MIN   Minimum market cap in USD (default: 1e9 = $1B)
"""

import sys
import os
import csv
import math
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed. Run: pip install pandas")
    sys.exit(1)

# ── Thresholds ────────────────────────────────────────────────────────────────
PE_MAX = float(os.environ.get("PE_MAX", 20))
ROE_MIN = float(os.environ.get("ROE_MIN", 15))
MARKET_CAP_MIN = float(os.environ.get("MARKET_CAP_MIN", 1e9))  # $1B USD

SP500_WIKI_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def fetch_sp500_tickers() -> list[str]:
    """Fetch S&P 500 constituent tickers from Wikipedia."""
    print("Fetching S&P 500 list from Wikipedia...", file=sys.stderr)
    try:
        tables = pd.read_html(SP500_WIKI_URL)
        df = tables[0]
        tickers = df["Symbol"].tolist()
        # Clean up: Wikipedia uses dots, Yahoo Finance uses dashes for BRK.B etc.
        tickers = [t.replace(".", "-") for t in tickers]
        print(f"  → Found {len(tickers)} S&P 500 constituents", file=sys.stderr)
        return tickers
    except Exception as e:
        print(f"  WARN: Failed to fetch from Wikipedia: {e}", file=sys.stderr)
        print("  Falling back to hardcoded S&P 100 subset...", file=sys.stderr)
        return [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
            "UNH", "LLY", "JPM", "V", "XOM", "AVGO", "PG", "MA", "COST", "HD",
            "MRK", "CVX", "ABBV", "PEP", "KO", "ADBE", "WMT", "MCD", "CRM",
            "BAC", "TMO", "ACN", "CSCO", "NFLX", "AMD", "ABT", "DHR", "TXN",
            "NEE", "PM", "UNP", "RTX", "AMGN", "ORCL", "HON", "QCOM", "IBM",
        ]


def safe_get(d, key, default=None):
    val = d.get(key, default)
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default
    return val


def fetch_metrics(ticker_sym: str) -> dict | None:
    """Fetch key metrics for a single ticker. Returns None on failure."""
    try:
        t = yf.Ticker(ticker_sym)
        info = t.info

        name = safe_get(info, "longName") or safe_get(info, "shortName", ticker_sym)
        market_cap = safe_get(info, "marketCap", 0)
        pe = safe_get(info, "trailingPE")
        roe = safe_get(info, "returnOnEquity")  # decimal, e.g. 0.15 = 15%
        sector = safe_get(info, "sector", "Unknown")
        industry = safe_get(info, "industry", "Unknown")

        # Convert to percentages
        roe_pct = round(roe * 100, 2) if roe is not None else None

        return {
            "ticker": ticker_sym,
            "name": name,
            "sector": sector,
            "industry": industry,
            "market_cap": market_cap,
            "pe_ratio": round(pe, 2) if pe else None,
            "roe": roe_pct,
        }
    except Exception as e:
        print(f"  WARN: Failed to fetch {ticker_sym}: {e}", file=sys.stderr)
        return None


def score(row: dict) -> float:
    """Compute composite score 0-100."""
    pe = row.get("pe_ratio")
    roe = row.get("roe")

    # Valuation: P/E 5→1.0, 20→0.0
    val_score = max(0, min(1, (PE_MAX - (pe or PE_MAX)) / (PE_MAX - 5))) if pe else 0
    # Profitability: ROE 15→0.0, 50→1.0
    prof_score = max(0, min(1, ((roe or ROE_MIN) - ROE_MIN) / 35)) if roe else 0

    return round((val_score * 0.40 + prof_score * 0.60) * 100, 1)


def passes_filters(row: dict) -> bool:
    pe = row.get("pe_ratio")
    roe = row.get("roe")
    mcap = row.get("market_cap", 0)

    if (mcap or 0) < MARKET_CAP_MIN:
        return False
    if pe is None or pe <= 0 or pe > PE_MAX:
        return False
    if roe is None or roe < ROE_MIN:
        return False
    return True


def format_mcap(v):
    if not v:
        return "N/A"
    if v >= 1e12:
        return f"${v/1e12:.2f}T"
    elif v >= 1e9:
        return f"${v/1e9:.2f}B"
    elif v >= 1e6:
        return f"${v/1e6:.2f}M"
    return str(v)


def main():
    if len(sys.argv) > 1:
        tickers = [t.upper() for t in sys.argv[1:]]
        print(f"Using {len(tickers)} custom tickers from command line", file=sys.stderr)
    else:
        tickers = fetch_sp500_tickers()

    print(f"\n🔍 Screening {len(tickers)} tickers...")
    print(f"   Filters: P/E < {PE_MAX} | ROE > {ROE_MIN}% | MCap > ${MARKET_CAP_MIN/1e9:.0f}B")
    print()

    rows = []
    for i, sym in enumerate(tickers):
        print(f"  [{i+1}/{len(tickers)}] Fetching {sym}...", end="", flush=True)
        data = fetch_metrics(sym)
        if data:
            data["score"] = score(data)
            rows.append(data)
            print(f" P/E={data['pe_ratio']} ROE={data['roe']}%")
        else:
            print(" skipped")

    # Filter
    passed = [r for r in rows if passes_filters(r)]
    passed.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n✅ {len(passed)} / {len(rows)} stocks passed all filters\n")

    if not passed:
        print("No stocks passed the current filters. Try relaxing thresholds via env vars (PE_MAX, ROE_MIN).")
        return

    # Print table
    print(f"{'Ticker':<8} {'Name':<35} {'Sector':<20} {'MCap':<10} {'P/E':<8} {'ROE%':<8} {'Score'}")
    print("-" * 100)
    for r in passed:
        print(f"{r['ticker']:<8} {str(r['name'])[:34]:<35} {str(r['sector'])[:19]:<20} "
              f"{format_mcap(r['market_cap']):<10} {str(r['pe_ratio']):<8} {str(r['roe']):<8} {r['score']}")

    # Save CSV
    output_file = "screener_results.csv"
    fieldnames = ["ticker", "name", "sector", "industry", "market_cap", "pe_ratio", "roe", "score"]
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(passed)

    print(f"\n💾 Results saved to {output_file}")
    print(f"   Screened at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
