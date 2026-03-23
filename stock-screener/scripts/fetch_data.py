#!/usr/bin/env python3
"""
Stock Screener - Multi-factor screening across any universe
Usage:
  python3 fetch_data.py                          # S&P 500 (default)
  python3 fetch_data.py --index sp500            # S&P 500
  python3 fetch_data.py --index nasdaq100        # Nasdaq 100
  python3 fetch_data.py --index russell2000      # Russell 2000
  python3 fetch_data.py --tickers AAPL MSFT NVDA # Custom list
  python3 fetch_data.py --sector XLK             # Sector ETF holdings
  python3 fetch_data.py --pe 25 --roe 10         # Custom thresholds
"""

import sys
import json
import csv
import argparse
import time

def get_sp500_tickers():
    import urllib.request
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode()
    import re
    return re.findall(r'<td><a href="/wiki/[^"]*" title="[^"]*">([A-Z.]{1,5})</a></td>', html)[:505]

def get_nasdaq100_tickers():
    import urllib.request
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode()
    import re
    tickers = re.findall(r'<td style="text-align:left"><a href="/wiki/[^"]*">([A-Z.]{1,5})</a>', html)
    return tickers[:110] if tickers else []

def get_russell2000_tickers():
    """Russell 2000 via iShares ETF holdings (IWM)"""
    try:
        import yfinance as yf
        # Use a sample of small-cap tickers as proxy
        # Full Russell 2000 requires paid data; use popular small-caps
        print("[screener] Note: Using curated small-cap universe (full Russell 2000 requires paid data)", file=sys.stderr)
        return ["ACLX","ACLS","ACMR","ADMA","ADUS","AFIB","AHCO","AIOT","AKRO","ALGN",
                "ALGT","ALKS","AMAG","AMBA","AMPH","AMRN","AMSC","AMWD","ANAB","ANIK"]  # sample
    except:
        return []

def get_sector_tickers(sector_etf):
    """Get top holdings of a sector ETF"""
    import yfinance as yf
    try:
        etf = yf.Ticker(sector_etf)
        holdings = etf.get_holdings()
        if holdings is not None and not holdings.empty:
            return holdings.index.tolist()[:50]
    except:
        pass
    # Fallback: common tickers per sector
    sector_map = {
        "XLK": ["AAPL","MSFT","NVDA","META","AVGO","ORCL","CRM","AMD","INTC","QCOM"],
        "XLF": ["BRK-B","JPM","V","MA","BAC","WFC","GS","MS","BLK","SCHW"],
        "XLE": ["XOM","CVX","COP","EOG","SLB","MPC","VLO","PSX","OXY","KMI"],
        "XLV": ["LLY","UNH","JNJ","MRK","ABBV","ABT","TMO","DHR","PFE","BMY"],
        "XLI": ["GE","RTX","CAT","HON","UNP","ETN","LMT","DE","WM","ITW"],
        "XLY": ["AMZN","TSLA","HD","MCD","NKE","SBUX","TJX","BKNG","LOW","CMG"],
        "XLP": ["PG","COST","KO","PEP","PM","MO","MDLZ","CL","EL","KMB"],
        "XLB": ["LIN","APD","SHW","ECL","NEM","NUE","FCX","ALB","IFF","CE"],
        "XLRE": ["PLD","AMT","EQIX","PSA","O","WELL","DLR","EXR","AVB","EQR"],
        "XLU": ["NEE","SO","DUK","AEP","XEL","SRE","D","EXC","PCG","WEC"],
    }
    return sector_map.get(sector_etf.upper(), [])

def screen_tickers(tickers, max_pe=20, min_roe=15, min_market_cap=1e9, max_workers=5):
    import yfinance as yf

    results = []
    total = len(tickers)
    print(f"[screener] Screening {total} tickers (P/E<{max_pe}, ROE>{min_roe}%, MCap>${min_market_cap/1e9:.0f}B)...", file=sys.stderr)

    for i, ticker in enumerate(tickers):
        if i % 20 == 0 and i > 0:
            print(f"[screener] Progress: {i}/{total}", file=sys.stderr)
        try:
            t = yf.Ticker(ticker)
            info = t.info
            if not info or info.get("quoteType") not in ("EQUITY", "ETF", None):
                continue

            pe = info.get("trailingPE") or info.get("forwardPE")
            roe = (info.get("returnOnEquity") or 0) * 100
            mcap = info.get("marketCap") or 0
            rev_growth = (info.get("revenueGrowth") or 0) * 100
            name = info.get("shortName") or ticker
            sector = info.get("sector") or "N/A"
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0

            # Scoring
            score = 0
            if pe and pe < max_pe: score += 2
            if roe > min_roe: score += 2
            if rev_growth > 10: score += 1
            if rev_growth > 20: score += 1
            if mcap > 1e10: score += 1  # bonus for large-cap stability

            passes = (
                (pe is None or pe < max_pe) and
                roe > min_roe and
                mcap > min_market_cap
            )

            if passes:
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "sector": sector,
                    "price": round(price, 2),
                    "market_cap_B": round(mcap / 1e9, 1),
                    "pe": round(pe, 1) if pe else "N/A",
                    "roe_pct": round(roe, 1),
                    "revenue_growth_pct": round(rev_growth, 1),
                    "score": score,
                })
        except Exception:
            continue
        time.sleep(0.05)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def main():
    parser = argparse.ArgumentParser(description="Multi-factor stock screener")
    parser.add_argument("--index", choices=["sp500","nasdaq100","russell2000"], default="sp500")
    parser.add_argument("--tickers", nargs="+", help="Custom ticker list")
    parser.add_argument("--sector", help="Sector ETF (e.g. XLK, XLF)")
    parser.add_argument("--pe", type=float, default=20, help="Max P/E ratio (default: 20)")
    parser.add_argument("--roe", type=float, default=15, help="Min ROE %% (default: 15)")
    parser.add_argument("--mcap", type=float, default=1.0, help="Min market cap in $B (default: 1)")
    parser.add_argument("--output", default="screener_results.csv")
    args = parser.parse_args()

    # Determine universe
    if args.tickers:
        tickers = args.tickers
        print(f"[screener] Universe: custom ({len(tickers)} tickers)", file=sys.stderr)
    elif args.sector:
        tickers = get_sector_tickers(args.sector)
        print(f"[screener] Universe: {args.sector} sector ({len(tickers)} tickers)", file=sys.stderr)
    elif args.index == "nasdaq100":
        tickers = get_nasdaq100_tickers()
        print(f"[screener] Universe: Nasdaq 100 ({len(tickers)} tickers)", file=sys.stderr)
    elif args.index == "russell2000":
        tickers = get_russell2000_tickers()
        print(f"[screener] Universe: Russell 2000 proxy ({len(tickers)} tickers)", file=sys.stderr)
    else:
        tickers = get_sp500_tickers()
        print(f"[screener] Universe: S&P 500 ({len(tickers)} tickers)", file=sys.stderr)

    results = screen_tickers(tickers, max_pe=args.pe, min_roe=args.roe, min_market_cap=args.mcap * 1e9)

    if not results:
        print("No stocks passed the filters.")
        return

    # Write CSV
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ {len(results)} stocks passed filters → {args.output}")
    print(f"\nTop 10:")
    for r in results[:10]:
        print(f"  {r['ticker']:<6} {r['name'][:30]:<30} P/E:{str(r['pe']):<6} ROE:{r['roe_pct']}%  Score:{r['score']}")

if __name__ == "__main__":
    main()
