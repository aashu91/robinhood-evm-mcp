#!/usr/bin/env python3
"""
StakingYield Contract Deployment Script
Deploys StakingYield contract to Robinhood Chain
"""

import asyncio
import os
import sys
import json
from web3 import Web3
from eth_account import Account
from constants import NETWORKS, DEFAULT_NETWORK
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


async def deploy_staking_contract():
    """Deploy StakingYield contract"""

    print("=" * 60)
    print("StakingYield Contract Deployment")
    print("=" * 60)

    # Initialize Web3 helper
    web3_helper = Web3Helper()

    if not web3_helper.connect():
        print("❌ Failed to connect to RPC endpoint")
        return None

    # Get account from private key
    private_key = os.getenv("ROBINHOOD_CHAIN_PRIVATE_KEY") or os.getenv("EVM_PRIVATE_KEY")
    if not private_key:
        print("❌ No private key found. Set ROBINHOOD_CHAIN_PRIVATE_KEY in .env")
        return None

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
        print("Please compile the contract first:")
        print("  npx hardhat compile")
        return None

    with open(contract_path, "r") as f:
        contract_abi = json.load(f)

    # Deploy contract
    print("\n📡 Deploying StakingYield contract...")

    staking_contract = web3_helper.w3.eth.contract(
        abi=contract_abi,
        bytecode=contract_abi["bytecode"]
    )

    # Estimate gas
    gas_estimate = staking_contract.constructor(
        web3_helper.w3.to_checksum_address(os.getenv("PYTH_ORACLE_ADDRESS", "0x0000000000000000000000000000000000000000")),
        web3_helper.w3.to_checksum_address(os.getenv("CHAINLINK_ORACLE_ADDRESS", "0x0000000000000000000000000000000000000000"))
    ).estimate_gas()

    print(f"Estimated gas: {gas_estimate}")

    # Build transaction
    tx = staking_contract.constructor(
        web3_helper.w3.to_checksum_address(os.getenv("PYTH_ORACLE_ADDRESS", "0x0000000000000000000000000000000000000000")),
        web3_helper.w3.to_checksum_address(os.getenv("CHAINLINK_ORACLE_ADDRESS", "0x0000000000000000000000000000000000000000"))
    ).build_transaction({
        "from": account.address,
        "nonce": web3_helper.w3.eth.get_transaction_count(account.address),
        "gas": gas_estimate,
        "gasPrice": web3_helper.w3.eth.gas_price,
        "value": 0
    })

    # Sign transaction
    signed_tx = web3_helper.w3.eth.account.sign_transaction(tx, private_key)

    # Send transaction
    tx_hash = web3_helper.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"✅ Transaction sent: {web3_helper.w3.to_hex(tx_hash)}")

    # Wait for confirmation
    print("⏳ Waiting for confirmation...")
    tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    if tx_receipt.status == 1:
        print("✅ Contract deployed successfully!")

        # Get contract address
        contract_address = web3_helper.w3.to_checksum_address(tx_receipt.contractAddress)
        print(f"📍 Contract Address: {contract_address}")

        # Save to .env file
        env_path = os.path.expanduser("~/.env")
        if os.path.exists(env_path):
            with open(env_path, "a") as f:
                f.write(f"\n# StakingYield Contract\n")
                f.write(f"STAKING_CONTRACT_ADDRESS={contract_address}\n")

        print(f"\n✅ Contract address saved to .env file")

        return contract_address
    else:
        print("❌ Deployment failed")
        return None


async def main():
    """Main deployment function"""
    try:
        contract_address = await deploy_staking_contract()

        if contract_address:
            print("\n" + "=" * 60)
            print("✅ Deployment Complete!")
            print("=" * 60)
            print(f"Contract Address: {contract_address}")
            print("\nNext steps:")
            print("1. Add contract address to your .env file")
            print("2. Test the contract using test_trust.py")
            print("3. Integrate with MCP server")

        else:
            print("\n❌ Deployment failed")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
