#!/usr/bin/env python3
"""
portfolio-monitor: Portfolio diagnostics — sector exposure, risk decomposition,
benchmark comparison, and concentration analysis.

Usage:
    python3 scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:50"
    python3 scripts/fetch_data.py "AAPL:25 MSFT:25 GOOGL:25 AMZN:25"
    python3 scripts/fetch_data.py "0700.HK:40 9988.HK:30 1810.HK:30"
"""

import sys, os, json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
try:
    from market import detect_market, detect_portfolio_market, get_risk_free_rate
except ImportError:
    def detect_market(ticker): return "US"
    def detect_portfolio_market(tickers): return "US"
    def get_risk_free_rate(market): return 0.045

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"ERROR: Missing dependency — {e}. Run: pip install yfinance pandas numpy", file=sys.stderr)
    sys.exit(1)


# Benchmark index per market
BENCHMARKS = {
    "US": "SPY",
    "HK": "2800.HK",
    "CN": "510300.SS",
    "JP": "1306.T",
    "UK": "ISF.L",
}


def parse_portfolio(input_str):
    """Parse 'AAPL:30 MSFT:20 NVDA:50' into {AAPL: 30, MSFT: 20, NVDA: 50}."""
    holdings = {}
    for part in input_str.strip().split():
        if ":" in part:
            sym, weight = part.split(":", 1)
            holdings[sym.upper()] = float(weight)
        else:
            holdings[part.upper()] = 1.0
    return holdings


def normalize_weights(weights):
    total = sum(weights.values())
    if total == 0:
        return {k: 1.0 / len(weights) for k in weights}
    return {k: round(v / total, 6) for k, v in weights.items()}


def fetch_price_history(tickers, days=365):
    """Fetch daily adjusted close prices for all tickers."""
    end = datetime.today()
    start = end - timedelta(days=days + 30)
    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
        if data.empty:
            return pd.DataFrame()
        if isinstance(data.columns, pd.MultiIndex):
            prices = data["Close"]
        else:
            prices = data[["Close"]].rename(columns={"Close": tickers[0]}) if len(tickers) == 1 else data
        return prices.dropna(how="all")
    except Exception as e:
        print(f"WARN: Failed to fetch price history: {e}", file=sys.stderr)
        return pd.DataFrame()


def compute_period_return(prices, period_days):
    """Compute period return (%) for each ticker. Handles cross-market NaN gaps."""
    if prices.empty or len(prices) < min(period_days, 5):
        return {}
    result = {}
    for col in prices.columns:
        series = prices[col].dropna()
        if len(series) < min(period_days, 5):
            continue
        idx = max(-period_days, -len(series))
        recent = series.iloc[-1]
        past = series.iloc[idx]
        if past != 0 and not np.isnan(past) and not np.isnan(recent):
            result[col] = round(float((recent - past) / past * 100), 2)
    return result


