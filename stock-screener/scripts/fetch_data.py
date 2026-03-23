#!/usr/bin/env python3
"""
Stock Screener - Server-side multi-factor screening via Yahoo Finance.

Two-phase approach:
  Phase 1: Server-side filter (sector, PE, ROE, market cap, region) — 1 API call
  Phase 2: Fetch detailed data only for top candidates — N API calls (N ≈ 25-50)

Usage:
  python3 fetch_data.py --sector Technology                    # US tech stocks
  python3 fetch_data.py --sector Technology --industry Semiconductors
  python3 fetch_data.py --region hk --sector Technology        # HK tech stocks
  python3 fetch_data.py --tickers AAPL MSFT NVDA               # Custom list
  python3 fetch_data.py --pe 25 --roe 10 --top 50              # Custom thresholds
  python3 fetch_data.py --sector Technology --pe 0 --roe 0     # No financial filters
"""

import sys
import os
import csv
import argparse
import time
import math
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
try:
    from market import HSI_TICKERS, HSTECH_TICKERS
except ImportError:
    HSI_TICKERS = []
    HSTECH_TICKERS = []

# Yahoo Finance sector names (used by EquityQuery)
VALID_SECTORS = {
    "Basic Materials", "Communication Services", "Consumer Cyclical",
    "Consumer Defensive", "Energy", "Financial Services", "Healthcare",
    "Industrials", "Real Estate", "Technology", "Utilities",
}

# Common sector name aliases for fuzzy matching
SECTOR_ALIASES = {
    "tech": "Technology",
    "it": "Technology",
    "finance": "Financial Services",
    "financial": "Financial Services",
    "bank": "Financial Services",
    "banking": "Financial Services",
    "health": "Healthcare",
    "pharma": "Healthcare",
    "energy": "Energy",
    "oil": "Energy",
    "industrial": "Industrials",
    "manufacturing": "Industrials",
    "consumer": "Consumer Cyclical",
    "retail": "Consumer Cyclical",
    "realestate": "Real Estate",
    "property": "Real Estate",
    "materials": "Basic Materials",
    "mining": "Basic Materials",
    "utility": "Utilities",
    "telecom": "Communication Services",
    "media": "Communication Services",
}


def resolve_sector(user_input):
    """Resolve user's sector input to a valid Yahoo Finance sector name.

    Returns a valid sector name or None if unresolvable.
    """
    if not user_input:
        return None

    # Exact match (case-insensitive)
    for s in VALID_SECTORS:
        if user_input.lower() == s.lower():
            return s

    # Partial match (e.g., "Financial" → "Financial Services")
    for s in VALID_SECTORS:
        if user_input.lower() in s.lower() or s.lower() in user_input.lower():
            return s

    # Alias match (e.g., "tech" -> "Technology")
    for alias, sector in SECTOR_ALIASES.items():
        if alias in user_input.lower():
            return sector

    print(f"[screener] Warning: sector '{user_input}' not recognized. "
          f"Valid: {', '.join(sorted(VALID_SECTORS))}", file=sys.stderr)
    return None


def compute_score(pe, max_pe, roe, min_roe, rev_growth, mcap):
    """Compute a 0-100 composite score with continuous scaling.

    Components (weighted):
    - Valuation  (30%): How far below max_pe — lower P/E scores higher
    - Profitability (30%): How far above min_roe — higher ROE scores higher
    - Growth     (25%): Revenue growth rate — higher is better
    - Scale      (15%): Market cap — larger gets moderate bonus
    """
    score = 0.0

    # Valuation: 0-30 pts
    if pe and pe > 0 and max_pe > 0:
        val_ratio = max(0, 1 - pe / max_pe)
        score += val_ratio * 30
    elif max_pe <= 0:
        score += 15  # no PE filter → neutral score
    else:
        score += 15  # missing PE data → neutral

    # Profitability: 0-30 pts
    if roe and roe > 0:
        if min_roe > 0:
            roe_ratio = max(0, (roe - min_roe) / (min_roe * 2))
        else:
            roe_ratio = min(1, roe / 30)  # no min_roe: 30% ROE = full score
        score += min(30, roe_ratio * 30)

    # Growth: 0-25 pts
    if rev_growth and rev_growth > 0:
        growth_ratio = min(1, rev_growth / 30)
        score += growth_ratio * 25

    # Scale: 0-15 pts
    if mcap and mcap > 0:
        log_mcap = math.log10(max(mcap, 1e9))
        scale_ratio = min(1, max(0, (log_mcap - 9) / 3))
        score += scale_ratio * 15

    return round(score, 1)


