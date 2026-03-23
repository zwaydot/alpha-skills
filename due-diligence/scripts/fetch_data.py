#!/usr/bin/env python3
"""
Due Diligence Data Pack - SEC EDGAR Document Fetcher
Fetches a company's latest 10-K and 10-Q filings from the SEC EDGAR API.
No API key required. Outputs a structured JSON with filing metadata and links.

Usage:
    python3 scripts/fetch_data.py AAPL
    python3 scripts/fetch_data.py MSFT --forms 10-K 10-Q DEF14A --output msft_edgar.json
    python3 scripts/fetch_data.py AAPL --cik 0000320193     # Use known CIK directly
"""

import sys
import json
import argparse
import time
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, quote

# SEC EDGAR base URLs
EDGAR_BASE = "https://data.sec.gov"
EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions"
EDGAR_FILING_BASE = "https://www.sec.gov/Archives/edgar/data"
EDGAR_FILING_URL = "https://www.sec.gov/cgi-bin/browse-edgar"

HEADERS = {
    "User-Agent": "AlphaSkills Research Tool research@example.com",
    "Accept": "application/json",
}


def fetch_json(url, retries=3, delay=1.0):
    """Fetch JSON from SEC EDGAR with rate limiting."""
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 429:
                print(f"  Rate limited (429). Waiting {delay * 2}s...")
                time.sleep(delay * 2)
            else:
                print(f"  HTTP Error {e.code} for {url}")
                return None
        except URLError as e:
            print(f"  URL Error: {e.reason} for {url}")
            return None
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            return None
        time.sleep(delay)
    return None


def search_company_cik(company_name_or_ticker):
    """Search SEC EDGAR for company CIK by name or ticker."""
    search_url = f"https://efts.sec.gov/LATEST/search-index?q=%22{quote(company_name_or_ticker)}%22&dateRange=custom&startdt=2000-01-01&enddt=2099-01-01&forms=10-K"

    # Use the EDGAR company search API instead
    ticker_url = f"https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK={quote(company_name_or_ticker)}&type=10-K&dateb=&owner=include&count=1&search_text=&action=getcompany&output=atom"

    # Try the company_tickers JSON (most reliable for US tickers)
    tickers_url = "https://www.sec.gov/files/company_tickers.json"
    print(f"  Searching EDGAR for ticker: {company_name_or_ticker}...")

    data = fetch_json(tickers_url)
    if data:
        ticker_upper = company_name_or_ticker.upper()
        for _, company in data.items():
            if company.get("ticker", "").upper() == ticker_upper:
                cik = str(company["cik_str"]).zfill(10)
                name = company.get("title", ticker_upper)
                print(f"  Found: {name} | CIK: {cik}")
                return cik, name

    print(f"  Could not find CIK for '{company_name_or_ticker}' in EDGAR")
    return None, None


def fetch_submissions(cik_padded):
    """Fetch company submission history from SEC EDGAR."""
    url = f"{EDGAR_SUBMISSIONS}/CIK{cik_padded}.json"
    return fetch_json(url)


def extract_filings(submissions, form_types=None, limit=5):
    """Extract recent filings of specified types from submission data."""
    if form_types is None:
        form_types = ["10-K", "10-Q"]

    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    acc_nums = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    reports_for = recent.get("reportDate", [])
    primary_docs = recent.get("primaryDocument", [])
    descriptions = recent.get("primaryDocDescription", [])

    cik_stripped = str(int(submissions.get("cik", "0")))

    filings = []
    seen_forms = {}

    for i, form in enumerate(forms):
        if form not in form_types:
            continue
        if seen_forms.get(form, 0) >= limit:
            continue

        acc_num = acc_nums[i] if i < len(acc_nums) else ""
        acc_formatted = acc_num.replace("-", "")
        filing_date = dates[i] if i < len(dates) else ""
        report_date = reports_for[i] if i < len(reports_for) else ""
        primary_doc = primary_docs[i] if i < len(primary_docs) else ""
        description = descriptions[i] if i < len(descriptions) else ""

        # Construct viewer URL
        viewer_url = f"https://www.sec.gov/Archives/edgar/data/{cik_stripped}/{acc_formatted}/{primary_doc}"
        index_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_stripped}&type={form}&dateb=&owner=include&count=10"

        filings.append({
            "form_type": form,
            "filing_date": filing_date,
            "report_date": report_date,
            "accession_number": acc_num,
            "primary_document": primary_doc,
            "description": description,
            "document_url": viewer_url,
            "filing_index_url": f"https://www.sec.gov/Archives/edgar/data/{cik_stripped}/{acc_formatted}/",
        })

        seen_forms[form] = seen_forms.get(form, 0) + 1

    return filings


