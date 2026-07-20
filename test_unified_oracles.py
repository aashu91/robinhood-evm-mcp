#!/usr/bin/env python3
"""
Unified Oracles Test Script
Tests Unified Oracles integration (Pyth + Chainlink)
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oracles.unified_oracles import UnifiedOracles

# Load environment variables
def load_env():
    env_path = os.path.expanduser("~/.env")
    if os.path.exists(".env"):
        env_path = ".env"

    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env()


async def test_unified_oracles():
    """Test Unified Oracles integration"""

    print("=" * 60)
    print("Unified Oracles Test")
    print("=" * 60)

    try:
        # Initialize Unified Oracles with context manager
        async with UnifiedOracles() as oracles:
            print("\n[Test 1] Get Gold Price (Pyth)...")
            gold = await oracles.get_gold_price()
            print(f"✅ Gold: {gold}")

            print("\n[Test 2] Get Silver Price (Pyth)...")
            silver = await oracles.get_silver_price()
            print(f"✅ Silver: {silver}")

            print("\n[Test 3] Get AAPL Price (Chainlink)...")
            aapl = await oracles.get_price_by_ticker("AAPL")
            print(f"✅ AAPL: {aapl}")

            print("\n[Test 4] Get TSLA Price (Chainlink)...")
            tsla = await oracles.get_price_by_ticker("TSLA")
            print(f"✅ TSLA: {tsla}")

            print("\n[Test 5] Get All Prices...")
            prices = await oracles.get_all_prices()
            print(f"✅ Retrieved {len(prices)} prices")
            for ticker, price_data in prices.items():
                print(f"   {ticker}: {price_data}")

        print("\n" + "=" * 60)
        print("✅ All Unified Oracles tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    try:
        success = await test_unified_oracles()

        if success:
            print("\n✅ Unified Oracles tests passed!")
        else:
            print("\n❌ Some tests failed")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
