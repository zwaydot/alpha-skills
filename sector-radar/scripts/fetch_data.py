#!/usr/bin/env python3
"""
sector-radar: Sector rotation scanner using SPDR sector ETFs.

Usage:
    python3 scripts/fetch_data.py
    python3 scripts/fetch_data.py XLK XLF XLE XLV
    python3 scripts/fetch_data.py > sector_report.md
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
try:
    from market import get_sector_etfs
except ImportError:
    get_sector_etfs = None

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)

SECTOR_MAP_US = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Healthcare",
    "XLI": "Industrials",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
}

SECTOR_MAP_HK = {
    "3067.HK": "HK Tech (HSTECH ETF)",
    "3033.HK": "HK Financials",
    "3012.HK": "HK Property",
    "2800.HK": "HK Broad Market (Tracker)",
    "2828.HK": "China A-share ETF",
    "3040.HK": "HK Consumer",
}


def get_sector_map(market: str = "US") -> dict:
    """Return the ETF→sector mapping for a market."""
    if get_sector_etfs:
        return get_sector_etfs(market)
    if market == "HK":
        return SECTOR_MAP_HK
    return SECTOR_MAP_US


DEFAULT_ETFS = list(SECTOR_MAP_US.keys())


def get_return(hist, days: int) -> float | None:
    """Calculate price return over past N days."""
    try:
        end_price = hist["Close"].iloc[-1]
        start_idx = max(0, len(hist) - days - 1)
        start_price = hist["Close"].iloc[start_idx]
        return round((end_price / start_price - 1) * 100, 2)
    except Exception:
        return None


def momentum_score(r1m, r3m, r6m) -> float:
    """Weighted momentum score 0-100."""
    scores = []
    weights = []
    for ret, w in [(r1m, 0.40), (r3m, 0.35), (r6m, 0.25)]:
        if ret is not None:
            # Map return to 0-1: -20% → 0, +20% → 1
            normalized = max(0.0, min(1.0, (ret + 20) / 40))
            scores.append(normalized * w)
            weights.append(w)
    if not weights:
        return 50.0
    return round(sum(scores) / sum(weights) * 100, 1)


def cycle_signal(score: float, pe: float | None) -> str:
    if score > 65 and (pe is None or pe < 22):
        return "🟢 Bullish"
    elif score < 35 or (pe is not None and pe > 28):
        return "🔴 Bearish"
    else:
        return "🟡 Neutral"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sector rotation scanner")
    parser.add_argument("etfs", nargs="*", help="ETF tickers to scan")
    parser.add_argument("--market", choices=["US", "HK"], default="US",
                        help="Market to scan (default: US)")
    args = parser.parse_args()

    sector_map = get_sector_map(args.market)

    if args.etfs:
        etfs = [e.upper() for e in args.etfs]
    else:
        etfs = list(sector_map.keys())

    today = datetime.now()
    start = today - timedelta(days=400)

    market_label = "US" if args.market == "US" else "Hong Kong"
    print(f"# Sector Radar Report — {market_label}", flush=True)
    print(f"\n_Generated: {today.strftime('%Y-%m-%d %H:%M')} UTC_\n")

    results = []
    for sym in etfs:
        sector = sector_map.get(sym, sym)
        try:
            t = yf.Ticker(sym)
            hist = t.history(start=start.strftime("%Y-%m-%d"))
            info = t.info

            r1m = get_return(hist, 21)
            r3m = get_return(hist, 63)
            r6m = get_return(hist, 126)
            r1y = get_return(hist, 252)
            pe = info.get("trailingPE")
            div_yield = info.get("yield") or info.get("dividendYield")

            score = momentum_score(r1m, r3m, r6m)
            signal = cycle_signal(score, pe)

            results.append({
                "etf": sym,
                "sector": sector,
                "r1m": r1m,
                "r3m": r3m,
                "r6m": r6m,
                "r1y": r1y,
                "pe": round(pe, 1) if pe else None,
                "div_yield": round(div_yield * 100, 2) if div_yield else None,
                "score": score,
                "signal": signal,
            })
        except Exception as e:
            print(f"WARN: Failed {sym}: {e}", file=sys.stderr)

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # ── Ranking Table ──────────────────────────────────────────────────────────
    print("## Sector Rankings\n")
    print("| # | ETF | Sector | 1M% | 3M% | 6M% | 1Y% | P/E | Score | Signal |")
    print("|---|-----|--------|-----|-----|-----|-----|-----|-------|--------|")
    for i, r in enumerate(results, 1):
        fmt = lambda v: f"{v:+.1f}%" if v is not None else "N/A"
        pe_str = str(r["pe"]) if r["pe"] else "N/A"
        print(f"| {i} | **{r['etf']}** | {r['sector']} | {fmt(r['r1m'])} | {fmt(r['r3m'])} | {fmt(r['r6m'])} | {fmt(r['r1y'])} | {pe_str} | {r['score']} | {r['signal']} |")

    # ── Summary ────────────────────────────────────────────────────────────────
    bullish = [r for r in results if "Bullish" in r["signal"]]
    bearish = [r for r in results if "Bearish" in r["signal"]]

    print("\n## Cycle Assessment\n")
    if bullish:
        print(f"**🟢 Bullish Sectors ({len(bullish)}):** " + ", ".join(f"{r['etf']} ({r['sector']})" for r in bullish))
    if bearish:
        print(f"\n**🔴 Bearish Sectors ({len(bearish)}):** " + ", ".join(f"{r['etf']} ({r['sector']})" for r in bearish))

    if results:
        top = results[0]
        print(f"\n## Top Conviction Pick\n")
        print(f"**{top['etf']} — {top['sector']}**")
        print(f"- Momentum Score: {top['score']}/100")
        print(f"- 1M / 3M / 6M: {top['r1m']:+.1f}% / {top['r3m']:+.1f}% / {top['r6m']:+.1f}%" if all(v is not None for v in [top['r1m'], top['r3m'], top['r6m']]) else "")
        print(f"- Signal: {top['signal']}")


if __name__ == "__main__":
    main()
