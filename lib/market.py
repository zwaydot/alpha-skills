"""
Multi-market configuration for alpha-skills.

Supports: US (default), HK, CN (basic).
To add a new market: add entries to MARKET_CONFIGS and MARKET_SECTOR_MULTIPLES.

Usage in any skill script:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
    from market import detect_market, get_market_config, get_sector_multiples
"""


def detect_market(ticker: str) -> str:
    """Detect market from ticker suffix.

    Examples:
        AAPL      → US
        0700.HK   → HK
        9988.HK   → HK
        600519.SS → CN
        000001.SZ → CN
        7203.T    → JP
        HSBA.L    → UK
        SAP.DE    → DE
    """
    t = ticker.upper().strip()
    if t.endswith(".HK"):
        return "HK"
    if t.endswith(".SS") or t.endswith(".SZ"):
        return "CN"
    if t.endswith(".T"):
        return "JP"
    if t.endswith(".L"):
        return "UK"
    if t.endswith(".DE"):
        return "DE"
    if t.endswith(".PA"):
        return "FR"
    if t.endswith(".AS"):
        return "NL"
    return "US"


def detect_portfolio_market(tickers: list[str]) -> str:
    """Detect primary market from a list of tickers (majority rule)."""
    if not tickers:
        return "US"
    markets = [detect_market(t) for t in tickers]
    from collections import Counter
    return Counter(markets).most_common(1)[0][0]


# ── Market-level parameters ─────────────────────────────────────────────────
# To add a new market, add a new key here with tax_rate, risk_free_rate, currency.

MARKET_CONFIGS = {
    "US": {"tax_rate": 0.21, "risk_free_rate": 0.045, "currency": "USD", "label": "United States"},
    "HK": {"tax_rate": 0.165, "risk_free_rate": 0.04, "currency": "HKD", "label": "Hong Kong"},
    "CN": {"tax_rate": 0.25, "risk_free_rate": 0.02, "currency": "CNY", "label": "China A-share"},
    "JP": {"tax_rate": 0.30, "risk_free_rate": 0.01, "currency": "JPY", "label": "Japan"},
    "UK": {"tax_rate": 0.25, "risk_free_rate": 0.04, "currency": "GBP", "label": "United Kingdom"},
    "DE": {"tax_rate": 0.30, "risk_free_rate": 0.03, "currency": "EUR", "label": "Germany"},
    "FR": {"tax_rate": 0.25, "risk_free_rate": 0.03, "currency": "EUR", "label": "France"},
    "NL": {"tax_rate": 0.26, "risk_free_rate": 0.03, "currency": "EUR", "label": "Netherlands"},
}

_DEFAULT_CONFIG = {"tax_rate": 0.21, "risk_free_rate": 0.04, "currency": "USD", "label": "Unknown"}


def get_market_config(market: str) -> dict:
    """Return full config dict for a market."""
    return MARKET_CONFIGS.get(market, _DEFAULT_CONFIG)


def get_tax_rate(market: str) -> float:
    return get_market_config(market)["tax_rate"]


def get_risk_free_rate(market: str) -> float:
    return get_market_config(market)["risk_free_rate"]


# ── Sector-aware valuation multiples per market ──────────────────────────────
# Format: (bear, base, bull) for pe, ev_ebitda; (bull_yield, base_yield, bear_yield) for fcf_yield
# — lower yield = higher price, so bull has lowest yield
#
# To add a new market: add a new key to MARKET_SECTOR_MULTIPLES.
# Missing sectors fall back to the market's _DEFAULT, then to US defaults.