def compute_max_drawdown(portfolio_values):
    """Max drawdown from a portfolio value series."""
    if portfolio_values.empty or len(portfolio_values) < 2:
        return None
    peak = portfolio_values.expanding().max()
    drawdown = (portfolio_values - peak) / peak
    return round(float(drawdown.min()) * 100, 2)


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:50"', file=sys.stderr)
        sys.exit(1)

    raw_input = " ".join(sys.argv[1:])
    raw_weights = parse_portfolio(raw_input)
    weights = normalize_weights(raw_weights)
    tickers = list(weights.keys())
    market = detect_portfolio_market(tickers)
    benchmark = BENCHMARKS.get(market, "SPY")

    print(f"Portfolio: {', '.join(f'{t}:{w*100:.1f}%' for t, w in weights.items())}", file=sys.stderr)
    print(f"Benchmark: {benchmark} | Market: {market}", file=sys.stderr)

    # ── Fetch price data (portfolio + benchmark) ─────────────────────────
    all_tickers = tickers + [benchmark]
    prices = fetch_price_history(all_tickers, days=365)

    # ── Individual holdings info ─────────────────────────────────────────
    holdings = {}
    sector_weights = {}  # sector → total weight

    for sym in tickers:
        print(f"  Fetching {sym}...", file=sys.stderr)
        t = yf.Ticker(sym)
        info = t.info
        price = None
        try:
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if price:
                price = round(float(price), 2)
        except Exception:
            pass

        sector = info.get("sector", "Unknown")
        w = weights[sym]

        holdings[sym] = {
            "name": (info.get("longName") or info.get("shortName", sym))[:30],
            "weight_pct": round(w * 100, 2),
            "price": price,
            "sector": sector,
            "market": detect_market(sym),
        }

        # Aggregate sector weights
        sector_weights[sector] = round(sector_weights.get(sector, 0) + w * 100, 2)

    # ── Per-holding returns ──────────────────────────────────────────────
    if not prices.empty:
        for period_name, days in [("return_1m_pct", 21), ("return_3m_pct", 63), ("return_1y_pct", 252)]:
            ret = compute_period_return(prices, days)
            for sym in tickers:
                if sym in ret:
                    holdings[sym][period_name] = ret[sym]

    # ── Portfolio daily returns & metrics ─────────────────────────────────
    available = [t for t in tickers if t in prices.columns]
    port_daily = None
    bench_daily = None
    correlation_matrix = {}
    vol_contributions = {}
    portfolio_vol = None
    portfolio_sharpe = None
    portfolio_drawdown = None
    benchmark_data = {}

    if not prices.empty and available:
        # Forward-fill cross-market NaN gaps (HK closed on US trading days etc.)
        daily_returns = prices[available].ffill().pct_change(fill_method=None).dropna()

        # Portfolio daily return series (weighted)
        w_vec = np.array([weights[t] for t in available])
        port_daily = (daily_returns[available] * w_vec).sum(axis=1)

        # Portfolio cumulative value (for drawdown)
        port_cumulative = (1 + port_daily).cumprod()
        portfolio_drawdown = compute_max_drawdown(port_cumulative)

        # Portfolio volatility (annualized)
        if len(available) > 1:
            cov_matrix = daily_returns[available].cov().values * 252
            port_variance = float(w_vec @ cov_matrix @ w_vec)
            portfolio_vol = round(np.sqrt(port_variance) * 100, 2)

            # Correlation matrix
            corr = daily_returns[available].corr().round(3)
            correlation_matrix = {row: {col: corr.loc[row, col] for col in corr.columns}
                                  for row in corr.index}

            # Volatility contributions (component VaR)
            marginal = cov_matrix @ w_vec
            contributions = w_vec * marginal
            total_var = contributions.sum()
            for i, sym in enumerate(available):
                vol_contributions[sym] = round(float(contributions[i] / total_var * 100), 2) if total_var else 0
        else:
            # Single stock portfolio
            portfolio_vol = round(float(daily_returns[available[0]].std() * np.sqrt(252) * 100), 2)

        # Sharpe ratio
        rf_rate = get_risk_free_rate(market)
        if portfolio_vol and portfolio_vol > 0:
            annual_return = float(port_daily.mean() * 252 * 100)
            portfolio_sharpe = round((annual_return - rf_rate * 100) / portfolio_vol, 2)

        # ── Benchmark comparison ─────────────────────────────────────────
        # If benchmark download failed, try fetching it separately
        if benchmark not in prices.columns:
            try:
                bench_prices = fetch_price_history([benchmark], days=365)
                if not bench_prices.empty and benchmark in bench_prices.columns:
                    prices = prices.join(bench_prices[[benchmark]], how="outer")
            except Exception:
                pass

        if benchmark in prices.columns and prices[benchmark].dropna().shape[0] > 20:
            bench_returns = prices[benchmark].pct_change(fill_method=None).dropna()
            bench_cumulative = (1 + bench_returns).cumprod()
            bench_vol = round(float(bench_returns.std() * np.sqrt(252) * 100), 2)
            bench_annual_return = float(bench_returns.mean() * 252 * 100)
            bench_sharpe = round((bench_annual_return - rf_rate * 100) / bench_vol, 2) if bench_vol > 0 else None
            bench_drawdown = compute_max_drawdown(bench_cumulative)

            # Portfolio vs benchmark returns
            bench_ret = compute_period_return(prices[[benchmark]], 252)
            bench_1y = bench_ret.get(benchmark)

            # Correlation of portfolio to benchmark
            if port_daily is not None:
                aligned = pd.DataFrame({"port": port_daily, "bench": bench_returns}).dropna()
                port_bench_corr = round(float(aligned["port"].corr(aligned["bench"])), 3) if len(aligned) > 20 else None
            else:
                port_bench_corr = None

            benchmark_data = {
                "ticker": benchmark,
                "return_1y_pct": bench_1y,
                "volatility_pct": bench_vol,
                "sharpe_ratio": bench_sharpe,
                "max_drawdown_pct": bench_drawdown,
                "correlation_to_portfolio": port_bench_corr,
            }

    # ── Portfolio-level weighted returns ──────────────────────────────────
    port_ret = {}
    for period_name in ["return_1m_pct", "return_3m_pct", "return_1y_pct"]:
        val = sum(weights[t] * (holdings[t].get(period_name) or 0) for t in tickers)
        port_ret[period_name] = round(val, 2)

    # ── Concentration (HHI) ──────────────────────────────────────────────
    hhi = round(sum((w * 100) ** 2 for w in weights.values()), 1)
    if hhi < 1500:
        hhi_level = "Well-diversified"
    elif hhi < 2500:
        hhi_level = "Moderately concentrated"
    else:
        hhi_level = "Highly concentrated"

    # Sector HHI
    sector_hhi = round(sum(v ** 2 for v in sector_weights.values()), 1)

    # ── Build result ─────────────────────────────────────────────────────
    result = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "market": market,
        "holdings": holdings,
        "sector_exposure": dict(sorted(sector_weights.items(), key=lambda x: x[1], reverse=True)),
        "portfolio_metrics": {
            **port_ret,
            "volatility_pct": portfolio_vol,
            "sharpe_ratio": portfolio_sharpe,
            "max_drawdown_pct": portfolio_drawdown,
        },
        "benchmark": benchmark_data,
        "correlation_matrix": correlation_matrix,
        "volatility_contributions": vol_contributions,
        "concentration": {
            "hhi": hhi,
            "hhi_level": hhi_level,
            "sector_hhi": sector_hhi,
            "top_holdings": sorted(
                [(t, round(w * 100, 2)) for t, w in weights.items()],
                key=lambda x: x[1], reverse=True
            )[:5],
        },
    }

    # ── Markdown report → stdout ─────────────────────────────────────────
    print(format_report(result, weights, tickers))

    # ── JSON → stderr (sanitize NaN → null) ──────────────────────────────
    def _sanitize(obj):
        if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
            return None
        if isinstance(obj, dict):
            return {k: _sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_sanitize(v) for v in obj]
        return obj

    print(f"\n---JSON---\n{json.dumps(_sanitize(result), indent=2, default=str)}", file=sys.stderr)


