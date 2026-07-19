#!/usr/bin/env python3
"""
Chainlink Oracle Test Script
Tests Chainlink Oracles integration for stock prices
"""

import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oracles.chainlink_oracle import ChainlinkOracle

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


async def test_chainlink_oracle():
    """Test Chainlink Oracle integration"""

    print("=" * 60)
    print("Chainlink Oracle Test")
    print("=" * 60)

    try:
        # Initialize Chainlink Oracle with context manager
        async with ChainlinkOracle() as oracle:
            print("\n[Test 1] Get AAPL Price...")
            aapl_price = await oracle.get_price_by_ticker("AAPL")
            print(f"✅ AAPL Price: ${aapl_price['price']}")
            print(f"   Confidence: {aapl_price['confidence']}")
            print(f"   Status: {aapl_price['status']}")

            print("\n[Test 2] Get TSLA Price...")
            tsla_price = await oracle.get_price_by_ticker("TSLA")
            print(f"✅ TSLA Price: ${tsla_price['price']}")
            print(f"   Confidence: {tsla_price['confidence']}")
            print(f"   Status: {tsla_price['status']}")

            print("\n[Test 3] Get Price by Ticker (AAPL)...")
            aapl_by_ticker = await oracle.get_price_by_ticker("AAPL")
            print(f"✅ AAPL Price: ${aapl_by_ticker['price']}")
            print(f"   Status: {aapl_by_ticker['status']}")

            print("\n[Test 4] Get Price by Ticker (TSLA)...")
            tsla_by_ticker = await oracle.get_price_by_ticker("TSLA")
            print(f"✅ TSLA Price: ${tsla_by_ticker['price']}")
            print(f"   Status: {tsla_by_ticker['status']}")

        print("\n" + "=" * 60)
        print("✅ All Chainlink Oracle tests passed!")
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
        success = await test_chainlink_oracle()

        if success:
            print("\n✅ Chainlink Oracle tests passed!")
        else:
            print("\n❌ Some tests failed")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