_US_MULTIPLES = {
    "Technology":              {"pe": (20, 30, 40), "ev_ebitda": (15, 22, 30), "fcf_yield": (0.02, 0.03, 0.04)},
    "Communication Services":  {"pe": (15, 22, 30), "ev_ebitda": (10, 16, 22), "fcf_yield": (0.03, 0.04, 0.05)},
    "Consumer Cyclical":       {"pe": (12, 18, 25), "ev_ebitda": (8, 13, 18),  "fcf_yield": (0.04, 0.05, 0.06)},
    "Consumer Defensive":      {"pe": (15, 20, 25), "ev_ebitda": (10, 14, 18), "fcf_yield": (0.04, 0.05, 0.06)},
    "Healthcare":              {"pe": (15, 22, 30), "ev_ebitda": (10, 16, 22), "fcf_yield": (0.03, 0.04, 0.05)},
    "Financial Services":      {"pe": (8, 12, 16),  "ev_ebitda": (6, 9, 12),   "fcf_yield": (0.06, 0.08, 0.10)},
    "Industrials":             {"pe": (12, 18, 24), "ev_ebitda": (8, 12, 16),  "fcf_yield": (0.04, 0.05, 0.07)},
    "Energy":                  {"pe": (6, 10, 14),  "ev_ebitda": (4, 6, 9),    "fcf_yield": (0.06, 0.08, 0.12)},
    "Basic Materials":         {"pe": (8, 13, 18),  "ev_ebitda": (5, 8, 12),   "fcf_yield": (0.05, 0.07, 0.09)},
    "Real Estate":             {"pe": (15, 25, 35), "ev_ebitda": (12, 18, 25), "fcf_yield": (0.04, 0.05, 0.06)},
    "Utilities":               {"pe": (12, 17, 22), "ev_ebitda": (8, 11, 14),  "fcf_yield": (0.05, 0.06, 0.08)},
    "_DEFAULT":                {"pe": (15, 20, 25), "ev_ebitda": (10, 14, 18), "fcf_yield": (0.04, 0.05, 0.06)},
}

# HK trades at a structural discount to US (lower liquidity, geopolitical risk)
# Roughly 20-30% lower multiples for growth sectors, 10-15% for defensive
_HK_MULTIPLES = {
    "Technology":              {"pe": (12, 20, 28), "ev_ebitda": (8, 14, 20),  "fcf_yield": (0.03, 0.05, 0.07)},
    "Communication Services":  {"pe": (10, 16, 22), "ev_ebitda": (6, 10, 15),  "fcf_yield": (0.04, 0.06, 0.08)},
    "Consumer Cyclical":       {"pe": (8, 14, 20),  "ev_ebitda": (5, 9, 14),   "fcf_yield": (0.05, 0.07, 0.09)},
    "Consumer Defensive":      {"pe": (10, 16, 22), "ev_ebitda": (7, 11, 15),  "fcf_yield": (0.05, 0.06, 0.08)},
    "Healthcare":              {"pe": (12, 18, 25), "ev_ebitda": (8, 13, 18),  "fcf_yield": (0.04, 0.05, 0.07)},
    "Financial Services":      {"pe": (4, 7, 10),   "ev_ebitda": (4, 6, 9),    "fcf_yield": (0.08, 0.10, 0.14)},
    "Industrials":             {"pe": (6, 10, 15),  "ev_ebitda": (4, 7, 11),   "fcf_yield": (0.06, 0.08, 0.10)},
    "Energy":                  {"pe": (4, 7, 10),   "ev_ebitda": (3, 5, 7),    "fcf_yield": (0.08, 0.10, 0.14)},
    "Basic Materials":         {"pe": (5, 8, 12),   "ev_ebitda": (3, 6, 9),    "fcf_yield": (0.07, 0.09, 0.12)},
    "Real Estate":             {"pe": (5, 10, 16),  "ev_ebitda": (8, 14, 20),  "fcf_yield": (0.05, 0.07, 0.09)},
    "Utilities":               {"pe": (8, 12, 16),  "ev_ebitda": (6, 9, 12),   "fcf_yield": (0.06, 0.07, 0.09)},
    "_DEFAULT":                {"pe": (8, 14, 20),  "ev_ebitda": (6, 10, 15),  "fcf_yield": (0.05, 0.07, 0.09)},
}