# ── Markdown Report ────────────────────────────────────────────────────────

def _fmt(v, suffix="", prefix=""):
    if v is None:
        return "—"
    try:
        if np.isnan(v) or np.isinf(v):
            return "—"
    except (TypeError, ValueError):
        pass
    return f"{prefix}{v}{suffix}"


def format_report(r, weights, tickers):
    lines = []
    lines.append("# Portfolio Diagnostics")
    lines.append(f"\n_{r['date']} | {len(tickers)} holdings | {r['market']} Market_\n")

    # ── Holdings Table ───────────────────────────────────────────────────
    lines.append("## Holdings\n")
    lines.append("| Ticker | Name | Weight | Sector | Price | 1M | 3M | 1Y |")
    lines.append("|--------|------|--------|--------|-------|-----|-----|-----|")
    for sym in sorted(tickers, key=lambda t: weights[t], reverse=True):
        h = r["holdings"][sym]
        lines.append(
            f"| **{sym}** | {h['name']} | {h['weight_pct']}% | {h['sector']} | "
            f"{_fmt(h.get('price'), prefix='$')} | "
            f"{_fmt(h.get('return_1m_pct'), suffix='%')} | "
            f"{_fmt(h.get('return_3m_pct'), suffix='%')} | "
            f"{_fmt(h.get('return_1y_pct'), suffix='%')} |"
        )

    # ── Portfolio vs Benchmark ───────────────────────────────────────────
    pm = r["portfolio_metrics"]
    bm = r.get("benchmark", {})
    lines.append("\n## Performance vs Benchmark\n")
    lines.append(f"| Metric | Portfolio | {bm.get('ticker', 'Benchmark')} | Delta |")
    lines.append("|--------|-----------|-----------|-------|")

    def delta(a, b):
        if a is not None and b is not None:
            d = round(a - b, 2)
            return f"{d:+.2f}"
        return "—"

    lines.append(f"| Return (1Y) | {_fmt(pm.get('return_1y_pct'), suffix='%')} | {_fmt(bm.get('return_1y_pct'), suffix='%')} | {delta(pm.get('return_1y_pct'), bm.get('return_1y_pct'))} |")
    lines.append(f"| Volatility | {_fmt(pm.get('volatility_pct'), suffix='%')} | {_fmt(bm.get('volatility_pct'), suffix='%')} | {delta(pm.get('volatility_pct'), bm.get('volatility_pct'))} |")
    lines.append(f"| Sharpe Ratio | {_fmt(pm.get('sharpe_ratio'))} | {_fmt(bm.get('sharpe_ratio'))} | {delta(pm.get('sharpe_ratio'), bm.get('sharpe_ratio'))} |")
    lines.append(f"| Max Drawdown | {_fmt(pm.get('max_drawdown_pct'), suffix='%')} | {_fmt(bm.get('max_drawdown_pct'), suffix='%')} | {delta(pm.get('max_drawdown_pct'), bm.get('max_drawdown_pct'))} |")

    if bm.get("correlation_to_portfolio") is not None:
        lines.append(f"\nPortfolio–Benchmark correlation: **{bm['correlation_to_portfolio']}**")

    # ── Sector Exposure ──────────────────────────────────────────────────
    lines.append("\n## Sector Exposure\n")
    lines.append("| Sector | Weight | Holdings |")
    lines.append("|--------|--------|----------|")
    sector_holdings = {}
    for sym in tickers:
        s = r["holdings"][sym]["sector"]
        sector_holdings.setdefault(s, []).append(sym)
    for sector, weight in r["sector_exposure"].items():
        syms = ", ".join(sector_holdings.get(sector, []))
        bar = "█" * int(weight / 5) if weight > 0 else ""
        lines.append(f"| {sector} | {weight}% {bar} | {syms} |")

    conc = r["concentration"]
    lines.append(f"\nSector HHI: **{conc['sector_hhi']}** — {'Concentrated' if conc['sector_hhi'] > 2500 else 'Diversified' if conc['sector_hhi'] < 1500 else 'Moderate'}")

    # ── Risk Decomposition ───────────────────────────────────────────────
    if r["volatility_contributions"]:
        lines.append("\n## Risk Decomposition\n")
        lines.append("| Ticker | Weight | Vol Contribution | Over/Under |")
        lines.append("|--------|--------|------------------|------------|")
        for sym in sorted(r["volatility_contributions"], key=lambda t: r["volatility_contributions"][t], reverse=True):
            w_pct = r["holdings"][sym]["weight_pct"]
            vc = r["volatility_contributions"][sym]
            diff = round(vc - w_pct, 1)
            flag = f"{diff:+.1f}pp" if abs(diff) > 2 else "≈"
            lines.append(f"| **{sym}** | {w_pct}% | {vc}% | {flag} |")

        lines.append(f"\nPortfolio volatility: **{_fmt(pm.get('volatility_pct'), suffix='%')}** annualized")

    # ── Correlation Matrix ───────────────────────────────────────────────
    if r["correlation_matrix"] and len(r["correlation_matrix"]) > 1:
        syms = list(r["correlation_matrix"].keys())
        lines.append("\n## Correlation Matrix\n")
        header = "| | " + " | ".join(syms) + " |"
        sep = "|---|" + "|".join(["---"] * len(syms)) + "|"
        lines.append(header)
        lines.append(sep)
        for row in syms:
            vals = " | ".join(str(r["correlation_matrix"][row].get(col, "—")) for col in syms)
            lines.append(f"| **{row}** | {vals} |")

        # Flag high correlations
        high_pairs = []
        for i, a in enumerate(syms):
            for b in syms[i+1:]:
                c = r["correlation_matrix"].get(a, {}).get(b)
                if c is not None and c > 0.8:
                    high_pairs.append((a, b, c))
        if high_pairs:
            lines.append("\n**High correlations (>0.8):**")
            for a, b, c in high_pairs:
                lines.append(f"- {a} ↔ {b}: {c} — minimal diversification benefit")

    # ── Concentration ────────────────────────────────────────────────────
    lines.append("\n## Concentration\n")
    lines.append(f"- **HHI**: {conc['hhi']} — {conc['hhi_level']}")
    lines.append(f"- **Top holding**: {conc['top_holdings'][0][0]} at {conc['top_holdings'][0][1]}%")
    if len(conc['top_holdings']) >= 3:
        top3_w = sum(h[1] for h in conc['top_holdings'][:3])
        lines.append(f"- **Top 3**: {top3_w:.1f}% of portfolio")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
