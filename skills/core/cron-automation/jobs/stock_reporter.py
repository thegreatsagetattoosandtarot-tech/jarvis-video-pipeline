#!/usr/bin/env python3
"""
J.A.R.V.I.S. Stock Reporter
Daily market summary (market days only).
"""

import os
import json
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path("/opt/data/jarvis")
LOGS_DIR = JARVIS_ROOT / "logs"

# Would use Alpha Vantage or similar API in production
# API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")


def get_market_data() -> dict:
    """Get market data (placeholder)."""
    # In production: call Alpha Vantage / Yahoo Finance API
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "indices": {
            "SP500": {"price": 5432.10, "change": +0.45},
            "NASDAQ": {"price": 17654.32, "change": +0.62},
            "DOW": {"price": 39876.54, "change": +0.31},
        },
        "portfolio": {
            "total_value": 125430.50,
            "daily_change": +1.23,
            "positions": [
                {"symbol": "AAPL", "shares": 10, "value": 1923.40, "change": +0.5},
                {"symbol": "MSFT", "shares": 5, "value": 2145.60, "change": +0.8},
                {"symbol": "NVDA", "shares": 3, "value": 3567.80, "change": +1.2},
            ]
        },
        "crypto": {
            "BTC": {"price": 67432.10, "change": -0.2},
            "ETH": {"price": 3421.50, "change": +0.1},
        }
    }


def main():
    # Check if market day (Mon-Fri)
    if datetime.now().weekday() >= 5:
        print("Weekend - skipping stock report")
        return
    
    print(f"=== J.A.R.V.I.S. MARKET REPORT - {datetime.now().strftime('%B %d, %Y')} ===\n")
    
    data = get_market_data()
    
    print("MAJOR INDICES:")
    for name, info in data["indices"].items():
        change_str = f"{info['change']:+.2f}%"
        print(f"  {name}: {info['price']:,.2f} ({change_str})")
    
    print("\nPORTFOLIO:")
    print(f"  Total Value: ${data['portfolio']['total_value']:,.2f}")
    print(f"  Daily Change: {data['portfolio']['daily_change']:+.2f}%")
    for pos in data["portfolio"]["positions"]:
        print(f"  {pos['symbol']}: {pos['shares']} shares @ ${pos['value']:,.2f} ({pos['change']:+.1f}%)")
    
    print("\nCRYPTO:")
    for symbol, info in data["crypto"].items():
        print(f"  {symbol}: ${info['price']:,.2f} ({info['change']:+.1f}%)")
    
    # Save
    LOGS_DIR.mkdir(exist_ok=True)
    stock_file = LOGS_DIR / f"stock_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(stock_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "market_data": data
        }, f, indent=2)
    
    print(f"\n✓ Stock report saved to {stock_file}")


if __name__ == "__main__":
    main()