#!/usr/bin/env python3
"""
Pyth Oracle Test Script
Tests Pyth Network integration for commodity prices
"""

import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oracles.pyth_oracle import PythOracle

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


async def test_pyth_oracle():
    """Test Pyth Oracle integration"""

    print("=" * 60)
    print("Pyth Oracle Test")
    print("=" * 60)

    try:
        # Initialize Pyth Oracle with context manager
        async with PythOracle() as oracle:
            print("\n[Test 1] Get Gold Price...")
            gold_price = await oracle.get_gold_price()
            print(f"✅ Gold Price: ${gold_price['price']}")
            print(f"   Confidence: {gold_price['confidence']}")
            print(f"   Exponent: {gold_price['exponent']}")
            print(f"   Status: {gold_price['status']}")

            print("\n[Test 2] Get Silver Price...")
            silver_price = await oracle.get_silver_price()
            print(f"✅ Silver Price: ${silver_price['price']}")
            print(f"   Confidence: {silver_price['confidence']}")
            print(f"   Exponent: {silver_price['exponent']}")
            print(f"   Status: {silver_price['status']}")

            print("\n[Test 3] Get Price by Ticker (GOLD)...")
            gold_by_ticker = await oracle.get_price_by_ticker("GOLD")
            print(f"✅ GOLD Price: ${gold_by_ticker['price']}")
            print(f"   Status: {gold_by_ticker['status']}")

            print("\n[Test 4] Get Price by Ticker (SILVER)...")
            silver_by_ticker = await oracle.get_price_by_ticker("SILVER")
            print(f"✅ SILVER Price: ${silver_by_ticker['price']}")
            print(f"   Status: {silver_by_ticker['status']}")

        print("\n" + "=" * 60)
        print("✅ All Pyth Oracle tests passed!")
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
        success = await test_pyth_oracle()

        if success:
            print("\n✅ Pyth Oracle tests passed!")
        else:
            print("\n❌ Some tests failed")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
