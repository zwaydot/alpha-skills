#!/usr/bin/env python3
"""
Stock Screener v2 - Multi-factor screening with style-adaptive scoring.

Two-phase approach:
  Phase 1: Server-side filter (sector, PE, ROE, market cap, region) - 1 API call
  Phase 2: Fetch detailed data for top candidates, score with 5 factors - N API calls

Scoring factors: Valuation (PE + EV/EBITDA) | Profitability (ROE) |
  Growth (revenue + earnings) | Momentum (52-week) | Safety (debt + cash flow)

Style presets adjust factor weights:
  balanced (default) | value | growth | quality

Usage:
  python3 fetch_data.py --sector Technology --style growth
  python3 fetch_data.py --sector "Financial Services" --style value
  python3 fetch_data.py --tickers AAPL MSFT NVDA --pe 40 --roe 10
  python3 fetch_data.py --region hk --sector Technology --style quality
"""

import sys
import csv
import argparse
import time
import math
from collections import Counter

# Hang Seng Index — major constituents
HSI_TICKERS = [
    "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0011.HK", "0016.HK", "0017.HK",
    "0027.HK", "0066.HK", "0101.HK", "0175.HK", "0241.HK", "0267.HK", "0288.HK",
    "0291.HK", "0386.HK", "0388.HK", "0669.HK", "0700.HK", "0762.HK", "0823.HK",
    "0857.HK", "0868.HK", "0883.HK", "0939.HK", "0941.HK", "0960.HK", "0968.HK",
    "1038.HK", "1044.HK", "1093.HK", "1109.HK", "1113.HK", "1177.HK", "1211.HK",
    "1299.HK", "1378.HK", "1398.HK", "1810.HK", "1876.HK", "1928.HK", "1997.HK",
    "2007.HK", "2018.HK", "2020.HK", "2269.HK", "2313.HK", "2318.HK", "2319.HK",
    "2331.HK", "2382.HK", "2388.HK", "2628.HK", "3328.HK", "3690.HK", "3968.HK",
    "3988.HK", "6098.HK", "6862.HK", "9618.HK", "9633.HK", "9888.HK", "9961.HK",
    "9988.HK", "9999.HK",
]

# Hang Seng TECH Index
HSTECH_TICKERS = [
    "0268.HK", "0285.HK", "0522.HK", "0700.HK", "0772.HK", "0909.HK", "0981.HK",
    "0992.HK", "1024.HK", "1347.HK", "1810.HK", "1833.HK", "2013.HK", "2018.HK",
    "2269.HK", "2382.HK", "3690.HK", "3888.HK", "6060.HK", "6618.HK", "6690.HK",
    "9618.HK", "9626.HK", "9888.HK", "9961.HK", "9988.HK", "9999.HK",
]

# Yahoo Finance sector names (used by EquityQuery)
VALID_SECTORS = {
    "Basic Materials", "Communication Services", "Consumer Cyclical",
    "Consumer Defensive", "Energy", "Financial Services", "Healthcare",
    "Industrials", "Real Estate", "Technology", "Utilities",
}


# Style presets: factor weights (must sum to 100)
STYLE_PRESETS = {
    "balanced": {"valuation": 25, "profitability": 25, "growth": 20, "momentum": 15, "safety": 15},
    "value":    {"valuation": 40, "profitability": 20, "growth": 10, "momentum": 10, "safety": 20},
    "growth":   {"valuation": 10, "profitability": 15, "growth": 40, "momentum": 25, "safety": 10},
    "quality":  {"valuation": 15, "profitability": 35, "growth": 15, "momentum": 10, "safety": 25},
}


