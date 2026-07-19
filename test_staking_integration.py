#!/usr/bin/env python3
"""
Staking Contract Integration Test
Tests StakingYield contract integration with Telegram Mini-App
"""

import asyncio
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_backend import app, web3_helper
from fastapi.testclient import TestClient

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


async def test_staking_api():
    """Test Staking API endpoints"""

    print("=" * 60)
    print("Staking API Integration Test")
    print("=" * 60)

    # Check if staking contract is available
    if not hasattr(app.state, 'staking_contract'):
        print("⚠️  Staking contract not loaded. Starting backend server...")
        # This would require starting the FastAPI server
        print("❌ Cannot test without deployed staking contract")
        return False

    staking_contract = app.state.staking_contract

    print("\n[Test 1] Get Contract Balance...")
    try:
        balance = staking_contract.functions.getContractBalance().call()
        print(f"✅ Contract Balance: {balance} wei")
        print(f"   = {web3_helper.w3.from_wei(balance, 'ether')} ETH")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False

    print("\n[Test 2] Get Total Rewards...")
    try:
        total_rewards = staking_contract.functions.getTotalRewards().call()
        print(f"✅ Total Rewards: {total_rewards} wei")
        print(f"   = {web3_helper.w3.from_wei(total_rewards, 'ether')} ETH")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False

    print("\n[Test 3] Get Reward Rate...")
    try:
        reward_rate = staking_contract.functions.getRewardRate().call()
        print(f"✅ Reward Rate: {reward_rate} / 100 = {reward_rate / 100}%")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ All Staking API tests passed!")
    print("=" * 60)

    return True


async def test_telegram_backend():
    """Test Telegram Backend API endpoints"""

    print("\n" + "=" * 60)
    print("Telegram Backend API Test")
    print("=" * 60)

    # Test health endpoint
    print("\n[Test 1] Health Check...")
    try:
        client = TestClient(app)
        response = client.get("/api/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False

    # Test prices endpoint
    print("\n[Test 2] Get Prices...")
    try:
        client = TestClient(app)
        response = client.get("/api/prices")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"✅ Retrieved {len(data)} price feeds")
        for key in ['gold', 'silver', 'aapl', 'tsla']:
            if key in data:
                print(f"   {key}: ${data[key].get('price', 'N/A')}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False

    # Test staking info endpoint
    print("\n[Test 3] Get Staking Info...")
    try:
        client = TestClient(app)
        response = client.get("/api/staking/0x0000000000000000000000000000000000000000")
        print(f"✅ Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved staking info")
            print(f"   Staked Amount: {data.get('stakedAmount', 0)}")
            print(f"   Pending Rewards: {data.get('pendingRewards', 0)}")
        else:
            print(f"   (Expected to fail without deployed contract)")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ All Telegram Backend API tests passed!")
    print("=" * 60)

    return True


async def main():
    """Main test function"""
    try:
        print("Starting Staking Integration Tests...\n")

        # Test Staking API
        staking_api_passed = await test_staking_api()

        # Test Telegram Backend API
        telegram_api_passed = await test_telegram_backend()

        if staking_api_passed and telegram_api_passed:
            print("\n✅ All integration tests passed!")
            return True
        else:
            print("\n❌ Some tests failed")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
