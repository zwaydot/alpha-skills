#!/usr/bin/env python3
"""
portfolio-monitor: Parse TICKER:WEIGHT input, compute correlations and volatility contributions.

Usage:
    python3 scripts/fetch_data.py "AAPL:30 MSFT:20 NVDA:50"
    python3 scripts/fetch_data.py "AAPL:25 MSFT:25 GOOGL:25 AMZN:25"
    python3 scripts/fetch_data.py "AAPL:40 NVDA:30 MSFT:30" > portfolio.json
"""

import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
try:
    from market import detect_portfolio_market, get_risk_free_rate
except ImportError:
    def detect_portfolio_market(tickers): return "US"
    def get_risk_free_rate(market): return 0.045

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"ERROR: Missing dependency — {e}. Run: pip install yfinance pandas numpy")
    sys.exit(1)


def parse_portfolio(input_str: str) -> dict:
    """Parse 'AAPL:30 MSFT:20 NVDA:50' into {AAPL: 30, MSFT: 20, NVDA: 50}."""
    holdings = {}
    for part in input_str.strip().split():
        if ":" in part:
            sym, weight = part.split(":", 1)
            holdings[sym.upper()] = float(weight)
        else:
            holdings[part.upper()] = 1.0  # equal weight placeholder
    return holdings


def normalize_weights(weights: dict) -> dict:
    total = sum(weights.values())
    if total == 0:
        return {k: 1.0 / len(weights) for k in weights}
    return {k: v / total for k, v in weights.items()}


def fetch_price_history(tickers: list, days: int = 365) -> pd.DataFrame:
    """Fetch daily adjusted close prices for all tickers."""
    end = datetime.today()
    start = end - timedelta(days=days + 30)
    try:
        data = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            prices = data["Close"]
        else:
            prices = data[["Close"]] if "Close" in data else data
        return prices.dropna(how="all")
    except Exception as e:
        print(f"WARN: Failed to fetch price history: {e}", file=sys.stderr)
        return pd.DataFrame()


def compute_returns(prices: pd.DataFrame, period_days: int) -> pd.Series:
    """Compute period return for each ticker."""
    if len(prices) < period_days:
        return pd.Series(dtype=float)
    recent = prices.iloc[-1]
    past = prices.iloc[-period_days] if len(prices) >= period_days else prices.iloc[0]
    return ((recent - past) / past * 100).round(2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fetch_data.py \"AAPL:30 MSFT:20 NVDA:50\"", file=sys.stderr)
        sys.exit(1)

    raw_input = " ".join(sys.argv[1:])
    raw_weights = parse_portfolio(raw_input)
    weights = normalize_weights(raw_weights)
    tickers = list(weights.keys())

    print(f"Portfolio: {', '.join(f'{t}:{w*100:.1f}%' for t, w in weights.items())}", file=sys.stderr)
    print(f"Fetching price data for {len(tickers)} holdings...", file=sys.stderr)

    # Fetch price history (1 year)
    prices = fetch_price_history(tickers, days=365)

    # Handle single ticker (returns Series not DataFrame)
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    # Individual ticker info
    holdings_data = {}
    for sym in tickers:
        t = yf.Ticker(sym)
        info = t.info
        current_price = None
        try:
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            if current_price:
                current_price = round(float(current_price), 2)
        except Exception:
            pass

        holdings_data[sym] = {
            "ticker": sym,
            "name": info.get("longName") or info.get("shortName", sym),
            "weight_pct": round(weights[sym] * 100, 2),
            "current_price": current_price,
            "sector": info.get("sector"),
        }

    # Returns
    if not prices.empty:
        ret_1m = compute_returns(prices, 21)
        ret_3m = compute_returns(prices, 63)
        ret_1y = compute_returns(prices, 252)

        for sym in tickers:
            if sym in holdings_data:
                for key, ret_series in [("return_1m_pct", ret_1m), ("return_3m_pct", ret_3m), ("return_1y_pct", ret_1y)]:
                    val = ret_series.get(sym) if sym in ret_series else None
                    holdings_data[sym][key] = round(float(val), 2) if val is not None and not np.isnan(val) else None

    # Correlation matrix
    correlation_matrix = {}
    vol_contributions = {}
    portfolio_vol = None

    if not prices.empty and len(tickers) > 1:
        # Align columns to tickers
        available = [t for t in tickers if t in prices.columns]
        if available:
            daily_returns = prices[available].pct_change().dropna()

            # Correlation
            corr = daily_returns.corr().round(3)
            correlation_matrix = corr.to_dict()

            # Portfolio variance / volatility
            w_vec = np.array([weights[t] for t in available])
            cov_matrix = daily_returns.cov().values * 252  # annualized
            port_variance = float(w_vec @ cov_matrix @ w_vec)
            portfolio_vol = round(np.sqrt(port_variance) * 100, 2)

            # Marginal contribution to portfolio variance
            marginal = cov_matrix @ w_vec
            contributions = w_vec * marginal
            total_var = contributions.sum()
            for i, sym in enumerate(available):
                vol_contributions[sym] = round(float(contributions[i] / total_var * 100), 2) if total_var else None

    # Sharpe ratio estimate (annualized, market-aware risk-free rate)
    market = detect_portfolio_market(tickers)
    rf_rate = get_risk_free_rate(market) * 100  # convert to percentage
    sharpe_ratio = None
    if not prices.empty and len(tickers) > 1 and portfolio_vol and portfolio_vol > 0:
        try:
            available = [t for t in tickers if t in prices.columns]
            if available:
                daily_returns = prices[available].pct_change().dropna()
                w_vec = np.array([weights[t] for t in available])
                port_daily = (daily_returns * w_vec).sum(axis=1)
                annual_return = float(port_daily.mean() * 252 * 100)
                sharpe_ratio = round((annual_return - rf_rate) / portfolio_vol, 2)
        except Exception:
            pass

    # Portfolio-level weighted returns
    port_ret_1m = sum(weights[t] * (holdings_data[t].get("return_1m_pct") or 0) for t in tickers)
    port_ret_3m = sum(weights[t] * (holdings_data[t].get("return_3m_pct") or 0) for t in tickers)
    port_ret_1y = sum(weights[t] * (holdings_data[t].get("return_1y_pct") or 0) for t in tickers)

    # Concentration risk (HHI)
    hhi = round(sum((w * 100) ** 2 for w in weights.values()), 1)
    if hhi < 1500:
        concentration_level = "Well-diversified"
    elif hhi < 2500:
        concentration_level = "Moderately concentrated"
    else:
        concentration_level = "Highly concentrated"

    result = {
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "holdings": holdings_data,
        "portfolio_metrics": {
            "return_1m_pct": round(port_ret_1m, 2),
            "return_3m_pct": round(port_ret_3m, 2),
            "return_1y_pct": round(port_ret_1y, 2),
            "annualized_volatility_pct": portfolio_vol,
            "sharpe_ratio": sharpe_ratio,
        },
        "correlation_matrix": correlation_matrix,
        "volatility_contributions": vol_contributions,
        "concentration_risk": {
            "hhi": hhi,
            "level": concentration_level,
            "top_holdings": sorted(
                [(t, round(w * 100, 2)) for t, w in weights.items()],
                key=lambda x: x[1], reverse=True
            )[:5],
        },
    }

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