def _extract_stock_data(info, quote=None):
    """Extract standardized stock data from yfinance info dict.

    Shared by both server-side and custom-ticker screening paths.
    """
    ticker = info.get("symbol") or (quote or {}).get("symbol", "")
    pe = info.get("trailingPE") or info.get("forwardPE")
    roe_raw = info.get("returnOnEquity")
    roe = (roe_raw or 0) * 100
    mcap = info.get("marketCap") or (quote or {}).get("marketCap") or 0
    rev_growth = (info.get("revenueGrowth") or 0) * 100
    name = info.get("shortName") or (quote or {}).get("shortName") or ticker
    price = (info.get("currentPrice")
             or info.get("regularMarketPrice")
             or (quote or {}).get("regularMarketPrice")
             or 0)

    return {
        "ticker": ticker,
        "name": name,
        "sector": info.get("sector") or "",
        "industry": info.get("industry") or "",
        "price": price,
        "pe": pe,
        "roe": roe,
        "mcap": mcap,
        "rev_growth": rev_growth,
    }


def _format_result(data, max_pe, min_roe):
    """Format extracted stock data into output row with score."""
    score = compute_score(data["pe"], max_pe, data["roe"], min_roe,
                          data["rev_growth"], data["mcap"])
    return {
        "ticker": data["ticker"],
        "name": data["name"],
        "sector": data["sector"] or "N/A",
        "industry": data["industry"] or "N/A",
        "price": round(data["price"], 2),
        "market_cap_B": round(data["mcap"] / 1e9, 1) if data["mcap"] else 0,
        "pe": round(data["pe"], 1) if data["pe"] else "",
        "roe_pct": round(data["roe"], 1),
        "revenue_growth_pct": round(data["rev_growth"], 1),
        "score": score,
    }


def screen_server_side(region="us", sector=None, max_pe=20, min_roe=15,
                       min_market_cap=1e9, top=25):
    """Phase 1: Server-side screening via Yahoo Finance EquityQuery.

    Makes ONE API call to Yahoo's screener endpoint which filters on their
    server and returns only matching stocks.

    Note: The screen response includes price/PE/marketCap but NOT
    sector/industry/ROE/revenueGrowth — those require Phase 2 enrichment.
    """
    import yfinance as yf

    conditions = []

    # Region filter (always applied)
    conditions.append(yf.EquityQuery('eq', ['region', region]))

    # Sector filter (server-side)
    if sector:
        resolved = resolve_sector(sector)
        if resolved:
            conditions.append(yf.EquityQuery('eq', ['sector', resolved]))
            print(f"[screener] Server-side filter: sector={resolved}", file=sys.stderr)
        else:
            print(f"[screener] Skipping sector filter (unresolved)", file=sys.stderr)

    # P/E filter (server-side) — skip if max_pe <= 0 (user wants no PE filter)
    if max_pe > 0:
        conditions.append(yf.EquityQuery('btwn', ['peratio.lasttwelvemonths', 0, max_pe]))

    # ROE filter (server-side) — skip if min_roe <= 0
    if min_roe > 0:
        conditions.append(yf.EquityQuery('gt', ['returnonequity.lasttwelvemonths', min_roe / 100]))

    # Market cap filter (server-side)
    if min_market_cap > 0:
        conditions.append(yf.EquityQuery('gt', ['intradaymarketcap', min_market_cap]))

    query = yf.EquityQuery('and', conditions)
    print(f"[screener] Running server-side screen (region={region})...", file=sys.stderr)

    try:
        result = yf.screen(query, sortField='intradaymarketcap', sortAsc=False,
                           size=min(top, 250))
    except Exception as e:
        print(f"[screener] Server-side screen failed: {e}", file=sys.stderr)
        print(f"[screener] This may be a network issue or Yahoo rate limit.", file=sys.stderr)
        return [], 0

    total = result.get('total', 0)
    quotes = result.get('quotes', [])
    print(f"[screener] Server returned {len(quotes)} stocks (total matching: {total})", file=sys.stderr)

    return quotes, total


