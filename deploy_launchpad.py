# deploy_launchpad.py
# Automated deployment script for MemeFactory on Robinhood Chain

import os
import json
import asyncio
from web3 import Web3
from eth_account import Account
from web3_helper import load_env, Web3Helper

load_env()

async def deploy():
    print("==================================================")
    print("🚀 Deploying MemeFactory to Robinhood Chain...")
    print("==================================================")

    # 1. Initialize Web3
    helper = Web3Helper()
    w3 = helper.w3
    if not w3.is_connected():
        print("❌ Failed to connect to the Robinhood Chain RPC.")
        return

    print(f"Connected to: {helper.network_config['name']} (Chain ID: {helper.network_config['chain_id']})")

    # 2. Load Account
    try:
        account = helper.get_account()
        print(f"Deployer Wallet Address: {account.address}")
        
        # Check balance
        bal = w3.eth.get_balance(account.address)
        bal_eth = w3.from_wei(bal, 'ether')
        print(f"Deployer Wallet Balance: {bal_eth} ETH")
        if bal == 0:
            print("❌ Deployer wallet has 0 ETH. Please fund the wallet to cover gas fees.")
            return
    except Exception as e:
        print(f"❌ Error loading deployer wallet private key: {str(e)}")
        return

    # 3. Load Compilation Artifacts
    artifact_path = "MemeFactory.json"
    if not os.path.exists(artifact_path):
        print(f"❌ Artifact '{artifact_path}' not found. Run 'node compile.cjs' first.")
        return

    with open(artifact_path, "r") as f:
        artifact = json.load(f)
    
    abi = artifact["abi"]
    bytecode = artifact["bytecode"]

    # 4. Get Payout Fee Recipient
    # Default to deployer wallet if AFFILIATE_FEE_RECIPIENT not set
    payout_address = os.getenv("AFFILIATE_FEE_RECIPIENT") or account.address
    payout_address = w3.to_checksum_address(payout_address)
    print(f"Payout Fee Recipient: {payout_address}")

    # 5. Build Deployment Transaction
    ContractFactory = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = int(w3.eth.gas_price * 1.1)

    print("Building transaction...")
    # MemeFactory constructor takes: address payable _feeRecipient
    construct_tx = ContractFactory.constructor(payout_address).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gasPrice': gas_price,
        'chainId': helper.network_config["chain_id"]
    })

    # Estimate Gas
    try:
        gas_estimate = w3.eth.estimate_gas(construct_tx)
        construct_tx['gas'] = int(gas_estimate * 1.2)
        print(f"Estimated Gas: {construct_tx['gas']}")
    except Exception as est_err:
        print(f"⚠️ Gas estimation failed: {str(est_err)}. Using default 3,000,000 gas limit.")
        construct_tx['gas'] = 3000000

    # 6. Sign and Send
    print("Signing transaction...")
    signed_tx = w3.eth.account.sign_transaction(construct_tx, private_key=account.key)
    
    print("Broadcasting transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hex = w3.to_hex(tx_hash)
    print(f"Transaction hash: {tx_hex}")

    # 7. Wait for receipt
    print("Waiting for transaction confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt.get("status") == 1:
        contract_address = receipt.contractAddress
        print(f"✅ MemeFactory deployed successfully!")
        print(f"Contract Address: {contract_address}")
        
        # 8. Save Address to .env file
        env_file_path = os.path.expanduser("~/.env")
        if os.path.exists(".env"):
            env_file_path = ".env"
            
        print(f"Updating {env_file_path}...")
        
        # Read existing variables
        env_lines = []
        if os.path.exists(env_file_path):
            with open(env_file_path, "r") as f:
                env_lines = f.readlines()
        
        # Filter out existing MEME_FACTORY_ADDRESS if present
        new_lines = []
        for line in env_lines:
            if not line.strip().startswith("MEME_FACTORY_ADDRESS="):
                new_lines.append(line)
        
        # Append new address
        new_lines.append(f"\nMEME_FACTORY_ADDRESS={contract_address}\n")
        
        with open(env_file_path, "w") as f:
            f.writelines(new_lines)
            
        print("✅ Environment variables updated.")
        print("You are ready to run the server!")
    else:
        print("❌ Transaction reverted/failed.")

if __name__ == "__main__":
    asyncio.run(deploy())