def fetch_edgar_filings(ticker_or_cik, form_types=None, limit=5, known_cik=None):
    """Main function to fetch EDGAR filings for a company."""
    print(f"\n=== SEC EDGAR Document Fetcher: {ticker_or_cik} ===\n")

    if form_types is None:
        form_types = ["10-K", "10-Q"]

    # Resolve CIK
    if known_cik:
        cik = str(known_cik).zfill(10)
        company_name = ticker_or_cik.upper()
        print(f"  Using provided CIK: {cik}")
    else:
        cik, company_name = search_company_cik(ticker_or_cik)
        if not cik:
            print(f"  Error: Could not resolve CIK for '{ticker_or_cik}'")
            print(f"  Try providing CIK directly with --cik flag")
            return None

    # Fetch submissions
    print(f"  Fetching submission history from EDGAR...")
    submissions = fetch_submissions(cik)
    if not submissions:
        print(f"  Error: Could not fetch EDGAR submissions for CIK {cik}")
        return None

    company_name_edgar = submissions.get("name", company_name)
    sic = submissions.get("sic", "N/A")
    sic_description = submissions.get("sicDescription", "N/A")
    state = submissions.get("stateOfIncorporation", "N/A")
    fiscal_year_end = submissions.get("fiscalYearEnd", "N/A")
    exchange = submissions.get("exchanges", ["N/A"])
    ein = submissions.get("ein", "N/A")

    print(f"  Company: {company_name_edgar} | SIC: {sic} ({sic_description})")
    print(f"  State: {state} | Fiscal Year End: {fiscal_year_end}")

    # Extract relevant filings
    print(f"  Extracting filings: {', '.join(form_types)}...")
    filings = extract_filings(submissions, form_types, limit=limit)

    # Summary counts
    form_counts = {}
    for f in filings:
        form_counts[f["form_type"]] = form_counts.get(f["form_type"], 0) + 1
    print(f"  Found: {', '.join(f'{k}: {v}' for k, v in form_counts.items())}")

    result = {
        "metadata": {
            "ticker": ticker_or_cik.upper(),
            "company_name": company_name_edgar,
            "cik": cik,
            "sic_code": sic,
            "sic_description": sic_description,
            "state_of_incorporation": state,
            "fiscal_year_end": fiscal_year_end,
            "exchange": exchange,
            "ein": ein,
            "fetched_at": datetime.now().isoformat(),
        },
        "edgar_links": {
            "company_page": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&dateb=&owner=include&count=40",
            "all_10k_filings": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=include&count=10",
            "all_10q_filings": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-Q&dateb=&owner=include&count=10",
            "xbrl_facts": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            "submissions_api": f"{EDGAR_SUBMISSIONS}/CIK{cik}.json",
        },
        "filing_count": form_counts,
        "filings": filings,
        "dd_checklist": {
            "annual_report_10k": {
                "latest_available": next((f["filing_date"] for f in filings if f["form_type"] == "10-K"), "Not found"),
                "status": "Retrieved" if any(f["form_type"] == "10-K" for f in filings) else "Not found",
                "key_sections": [
                    "Item 1: Business description",
                    "Item 1A: Risk factors",
                    "Item 7: MD&A (Management Discussion & Analysis)",
                    "Item 8: Financial statements",
                    "Item 9A: Controls and procedures",
                ],
            },
            "quarterly_report_10q": {
                "latest_available": next((f["filing_date"] for f in filings if f["form_type"] == "10-Q"), "Not found"),
                "status": "Retrieved" if any(f["form_type"] == "10-Q" for f in filings) else "Not found",
                "key_sections": [
                    "Part I: Financial statements",
                    "Item 2: MD&A",
                    "Item 3: Quantitative/qualitative market risk",
                    "Item 4: Controls and procedures",
                ],
            },
            "additional_dd_items": [
                "Proxy statement (DEF 14A) - executive compensation, related party transactions",
                "8-K filings - material events, earnings releases",
                "S-1/S-11 - if IPO or REIT",
                "SC 13D/G - major shareholder filings",
            ],
        }
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch SEC EDGAR filings for due diligence")
    parser.add_argument("ticker", help="Ticker symbol or company name (e.g. AAPL)")
    parser.add_argument("--forms", nargs="+", default=["10-K", "10-Q"],
                        help="Form types to retrieve (default: 10-K 10-Q)")
    parser.add_argument("--limit", type=int, default=5,
                        help="Max filings per form type (default: 5)")
    parser.add_argument("--cik", default=None,
                        help="Use known CIK directly (optional, e.g. 0000320193 for Apple)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output JSON filename")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    output_file = args.output or f"{ticker}_edgar_{datetime.now().strftime('%Y%m%d')}.json"

    data = fetch_edgar_filings(ticker, args.forms, args.limit, args.cik)

    if not data:
        print("\n❌ Failed to fetch EDGAR data.")
        sys.exit(1)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ EDGAR filing data saved to: {output_file}")

    # Print filings summary
    print("\n--- Recent Filings ---")
    for filing in data["filings"][:8]:
        print(f"  [{filing['form_type']}] {filing['filing_date']} | {filing['description'] or 'N/A'}")
        print(f"    URL: {filing['document_url']}")

    print(f"\n--- Key EDGAR Links ---")
    for name, url in data["edgar_links"].items():
        print(f"  {name}: {url}")


if __name__ == "__main__":
    main()
