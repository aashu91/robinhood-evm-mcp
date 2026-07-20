#!/usr/bin/env python3
"""
Comprehensive Test Suite for Robinhood EVM MCP Server
Tests Oracles, Staking, and Telegram Mini-App integration
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


async def run_pyth_oracle_test():
    """Run Pyth Oracle tests"""
    print("\n" + "=" * 60)
    print("Testing Pyth Oracle...")
    print("=" * 60)

    try:
        from test_pyth_oracle import test_pyth_oracle
        return await test_pyth_oracle()
    except Exception as e:
        print(f"❌ Pyth Oracle test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_chainlink_oracle_test():
    """Run Chainlink Oracle tests"""
    print("\n" + "=" * 60)
    print("Testing Chainlink Oracle...")
    print("=" * 60)

    try:
        from test_chainlink_oracle import test_chainlink_oracle
        return await test_chainlink_oracle()
    except Exception as e:
        print(f"❌ Chainlink Oracle test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_unified_oracles_test():
    """Run Unified Oracles tests"""
    print("\n" + "=" * 60)
    print("Testing Unified Oracles...")
    print("=" * 60)

    try:
        from test_unified_oracles import test_unified_oracles
        return await test_unified_oracles()
    except Exception as e:
        print(f"❌ Unified Oracles test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_staking_integration_test():
    """Run Staking integration tests"""
    print("\n" + "=" * 60)
    print("Testing Staking Integration...")
    print("=" * 60)

    try:
        from test_staking_integration import test_staking_api, test_telegram_backend

        staking_api_passed = await test_staking_api()
        telegram_api_passed = await test_telegram_backend()

        return staking_api_passed and telegram_api_passed
    except Exception as e:
        print(f"❌ Staking integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test suite"""

    print("=" * 60)
    print("🚀 Robinhood EVM MCP Server - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Current Directory: {os.getcwd()}")
    print("=" * 60)

    # Run all tests
    tests = [
        ("Pyth Oracle", run_pyth_oracle_test),
        ("Chainlink Oracle", run_chainlink_oracle_test),
        ("Unified Oracles", run_unified_oracles_test),
        ("Staking Integration", run_staking_integration_test),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            passed = await test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ Test suite crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print("\n" + "=" * 60)
    print(f"Total: {total_passed}/{total_tests} tests passed")
    print("=" * 60)

    return total_passed == total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
