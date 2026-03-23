#!/usr/bin/env python3
"""
Fetch financial data from multiple sources
Supports: Yahoo Finance (US), Tencent Finance (CN/HK)
"""

import json
import sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests module not found. Run: pip install requests")
    sys.exit(1)

def fetch_yahoo(ticker):
    """Fetch data from Yahoo Finance"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        data = resp.json()
        meta = data['chart']['result'][0]['meta']
        return {
            'ticker': ticker,
            'price': meta.get('regularMarketPrice'),
            'currency': meta.get('currency'),
            'source': 'Yahoo Finance'
        }
    except Exception as e:
        return {'error': str(e)}

def fetch_tencent(symbol):
    """Fetch data from Tencent Finance"""
    # Determine market prefix
    if symbol.startswith('sh'):
        code = symbol[2:]
        market = 'sh'
    elif symbol.startswith('sz'):
        code = symbol[2:]
        market = 'sz'
    elif symbol.startswith('hk'):
        code = symbol[2:]
        market = 'hk'
    else:
        code = symbol
        market = 'sh'  # Default
    
    url = f"https://qt.gtimg.cn/q={market}{code}"
    try:
        resp = requests.get(url, timeout=30)
        resp.encoding = 'gbk'
        data = resp.text
        # Parse Tencent format
        parts = data.split('~')
        if len(parts) > 45:
            return {
                'symbol': symbol,
                'name': parts[1],
                'price': float(parts[3]),
                'change': float(parts[4]),
                'change_pct': float(parts[5]),
                'volume': int(parts[6]),
                'market_cap': parts[44],
                'source': 'Tencent Finance'
            }
        return {'error': 'Parse failed', 'raw': data[:200]}
    except Exception as e:
        return {'error': str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_data.py <ticker/symbol>")
        print("Examples:")
        print("  fetch_data.py AAPL       # US stock")
        print("  fetch_data.py sh600519   # A-share")
        print("  fetch_data.py hk00700    # HK stock")
        sys.exit(1)
    
    symbol = sys.argv[1]
    
    # Determine source
    if symbol.startswith(('sh', 'sz', 'hk')):
        result = fetch_tencent(symbol)
    else:
        result = fetch_yahoo(symbol)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