def resolve_sector(user_input):
    """Resolve user's sector input to a valid Yahoo Finance sector name.

    Yahoo Finance only accepts these 11 sector names. The caller (LLM) is
    responsible for mapping user intent to the correct sector name. This
    function does case-insensitive and substring matching as a convenience.
    """
    if not user_input:
        return None
    # Exact match (case-insensitive)
    for s in VALID_SECTORS:
        if user_input.lower() == s.lower():
            return s
    # Substring match
    for s in VALID_SECTORS:
        if user_input.lower() in s.lower() or s.lower() in user_input.lower():
            return s
    print(f"[screener] Warning: sector '{user_input}' not recognized. "
          f"Valid: {', '.join(sorted(VALID_SECTORS))}. "
          f"Use --industry for sub-sectors or --tickers for specific stocks.",
          file=sys.stderr)
    return None


def _compute_valuation_scores(stocks_data, max_pe):
    """Compute relative valuation scores using z-scores within the result set.

    Uses composite of PE and EV/EBITDA. Lower values = higher score.
    Returns dict of ticker -> valuation score (0-1).
    """
    # Collect valid PE and EV/EBITDA values
    pe_values = {}
    ev_values = {}
    for d in stocks_data:
        t = d["ticker"]
        if d["pe"] and d["pe"] > 0:
            pe_values[t] = d["pe"]
        if d["ev_ebitda"] and d["ev_ebitda"] > 0:
            ev_values[t] = d["ev_ebitda"]

    def _rank_score(values_dict):
        """Convert values to 0-1 scores where lower value = higher score."""
        if not values_dict:
            return {}
        sorted_items = sorted(values_dict.items(), key=lambda x: x[1])
        n = len(sorted_items)
        if n == 1:
            # Single stock: score based on absolute PE vs threshold
            t, v = sorted_items[0]
            if max_pe > 0:
                return {t: max(0, min(1, 1 - v / max_pe))}
            return {t: 0.5}
        scores = {}
        for rank, (t, _) in enumerate(sorted_items):
            scores[t] = 1 - rank / (n - 1)  # rank 0 (lowest PE) = 1.0
        return scores

    pe_scores = _rank_score(pe_values)
    ev_scores = _rank_score(ev_values)

    # Combine: average of available scores
    result = {}
    all_tickers = set(d["ticker"] for d in stocks_data)
    for t in all_tickers:
        components = []
        if t in pe_scores:
            components.append(pe_scores[t])
        if t in ev_scores:
            components.append(ev_scores[t])
        if components:
            result[t] = sum(components) / len(components)
        else:
            result[t] = 0.5  # neutral if no valuation data
    return result


def compute_scores(stocks_data, max_pe, min_roe, style="balanced"):
    """Compute 0-100 composite scores for all stocks using 5-factor model.

    Valuation is computed relatively (within result set).
    Other factors use absolute scaling.
    Returns list of (ticker, score) tuples.
    """
    weights = STYLE_PRESETS.get(style, STYLE_PRESETS["balanced"])

    # Phase A: compute relative valuation scores
    val_scores = _compute_valuation_scores(stocks_data, max_pe)

    results = {}
    for d in stocks_data:
        t = d["ticker"]
        score = 0.0

        # 1. Valuation (relative within set)
        score += val_scores.get(t, 0.5) * weights["valuation"]

        # 2. Profitability: ROE above threshold
        roe = d.get("roe") or 0
        if roe > 0:
            if min_roe > 0:
                prof_ratio = max(0, (roe - min_roe) / (min_roe * 2))
            else:
                prof_ratio = min(1, roe / 30)
            score += min(1, prof_ratio) * weights["profitability"]

        # 3. Growth: blend of revenue + earnings growth
        rev_g = d.get("rev_growth") or 0
        earn_g = d.get("earnings_growth") or 0
        # Use average of available; cap at 50% for scoring
        growth_vals = []
        if rev_g != 0:
            growth_vals.append(rev_g)
        if earn_g != 0:
            growth_vals.append(earn_g)
        if growth_vals:
            avg_growth = sum(growth_vals) / len(growth_vals)
            growth_ratio = max(0, min(1, avg_growth / 50))
            score += growth_ratio * weights["growth"]

        # 4. Momentum: 52-week price change
        mom = d.get("momentum_52w") or 0
        # -30% to +80% mapped to 0-1
        mom_ratio = max(0, min(1, (mom + 30) / 110))
        score += mom_ratio * weights["momentum"]

        # 5. Safety: debt/equity (lower = safer) + cash flow quality (higher = safer)
        safety_components = []
        de = d.get("debt_to_equity")
        if de is not None and de >= 0:
            # D/E 0-200: lower is better
            de_score = max(0, min(1, 1 - de / 200))
            safety_components.append(de_score)
        ocf = d.get("ocf") or 0
        ni = d.get("net_income") or 0
        if ni > 0 and ocf > 0:
            # OCF/NI ratio: >1.0 = good cash quality
            cf_quality = min(1, ocf / ni / 1.5)
            safety_components.append(cf_quality)
        if safety_components:
            safety_score = sum(safety_components) / len(safety_components)
        else:
            safety_score = 0.5  # neutral if no data
        score += safety_score * weights["safety"]

        results[t] = round(score, 1)

    return results


