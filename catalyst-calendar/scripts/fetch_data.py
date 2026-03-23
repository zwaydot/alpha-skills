#!/usr/bin/env python3
"""
catalyst-calendar: Fetch earnings and dividend dates for a list of tickers.

Usage:
    python3 scripts/fetch_data.py AAPL MSFT NVDA TSLA
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py AAPL MSFT NVDA > calendar.md
"""

import sys
from datetime import datetime, timedelta, date

try:
    import yfinance as yf
    import pandas as pd
except ImportError as e:
    print(f"ERROR: Missing dependency — {e}. Run: pip install yfinance pandas")
    sys.exit(1)


def parse_date(val) -> date | None:
    """Convert various date formats to date object."""
    if val is None:
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.date()
    if isinstance(val, date):
        return val
    try:
        return pd.Timestamp(val).date()
    except Exception:
        return None


def fetch_events(ticker_sym: str, today: date, cutoff: date) -> list[dict]:
    """Fetch all catalyst events within [today, cutoff]."""
    events = []
    t = yf.Ticker(ticker_sym)
    info = t.info
    name = info.get("longName") or info.get("shortName", ticker_sym)

    # ── Earnings date ──────────────────────────────────────────────────────────
    try:
        cal = t.calendar
        if cal is not None:
            # calendar can be a dict or DataFrame depending on yfinance version
            if isinstance(cal, dict):
                earnings_dates = cal.get("Earnings Date", [])
                if not isinstance(earnings_dates, list):
                    earnings_dates = [earnings_dates]
                for ed in earnings_dates:
                    d = parse_date(ed)
                    if d and today <= d <= cutoff:
                        eps_est = info.get("epsForward") or info.get("epsCurrentYear")
                        events.append({
                            "date": d,
                            "ticker": ticker_sym.upper(),
                            "name": name,
                            "event_type": "📊 Earnings",
                            "detail": f"EPS est: ${eps_est:.2f}" if eps_est else "EPS est: N/A",
                        })
            elif isinstance(cal, pd.DataFrame):
                for col in cal.columns:
                    row_key = "Earnings Date"
                    if row_key in cal.index:
                        d = parse_date(cal.loc[row_key, col])
                        if d and today <= d <= cutoff:
                            eps_est = info.get("epsForward")
                            events.append({
                                "date": d,
                                "ticker": ticker_sym.upper(),
                                "name": name,
                                "event_type": "📊 Earnings",
                                "detail": f"EPS est: ${eps_est:.2f}" if eps_est else "EPS est: N/A",
                            })
    except Exception as e:
        print(f"  WARN: Could not fetch earnings for {ticker_sym}: {e}", file=sys.stderr)

    # Also try earnings_dates attribute (more reliable in newer yfinance)
    try:
        ed_df = t.earnings_dates
        if ed_df is not None and not ed_df.empty:
            for idx in ed_df.index:
                d = parse_date(idx)
                if d and today <= d <= cutoff:
                    # Check if not already added
                    if not any(e["date"] == d and e["event_type"] == "📊 Earnings" for e in events):
                        eps_est = None
                        try:
                            eps_est = float(ed_df.loc[idx, "EPS Estimate"]) if "EPS Estimate" in ed_df.columns else None
                        except Exception:
                            pass
                        events.append({
                            "date": d,
                            "ticker": ticker_sym.upper(),
                            "name": name,
                            "event_type": "📊 Earnings",
                            "detail": f"EPS est: ${eps_est:.2f}" if eps_est else "EPS est: N/A",
                        })
    except Exception:
        pass

    # ── Dividend dates ─────────────────────────────────────────────────────────
    try:
        ex_div = parse_date(info.get("exDividendDate"))
        if ex_div and today <= ex_div <= cutoff:
            div_rate = info.get("dividendRate") or info.get("lastDividendValue")
            events.append({
                "date": ex_div,
                "ticker": ticker_sym.upper(),
                "name": name,
                "event_type": "💰 Ex-Dividend",
                "detail": f"Div: ${div_rate:.4f}/share" if div_rate else "Div: N/A",
            })
    except Exception:
        pass

    return events


def format_markdown_calendar(events: list[dict], today: date, cutoff: date) -> str:
    """Format events as Markdown table."""
    lines = []
    lines.append(f"# 📅 Catalyst Calendar")
    lines.append(f"**Period:** {today.strftime('%Y-%m-%d')} → {cutoff.strftime('%Y-%m-%d')} (90 days)")
    lines.append(f"**Generated:** {today.strftime('%Y-%m-%d')}")
    lines.append("")

    if not events:
        lines.append("> No catalyst events found in the next 90 days for the selected tickers.")
        return "\n".join(lines)

    # Sort by date
    events_sorted = sorted(events, key=lambda x: x["date"])

    lines.append("| Date | Ticker | Company | Event | Detail |")
    lines.append("|------|--------|---------|-------|--------|")

    for e in events_sorted:
        d_str = e["date"].strftime("%Y-%m-%d")
        day_name = e["date"].strftime("%a")
        days_until = (e["date"] - today).days
        days_label = f"T+{days_until}" if days_until > 0 else "Today"
        lines.append(
            f"| {d_str} ({day_name}, {days_label}) | **{e['ticker']}** | {e['name']} | {e['event_type']} | {e['detail']} |"
        )

    lines.append("")
    lines.append(f"**Total events:** {len(events_sorted)}")

    # Summary by type
    type_counts = {}
    for e in events_sorted:
        type_counts[e["event_type"]] = type_counts.get(e["event_type"], 0) + 1
    lines.append("")
    lines.append("**Event breakdown:**")
    for etype, count in sorted(type_counts.items()):
        lines.append(f"- {etype}: {count}")

    return "\n".join(lines)


def main():
    tickers = [t.upper() for t in sys.argv[1:]] if len(sys.argv) > 1 else ["AAPL", "MSFT", "NVDA"]

    today = date.today()
    cutoff = today + timedelta(days=90)

    print(f"Scanning {len(tickers)} tickers for events in next 90 days...", file=sys.stderr)

    all_events = []
    for sym in tickers:
        print(f"  → {sym}...", file=sys.stderr)
        events = fetch_events(sym, today, cutoff)
        all_events.extend(events)
        print(f"     Found {len(events)} event(s)", file=sys.stderr)

    print("", file=sys.stderr)
    output = format_markdown_calendar(all_events, today, cutoff)
    print(output)


if __name__ == "__main__":
    main()
