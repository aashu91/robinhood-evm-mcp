#!/usr/bin/env python3
"""
StakingYield Contract Test Script
Tests all staking functionality
"""

import asyncio
import os
import sys
import json
from web3 import Web3
from eth_account import Account
from web3_helper import Web3Helper

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


async def test_staking_contract():
    """Test StakingYield contract"""

    print("=" * 60)
    print("StakingYield Contract Test")
    print("=" * 60)

    # Initialize Web3 helper
    web3_helper = Web3Helper()

    if not web3_helper.connect():
        print("❌ Failed to connect to RPC endpoint")
        return False

    # Get account from private key
    private_key = os.getenv("ROBINHOOD_CHAIN_PRIVATE_KEY") or os.getenv("EVM_PRIVATE_KEY")
    if not private_key:
        print("❌ No private key found. Set ROBINHOOD_CHAIN_PRIVATE_KEY in .env")
        return False

    if private_key.startswith("0x"):
        private_key = private_key[2:]

    account = Account.from_key(private_key)
    print(f"✅ Account: {account.address}")

    # Load StakingYield contract ABI
    contract_path = os.path.join(
        os.path.dirname(__file__),
        "contracts",
        "StakingYield.json"
    )

    if not os.path.exists(contract_path):
        print(f"❌ Contract ABI not found: {contract_path}")
        print("Please deploy the contract first:")
        print("  python deploy_staking.py")
        return False

    with open(contract_path, "r") as f:
        contract_abi = json.load(f)

    # Get contract address from .env
    contract_address = os.getenv("STAKING_CONTRACT_ADDRESS")
    if not contract_address:
        print("❌ No contract address found. Set STAKING_CONTRACT_ADDRESS in .env")
        return False

    contract_address = web3_helper.w3.to_checksum_address(contract_address)
    print(f"📍 Contract Address: {contract_address}")

    # Create contract instance
    staking_contract = web3_helper.w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    print("\n" + "=" * 60)
    print("Testing StakingYield Contract")
    print("=" * 60)

    # Test 1: Get contract info
    print("\n[Test 1] Getting contract info...")
    try:
        contract_balance = staking_contract.functions.getContractBalance().call()
        total_rewards = staking_contract.functions.getTotalRewards().call()
        reward_rate = staking_contract.functions.getRewardRate().call()
        print(f"✅ Contract Balance: {contract_balance} wei")
        print(f"✅ Total Rewards: {total_rewards} wei")
        print(f"✅ Reward Rate: {reward_rate} / 100 = {reward_rate / 100}%")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False

    # Test 2: Stake tokens
    print("\n[Test 2] Staking tokens...")
    try:
        stake_amount = 1 * 10**18  # 1 ETH/USDG
        tx_hash = staking_contract.functions.stake(stake_amount).transact({
            "from": account.address,
            "value": stake_amount,
            "gas": 200000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        if tx_receipt.status == 1:
            print(f"✅ Staked {stake_amount} wei")
        else:
            print(f"❌ Stake transaction failed")
            return False
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False

    # Test 3: Get user staking info
    print("\n[Test 3] Getting user staking info...")
    try:
        staked_amount, pending_rewards = staking_contract.functions.getUserStakingInfo(
            account.address
        ).call()
        print(f"✅ Staked Amount: {staked_amount} wei")
        print(f"✅ Pending Rewards: {pending_rewards} wei")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False

    # Test 4: Claim rewards
    print("\n[Test 4] Claiming rewards...")
    try:
        tx_hash = staking_contract.functions.claimRewards().transact({
            "from": account.address,
            "gas": 200000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        if tx_receipt.status == 1:
            print(f"✅ Rewards claimed successfully")
        else:
            print(f"❌ Claim transaction failed")
            return False
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False

    # Test 5: Unstake tokens
    print("\n[Test 5] Unstaking tokens...")
    try:
        unstake_amount = 1 * 10**18  # 1 ETH/USDG
        tx_hash = staking_contract.functions.unstake(unstake_amount).transact({
            "from": account.address,
            "gas": 200000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        if tx_receipt.status == 1:
            print(f"✅ Unstaked {unstake_amount} wei")
        else:
            print(f"❌ Unstake transaction failed")
            return False
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
        return False

    # Test 6: Update reward rate
    print("\n[Test 6] Updating reward rate...")
    try:
        new_rate = 50  # 0.5%
        tx_hash = staking_contract.functions.updateRewardRate(new_rate).transact({
            "from": account.address,
            "gas": 100000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
        if tx_receipt.status == 1:
            print(f"✅ Reward rate updated to {new_rate} / 100 = {new_rate / 100}%")
        else:
            print(f"❌ Update reward rate transaction failed")
            return False
    except Exception as e:
        print(f"❌ Test 6 failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

    return True


async def main():
    """Main test function"""
    try:
        success = await test_staking_contract()

        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
