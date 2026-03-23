# catalyst-calendar

**Stage:** 事件驱动 (Event-Driven)

## Description

90-day catalyst calendar for a list of tickers. Aggregates upcoming earnings dates, dividend ex-dates, and dividend payment dates from Yahoo Finance. Outputs a chronological Markdown calendar to help plan trade timing around key corporate events.

## Name

Catalyst Calendar

## Inputs

- `tickers` — Space-separated list of ticker symbols (e.g., `AAPL MSFT NVDA TSLA`)

## Outputs

Markdown calendar containing:
- Chronological table of events in the next 90 days
- Event types: Earnings, Ex-Dividend, Dividend Payment
- Company name and ticker for each event
- Expected EPS (where available) for earnings events

## Event Types

| Event | Description |
|-------|-------------|
| 📊 Earnings | Quarterly earnings release date |
| 💰 Ex-Dividend | Last day to own stock to receive dividend |
| 💵 Dividend Payment | Date dividend is paid to shareholders |

## Data Sources

- **yfinance** — `ticker.calendar` for earnings and dividend dates
- **yfinance** — `ticker.info` for EPS estimates and company name

## Script Usage

```bash
# Generate calendar for a list of tickers
python3 scripts/fetch_data.py AAPL MSFT NVDA TSLA AMZN

# Single ticker
python3 scripts/fetch_data.py AAPL

# Save Markdown output
python3 scripts/fetch_data.py AAPL MSFT NVDA > catalyst_calendar.md
```

Output printed as formatted Markdown table to stdout.

## Example Prompts

```
Show me the catalyst calendar for the next 90 days: AAPL MSFT NVDA TSLA AMZN GOOGL
```

```
When are the next earnings dates for my portfolio? AAPL:30 MSFT:20 NVDA:50
```

```
Build a 90-day event calendar for mega-cap tech stocks
```

## Usage Tips

- Run before each week to check for upcoming catalysts
- Earnings dates from Yahoo Finance may be estimates — confirm with IR websites for precision
- Ex-dividend dates are useful for dividend capture strategies
- Combine with `valuation-matrix` to identify pre-earnings entry points