def enrich_with_details(quotes, max_pe, min_roe, industry_filter=None,
                        min_market_cap=0):
    """Phase 2: Fetch detailed data (ROE, industry, revenue growth) for candidates.

    The screen response only has price/PE/marketCap. This step fetches the full
    financial profile for scoring and ranking. Only called for server-side
    filtered candidates (typically 25-50 stocks).

    Re-validates financial filters against detailed data because server-side
    screen data can diverge from ticker-level info (stale snapshots, different
    data sources within Yahoo).
    """
    import yfinance as yf

    results = []
    skipped_industry = 0
    skipped_revalidation = 0

    print(f"[screener] Fetching details for {len(quotes)} candidates...", file=sys.stderr)

    for q in quotes:
        ticker = q.get('symbol', '')
        if not ticker:
            continue

        try:
            info = yf.Ticker(ticker).info
            data = _extract_stock_data(info, quote=q)

            # Industry filter (client-side — not available in server-side screen)
            if industry_filter:
                if industry_filter.lower() not in data["industry"].lower():
                    skipped_industry += 1
                    continue

            # Re-validate financial filters against detailed data
            if max_pe > 0 and data["pe"] is not None and data["pe"] >= max_pe:
                skipped_revalidation += 1
                continue
            if min_roe > 0 and data["roe"] <= min_roe:
                skipped_revalidation += 1
                continue
            if min_market_cap > 0 and data["mcap"] <= min_market_cap:
                skipped_revalidation += 1
                continue

            results.append(_format_result(data, max_pe, min_roe))
        except Exception as e:
            print(f"[screener] Skip {ticker}: {e}", file=sys.stderr)
            continue
        time.sleep(0.05)

    if industry_filter and skipped_industry:
        print(f"[screener] Industry filter '{industry_filter}': {skipped_industry} skipped", file=sys.stderr)
    if skipped_revalidation:
        print(f"[screener] Re-validation: {skipped_revalidation} removed (server/detail data mismatch)", file=sys.stderr)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def screen_custom_tickers(tickers, max_pe=20, min_roe=15, min_market_cap=1e9,
                          sector_filter=None, industry_filter=None):
    """Screen a custom list of tickers (no server-side screening available).

    Used for: --tickers, --index hstech/hsi (predefined HK lists).
    Each ticker requires an individual API call, so keep lists small.
    """
    import yfinance as yf

    results = []
    total = len(tickers)
    print(f"[screener] Screening {total} custom tickers...", file=sys.stderr)

    for i, ticker in enumerate(tickers):
        if i % 20 == 0 and i > 0:
            print(f"[screener] Progress: {i}/{total}", file=sys.stderr)
        try:
            info = yf.Ticker(ticker).info
            if not info:
                continue

            data = _extract_stock_data(info)

            # Sector filter (client-side partial match)
            if sector_filter:
                resolved = resolve_sector(sector_filter) or sector_filter
                sf = resolved.lower()
                ss = data["sector"].lower()
                if sf not in ss and ss not in sf:
                    continue

            # Industry filter (client-side partial match)
            if industry_filter:
                if industry_filter.lower() not in data["industry"].lower():
                    continue

            # Financial filters
            passes = True
            if max_pe > 0 and data["pe"] is not None and data["pe"] >= max_pe:
                passes = False
            if min_roe > 0 and data["roe"] <= min_roe:
                passes = False
            if min_market_cap > 0 and data["mcap"] <= min_market_cap:
                passes = False

            if passes:
                results.append(_format_result(data, max_pe, min_roe))
        except Exception:
            continue
        time.sleep(0.05)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Multi-factor stock screener")
    parser.add_argument("--region", default="us",
                        help="Market region: us, hk, gb, jp, etc. (default: us)")
    parser.add_argument("--index", choices=["hsi", "hstech"],
                        help="Use a predefined HK index universe (bypasses server-side screen)")
    parser.add_argument("--tickers", nargs="+",
                        help="Custom ticker list (e.g., AAPL MSFT or 0700.HK)")
    parser.add_argument("--sector",
                        help="Sector filter (e.g., Technology, Healthcare, tech)")
    parser.add_argument("--industry",
                        help="Industry sub-filter, partial match (e.g., Semiconductors, Banks)")
    parser.add_argument("--pe", type=float, default=20,
                        help="Max P/E ratio; 0 to disable (default: 20)")
    parser.add_argument("--roe", type=float, default=15,
                        help="Min ROE %%; 0 to disable (default: 15)")
    parser.add_argument("--mcap", type=float, default=1.0,
                        help="Min market cap in $B; 0 to disable (default: 1)")
    parser.add_argument("--top", type=int, default=25,
                        help="Max results from server-side screen (default: 25)")
    parser.add_argument("--output", default="screener_results.csv")
    args = parser.parse_args()

    # Route: custom tickers or predefined index → individual fetch
    # Otherwise → server-side screening (much faster)
    use_custom = args.tickers or args.index in ("hsi", "hstech")

    if use_custom:
        if args.tickers:
            tickers = args.tickers
            label = f"custom ({len(tickers)} tickers)"
        elif args.index == "hsi":
            tickers = HSI_TICKERS if HSI_TICKERS else []
            label = f"Hang Seng Index ({len(tickers)} tickers)"
        else:  # hstech
            tickers = HSTECH_TICKERS if HSTECH_TICKERS else []
            label = f"Hang Seng Tech ({len(tickers)} tickers)"

        if not tickers:
            print("[screener] ERROR: No tickers in universe.", file=sys.stderr)
            sys.exit(1)

        print(f"[screener] Mode: {label}", file=sys.stderr)
        results = screen_custom_tickers(
            tickers,
            max_pe=args.pe, min_roe=args.roe,
            min_market_cap=args.mcap * 1e9,
            sector_filter=args.sector, industry_filter=args.industry,
        )
    else:
        # Server-side screening (default path)
        quotes, total = screen_server_side(
            region=args.region,
            sector=args.sector,
            max_pe=args.pe, min_roe=args.roe,
            min_market_cap=args.mcap * 1e9,
            top=args.top,
        )

        if not quotes:
            print("No stocks matched server-side filters.")
            return

        results = enrich_with_details(
            quotes,
            max_pe=args.pe, min_roe=args.roe,
            industry_filter=args.industry,
            min_market_cap=args.mcap * 1e9,
        )

    if not results:
        print("No stocks passed all filters.")
        return

    # Write CSV
    fieldnames = ["ticker", "name", "sector", "industry", "price",
                  "market_cap_B", "pe", "roe_pct", "revenue_growth_pct", "score"]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # --- Formatted output report ---
    print(f"\n{'=' * 80}")
    print("SCREENING RESULTS")
    print(f"{'=' * 80}")

    # Filters summary
    filters = []
    if args.sector:
        filters.append(f"Sector: {resolve_sector(args.sector) or args.sector}")
    if args.industry:
        filters.append(f"Industry: {args.industry}")
    if not use_custom:
        filters.append(f"Region: {args.region.upper()}")
    if args.pe > 0:
        filters.append(f"P/E < {args.pe}")
    if args.roe > 0:
        filters.append(f"ROE > {args.roe}%")
    if args.mcap > 0:
        filters.append(f"Market Cap > ${args.mcap}B")
    print(f"Filters: {' | '.join(filters) if filters else 'None'}")
    print(f"Results: {len(results)} stocks passed")
    print(f"Output:  {args.output}")

    # Scoring methodology
    print(f"\nScoring: Valuation(30%) + Profitability(30%) + Growth(25%) + Scale(15%) = 0-100")
    pe_note = f"PE<{args.pe} threshold" if args.pe > 0 else "PE not filtered"
    roe_note = f"ROE>{args.roe}% threshold" if args.roe > 0 else "ROE not filtered"
    print(f"  Valuation:     Lower P/E relative to {pe_note} scores higher")
    print(f"  Profitability: Higher ROE above {roe_note} scores higher")
    print(f"  Growth:        Revenue growth 0-30%+ mapped linearly")
    print(f"  Scale:         Market cap $1B-$1T on log scale")

    # Formatted table
    print(f"\n{'Rank':<5} {'Ticker':<8} {'Company':<28} {'Industry':<24} "
          f"{'P/E':>6} {'ROE%':>7} {'Growth%':>8} {'MCap($B)':>9} {'Score':>6}")
    print(f"{'-' * 5} {'-' * 8} {'-' * 28} {'-' * 24} "
          f"{'-' * 6} {'-' * 7} {'-' * 8} {'-' * 9} {'-' * 6}")

    for i, r in enumerate(results[:20], 1):
        pe_str = f"{r['pe']:.1f}" if r['pe'] != '' else '-'
        print(f"{i:<5} {r['ticker']:<8} {r['name'][:27]:<28} {r['industry'][:23]:<24} "
              f"{pe_str:>6} {r['roe_pct']:>6.1f}% {r['revenue_growth_pct']:>7.1f}% "
              f"{r['market_cap_B']:>8.1f} {r['score']:>6.1f}")

    if len(results) > 20:
        print(f"  ... and {len(results) - 20} more (see CSV)")

    # Industry breakdown
    industries = Counter(r['industry'] for r in results if r['industry'] != 'N/A')
    if industries:
        print(f"\nIndustry Breakdown:")
        for ind, count in industries.most_common(5):
            print(f"  {ind:<30} {count} stocks")

    # Score distribution
    scores = [r['score'] for r in results]
    print(f"\nScore Distribution:")
    print(f"  Highest: {max(scores):.1f} ({results[0]['ticker']})")
    print(f"  Lowest:  {min(scores):.1f} ({results[-1]['ticker']})")
    print(f"  Average: {sum(scores)/len(scores):.1f}")

    print(f"\n{'=' * 80}")


if __name__ == "__main__":
    main()