# CN (A-share) — higher P/E for consumer/healthcare (scarcity premium), lower for SOE-heavy sectors
_CN_MULTIPLES = {
    "Technology":              {"pe": (15, 25, 35), "ev_ebitda": (10, 18, 25), "fcf_yield": (0.02, 0.04, 0.06)},
    "Consumer Cyclical":       {"pe": (15, 25, 35), "ev_ebitda": (10, 16, 22), "fcf_yield": (0.03, 0.04, 0.06)},
    "Consumer Defensive":      {"pe": (20, 30, 40), "ev_ebitda": (12, 18, 25), "fcf_yield": (0.02, 0.03, 0.05)},
    "Healthcare":              {"pe": (18, 28, 38), "ev_ebitda": (12, 20, 28), "fcf_yield": (0.02, 0.04, 0.06)},
    "Financial Services":      {"pe": (4, 6, 9),    "ev_ebitda": (3, 5, 8),    "fcf_yield": (0.08, 0.12, 0.16)},
    "Energy":                  {"pe": (5, 8, 12),   "ev_ebitda": (3, 5, 8),    "fcf_yield": (0.08, 0.10, 0.14)},
    "Industrials":             {"pe": (8, 14, 20),  "ev_ebitda": (5, 9, 14),   "fcf_yield": (0.05, 0.07, 0.09)},
    "Real Estate":             {"pe": (5, 8, 12),   "ev_ebitda": (4, 7, 10),   "fcf_yield": (0.06, 0.09, 0.12)},
    "Utilities":               {"pe": (10, 14, 18), "ev_ebitda": (6, 9, 12),   "fcf_yield": (0.05, 0.07, 0.09)},
    "_DEFAULT":                {"pe": (10, 18, 25), "ev_ebitda": (8, 12, 18),  "fcf_yield": (0.04, 0.06, 0.08)},
}

MARKET_SECTOR_MULTIPLES = {
    "US": _US_MULTIPLES,
    "HK": _HK_MULTIPLES,
    "CN": _CN_MULTIPLES,
    # New markets: add here. Missing markets fall back to US multiples.
}


def get_sector_multiples(market: str, sector: str | None) -> dict:
    """Return (bear, base, bull) multiple ranges for a market+sector pair."""
    market_map = MARKET_SECTOR_MULTIPLES.get(market, _US_MULTIPLES)
    if sector and sector in market_map:
        return market_map[sector]
    return market_map.get("_DEFAULT", _US_MULTIPLES["_DEFAULT"])


# ── Index / Universe tickers ────────────────────────────────────────────────
# Used by stock-screener. To add a new index, add a function or entry here.

# Hang Seng Index — major constituents (~60 stocks)
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

# Hang Seng TECH Index — ~30 tech-focused stocks
HSTECH_TICKERS = [
    "0268.HK", "0285.HK", "0522.HK", "0700.HK", "0772.HK", "0909.HK", "0981.HK",
    "0992.HK", "1024.HK", "1347.HK", "1810.HK", "1833.HK", "2013.HK", "2018.HK",
    "2269.HK", "2382.HK", "3690.HK", "3888.HK", "6060.HK", "6618.HK", "6690.HK",
    "9618.HK", "9626.HK", "9888.HK", "9961.HK", "9988.HK", "9999.HK",
]


# ── Sector ETF mappings per market ──────────────────────────────────────────
# Used by sector-radar.

SECTOR_ETFS = {
    "US": {
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
    },
    "HK": {
        "3067.HK": "HK Tech (HSTECH ETF)",
        "3033.HK": "HK Financials (S&P HK Financials)",
        "3012.HK": "HK Property",
        "2800.HK": "HK Broad Market (Tracker Fund)",
        "2828.HK": "China A-share (HSI A-share ETF)",
        "3040.HK": "HK Consumer",
    },
    # Add new markets here
}


def get_sector_etfs(market: str) -> dict:
    """Return {etf_ticker: sector_name} for a market."""
    return SECTOR_ETFS.get(market, SECTOR_ETFS["US"])