def _extract_stock_data(info, quote=None):
    """Extract standardized stock data from yfinance info dict."""
    ticker = info.get("symbol") or (quote or {}).get("symbol", "")
    pe = info.get("trailingPE") or info.get("forwardPE")
    forward_pe = info.get("forwardPE")
    ev_ebitda = info.get("enterpriseToEbitda")
    roe_raw = info.get("returnOnEquity")
    roe = (roe_raw or 0) * 100
    mcap = info.get("marketCap") or (quote or {}).get("marketCap") or 0
    rev_growth = (info.get("revenueGrowth") or 0) * 100
    earnings_growth = (info.get("earningsGrowth") or 0) * 100
    momentum_52w = (info.get("52WeekChange") or 0) * 100
    debt_to_equity = info.get("debtToEquity")
    ocf = info.get("operatingCashflow") or 0
    net_income = info.get("netIncomeToCommon") or 0
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
        "forward_pe": forward_pe,
        "ev_ebitda": ev_ebitda,
        "roe": roe,
        "mcap": mcap,
        "rev_growth": rev_growth,
        "earnings_growth": earnings_growth,
        "momentum_52w": momentum_52w,
        "debt_to_equity": debt_to_equity,
        "ocf": ocf,
        "net_income": net_income,
    }


def _normalize_company_name(name):
    """Normalize company name for deduplication grouping.

    Strips punctuation, suffixes, and whitespace differences so that
    'Novo-Nordisk A/S' and 'Novo Nordisk A/S' group together.
    """
    import re
    n = name.strip().lower()
    # Remove common suffixes
    for suffix in [" inc.", " inc", " ltd.", " ltd", " corp.", " corp",
                   " co.", " co", " plc", " s.a.", " sa", " ag", " a/s",
                   " se", " nv", " n.v.", " lp", " llc"]:
        if n.endswith(suffix):
            n = n[:-len(suffix)]
    # Remove punctuation and normalize whitespace
    n = re.sub(r'[^a-z0-9\s]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n


def _deduplicate(stocks_data):
    """Remove duplicate listings of the same company.

    Yahoo Finance returns multiple tickers for the same company (e.g., ADR + OTC
    foreign ordinary + OTC pink sheets). Group by normalized company name and keep
    only the best representative ticker per company.

    Tie-breaking: highest market cap wins. When market caps are within 5% of each
    other, prefer the shorter ticker (typically the primary exchange listing).
    """
    from collections import defaultdict
    groups = defaultdict(list)
    for d in stocks_data:
        key = _normalize_company_name(d["name"])
        groups[key].append(d)

    deduped = []
    removed = 0
    for key, entries in groups.items():
        if len(entries) == 1:
            deduped.append(entries[0])
        else:
            # Sort by market cap descending
            entries.sort(key=lambda x: x.get("mcap") or 0, reverse=True)
            best = entries[0]
            top_mcap = best.get("mcap") or 0
            # Among entries within 5% of top market cap, prefer shorter ticker
            if top_mcap > 0:
                close = [e for e in entries
                         if (e.get("mcap") or 0) >= top_mcap * 0.95]
                if len(close) > 1:
                    best = min(close, key=lambda x: len(x["ticker"]))
            deduped.append(best)
            removed += len(entries) - 1

    if removed:
        print(f"[screener] Deduplicated: {removed} duplicate listings removed", file=sys.stderr)

    return deduped


def _format_result(data, score):
    """Format extracted stock data into output row."""
    return {
        "ticker": data["ticker"],
        "name": data["name"],
        "sector": data["sector"] or "N/A",
        "industry": data["industry"] or "N/A",
        "price": round(data["price"], 2),
        "market_cap_B": round(data["mcap"] / 1e9, 1) if data["mcap"] else 0,
        "pe": round(data["pe"], 1) if data["pe"] else "",
        "forward_pe": round(data["forward_pe"], 1) if data["forward_pe"] else "",
        "ev_ebitda": round(data["ev_ebitda"], 1) if data["ev_ebitda"] else "",
        "roe_pct": round(data["roe"], 1),
        "revenue_growth_pct": round(data["rev_growth"], 1),
        "earnings_growth_pct": round(data["earnings_growth"], 1),
        "momentum_52w_pct": round(data["momentum_52w"], 1),
        "debt_equity": round(data["debt_to_equity"], 1) if data["debt_to_equity"] is not None else "",
        "score": score,
    }


def screen_server_side(region="us", sector=None, max_pe=20, min_roe=15,
                       min_market_cap=1e9, top=25):
    """Phase 1: Server-side screening via Yahoo Finance EquityQuery."""
    import yfinance as yf

    conditions = []
    conditions.append(yf.EquityQuery('eq', ['region', region]))

    if sector:
        resolved = resolve_sector(sector)
        if resolved:
            conditions.append(yf.EquityQuery('eq', ['sector', resolved]))
            print(f"[screener] Server-side filter: sector={resolved}", file=sys.stderr)
        else:
            print(f"[screener] Skipping sector filter (unresolved)", file=sys.stderr)

    if max_pe > 0:
        conditions.append(yf.EquityQuery('btwn', ['peratio.lasttwelvemonths', 0, max_pe]))

    if min_roe > 0:
        conditions.append(yf.EquityQuery('gt', ['returnonequity.lasttwelvemonths', min_roe / 100]))

    if min_market_cap > 0:
        conditions.append(yf.EquityQuery('gt', ['intradaymarketcap', min_market_cap]))

    query = yf.EquityQuery('and', conditions)
    print(f"[screener] Running server-side screen (region={region})...", file=sys.stderr)

    try:
        result = yf.screen(query, sortField='intradaymarketcap', sortAsc=False,
                           size=min(top, 250))
    except Exception as e:
        print(f"[screener] Server-side screen failed: {e}", file=sys.stderr)
        return [], 0

    total = result.get('total', 0)
    quotes = result.get('quotes', [])
    print(f"[screener] Server returned {len(quotes)} stocks (total matching: {total})", file=sys.stderr)

    return quotes, total


def enrich_with_details(quotes, max_pe, min_roe, min_market_cap=0,
                        industry_filter=None, style="balanced"):
    """Phase 2: Fetch detailed data and score candidates."""
    import yfinance as yf

    all_data = []
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

            if industry_filter:
                if industry_filter.lower() not in data["industry"].lower():
                    skipped_industry += 1
                    continue

            # Re-validate filters
            if max_pe > 0 and data["pe"] is not None and data["pe"] >= max_pe:
                skipped_revalidation += 1
                continue
            if min_roe > 0 and data["roe"] <= min_roe:
                skipped_revalidation += 1
                continue
            if min_market_cap > 0 and data["mcap"] <= min_market_cap:
                skipped_revalidation += 1
                continue

            all_data.append(data)
        except Exception as e:
            print(f"[screener] Skip {ticker}: {e}", file=sys.stderr)
            continue
        time.sleep(0.05)

    if industry_filter and skipped_industry:
        print(f"[screener] Industry filter '{industry_filter}': {skipped_industry} skipped", file=sys.stderr)
    if skipped_revalidation:
        print(f"[screener] Re-validation: {skipped_revalidation} removed", file=sys.stderr)

    if not all_data:
        return []

    all_data = _deduplicate(all_data)

    # Compute scores for all candidates together (relative valuation)
    scores = compute_scores(all_data, max_pe, min_roe, style)
    results = []
    for d in all_data:
        score = scores.get(d["ticker"], 0)
        results.append(_format_result(d, score))

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def screen_custom_tickers(tickers, max_pe=20, min_roe=15, min_market_cap=1e9,
                          sector_filter=None, industry_filter=None, style="balanced"):
    """Screen a custom list of tickers."""
    import yfinance as yf

    all_data = []
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

            if sector_filter:
                resolved = resolve_sector(sector_filter) or sector_filter
                sf = resolved.lower()
                ss = data["sector"].lower()
                if sf not in ss and ss not in sf:
                    continue

            if industry_filter:
                if industry_filter.lower() not in data["industry"].lower():
                    continue

            passes = True
            if max_pe > 0 and data["pe"] is not None and data["pe"] >= max_pe:
                passes = False
            if min_roe > 0 and data["roe"] <= min_roe:
                passes = False
            if min_market_cap > 0 and data["mcap"] <= min_market_cap:
                passes = False

            if passes:
                all_data.append(data)
        except Exception as e:
            print(f"{e}", file=sys.stderr)
            continue
        time.sleep(0.05)

    if not all_data:
        return []

    all_data = _deduplicate(all_data)

    scores = compute_scores(all_data, max_pe, min_roe, style)
    results = []
    for d in all_data:
        score = scores.get(d["ticker"], 0)
        results.append(_format_result(d, score))

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Multi-factor stock screener v2")
    parser.add_argument("--region", default="us",
                        help="Market region: us, hk, gb, jp, etc. (default: us)")
    parser.add_argument("--index",
                        help="Predefined index universe (e.g., hsi, hstech)")
    parser.add_argument("--tickers", nargs="+",
                        help="Custom ticker list (e.g., AAPL MSFT or 0700.HK)")
    parser.add_argument("--sector",
                        help="Sector filter (e.g., Technology, Healthcare)")
    parser.add_argument("--industry",
                        help="Industry sub-filter, partial match")
    parser.add_argument("--pe", type=float, default=20,
                        help="Max P/E ratio; 0 to disable (default: 20)")
    parser.add_argument("--roe", type=float, default=15,
                        help="Min ROE %%; 0 to disable (default: 15)")
    parser.add_argument("--mcap", type=float, default=1.0,
                        help="Min market cap in $B; 0 to disable (default: 1)")
    parser.add_argument("--top", type=int, default=25,
                        help="Max results from server-side screen (default: 25)")
    parser.add_argument("--style", choices=list(STYLE_PRESETS.keys()),
                        default="balanced",
                        help="Scoring style preset (default: balanced)")
    parser.add_argument("--output", default="screener_results.csv")
    args = parser.parse_args()

    use_custom = args.tickers or args.index

    if use_custom:
        if args.tickers:
            tickers = args.tickers
            label = f"custom ({len(tickers)} tickers)"
        elif args.index:
            index_map = {
                "hsi": (HSI_TICKERS, "Hang Seng Index"),
                "hstech": (HSTECH_TICKERS, "Hang Seng Tech"),
            }
            if args.index.lower() in index_map:
                tickers, idx_name = index_map[args.index.lower()]
                label = f"{idx_name} ({len(tickers)} tickers)"
            else:
                print(f"[screener] Unknown index '{args.index}'. "
                      f"Known: {', '.join(index_map.keys())}. "
                      f"Use --tickers for custom lists.", file=sys.stderr)
                sys.exit(1)

        if not tickers:
            print("[screener] ERROR: No tickers in universe.", file=sys.stderr)
            sys.exit(1)

        print(f"[screener] Mode: {label}", file=sys.stderr)
        results = screen_custom_tickers(
            tickers,
            max_pe=args.pe, min_roe=args.roe,
            min_market_cap=args.mcap * 1e9,
            sector_filter=args.sector, industry_filter=args.industry,
            style=args.style,
        )
    else:
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
            min_market_cap=args.mcap * 1e9,
            industry_filter=args.industry,
            style=args.style,
        )

    if not results:
        print("No stocks passed all filters.")
        return

    # Write CSV
    fieldnames = ["ticker", "name", "sector", "industry", "price",
                  "market_cap_B", "pe", "forward_pe", "ev_ebitda",
                  "roe_pct", "revenue_growth_pct", "earnings_growth_pct",
                  "momentum_52w_pct", "debt_equity", "score"]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # --- Formatted output report ---
    weights = STYLE_PRESETS[args.style]
    print(f"\n{'=' * 90}")
    print("SCREENING RESULTS")
    print(f"{'=' * 90}")

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
    print(f"Style:   {args.style} | Results: {len(results)} stocks passed")
    print(f"Output:  {args.output}")

    # Scoring methodology
    print(f"\nScoring ({args.style}): "
          f"Valuation({weights['valuation']}%) + "
          f"Profitability({weights['profitability']}%) + "
          f"Growth({weights['growth']}%) + "
          f"Momentum({weights['momentum']}%) + "
          f"Safety({weights['safety']}%) = 0-100")
    print(f"  Valuation:     Composite PE + EV/EBITDA, relative within result set")
    print(f"  Profitability: ROE above threshold")
    print(f"  Growth:        Revenue + earnings growth blend")
    print(f"  Momentum:      52-week price change")
    print(f"  Safety:        Low debt/equity + strong cash flow quality")

    # Formatted table
    print(f"\n{'Rank':<5} {'Ticker':<8} {'Company':<28} {'Industry':<20} "
          f"{'P/E':>6} {'EV/EB':>6} {'ROE%':>6} {'Grw%':>6} {'Mom%':>6} "
          f"{'D/E':>6} {'MCap$B':>7} {'Score':>6}")
    print(f"{'-' * 5} {'-' * 8} {'-' * 28} {'-' * 20} "
          f"{'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} {'-' * 6} "
          f"{'-' * 6} {'-' * 7} {'-' * 6}")

    for i, r in enumerate(results[:20], 1):
        pe_str = f"{r['pe']:.1f}" if r['pe'] != '' else '-'
        ev_str = f"{r['ev_ebitda']:.1f}" if r['ev_ebitda'] != '' else '-'
        de_str = f"{r['debt_equity']:.1f}" if r['debt_equity'] != '' else '-'
        # Growth: average of revenue + earnings
        rev_g = r['revenue_growth_pct']
        earn_g = r['earnings_growth_pct']
        if rev_g and earn_g:
            grw = (rev_g + earn_g) / 2
        else:
            grw = rev_g or earn_g or 0
        print(f"{i:<5} {r['ticker']:<8} {r['name'][:27]:<28} {r['industry'][:19]:<20} "
              f"{pe_str:>6} {ev_str:>6} {r['roe_pct']:>5.1f}% {grw:>5.1f}% "
              f"{r['momentum_52w_pct']:>5.1f}% {de_str:>6} {r['market_cap_B']:>7.1f} "
              f"{r['score']:>6.1f}")

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

    print(f"\n{'=' * 90}")


if __name__ == "__main__":
    main()
