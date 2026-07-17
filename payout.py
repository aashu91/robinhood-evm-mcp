# payout.py
# Local developer manual review and payout script for Termux/Linux environments.
# Usage: python payout.py <PR_NUMBER> [ETH_AMOUNT]

import os
import sys
import re
import urllib.request
import json
from web3 import Web3
from eth_account import Account

# Inline ABI for EcosystemTreasury contract to ensure zero-dependency execution
TREASURY_ABI = [
    {
        "inputs": [],
        "name": "devPoolBalance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "factoryAddress", "type": "address"},
            {"name": "tokenAddress", "type": "address"},
            {"name": "developer", "type": "address"},
            {"name": "ethAmount", "type": "uint256"}
        ],
        "name": "payoutDeveloperToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Helper to load .env variables manually
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

def get_pr_details(pr_number):
    """Fetches Pull Request information from GitHub API."""
    github_repo = os.getenv("GITHUB_REPO") or "salvationfinder/robinhood-evm-mcp"
    url = f"https://api.github.com/repos/{github_repo}/pulls/{pr_number}"
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"❌ Error fetching PR {pr_number} from GitHub: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python payout.py <PR_NUMBER> [ETH_AMOUNT]")
        sys.exit(1)

    pr_number = sys.argv[1]
    
    # Default payout ETH amount (for buyback) is 0.001 ETH if not specified
    eth_amount_str = sys.argv[2] if len(sys.argv) > 2 else "0.001"
    eth_amount = float(eth_amount_str)

    # 1. Load configuration
    rpc_url = os.getenv("ROBINHOOD_CHAIN_RPC_URL", "https://rpc.mainnet.chain.robinhood.com")
    private_key = os.getenv("ROBINHOOD_CHAIN_PRIVATE_KEY")
    factory_address = os.getenv("MEME_FACTORY_ADDRESS")
    treasury_address = os.getenv("ECOSYSTEM_TREASURY_ADDRESS")
    token_address = os.getenv("ROBIN_MCP_TOKEN_ADDRESS")

    if not private_key:
        print("❌ Error: ROBINHOOD_CHAIN_PRIVATE_KEY not set in your .env configuration.")
        sys.exit(1)
    if not treasury_address:
        print("❌ Error: ECOSYSTEM_TREASURY_ADDRESS not set in your .env configuration.")
        sys.exit(1)
    if not factory_address:
        print("❌ Error: MEME_FACTORY_ADDRESS not set in your .env configuration.")
        sys.exit(1)
    if not token_address:
        print("❌ Error: ROBIN_MCP_TOKEN_ADDRESS (target project utility token) not set in your .env configuration.")
        sys.exit(1)

    # 2. Fetch PR details
    print(f"🔍 Fetching details for PR #{pr_number}...")
    pr_data = get_pr_details(pr_number)

    pr_title = pr_data.get("title")
    pr_author = pr_data.get("user", {}).get("login")
    pr_body = pr_data.get("body") or ""

    # Parse EVM address from PR description
    evm_match = re.search(r"0x[a-fA-F0-9]{40}", pr_body)
    if not evm_match:
        print("❌ Error: No EVM wallet address (0x...) found in the PR description body.")
        print("Please ask the developer to edit the PR description to include their wallet.")
        sys.exit(1)

    developer_wallet = Web3.to_checksum_address(evm_match.group(0))

    # 3. Setup Web3 connection
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"❌ Error: Failed to connect to RPC network: {rpc_url}")
        sys.exit(1)

    account = Account.from_key(private_key)
    treasury_contract = w3.eth.contract(address=Web3.to_checksum_address(treasury_address), abi=TREASURY_ABI)

    # Fetch pool balance
    dev_pool_wei = treasury_contract.functions.devPoolBalance().call()
    dev_pool_eth = w3.from_wei(dev_pool_wei, 'ether')
    payout_wei = w3.to_wei(eth_amount, 'ether')

    print("\n" + "="*50)
    print("📋 PR VALIDATION SUMMARY")
    print("="*50)
    print(f"• PR Number:  #{pr_number}")
    print(f"• Title:      {pr_title}")
    print(f"• Contributor: @{pr_author}")
    print(f"• Target Dev:  {developer_wallet}")
    print(f"• Payout ETH:  {eth_amount} ETH")
    print(f"• Pool Bal:   {dev_pool_eth} ETH")
    print("="*50)

    if payout_wei > dev_pool_wei:
        print("❌ Error: Insufficient developer pool balance in EcosystemTreasury.")
        sys.exit(1)

    # 4. Prompt for manual confirmation
    confirm = input("\nConfirm payout signing and buyback trigger? [y/N]: ").strip().lower()
    if confirm != 'y' and confirm != 'yes':
        print("🚫 Payout execution cancelled by maintainer.")
        sys.exit(0)

    print("\n⏳ Building payout transaction...")
    
    # 5. Build, sign, and send transaction
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price

    tx = treasury_contract.functions.payoutDeveloperToken(
        Web3.to_checksum_address(factory_address),
        Web3.to_checksum_address(token_address),
        developer_wallet,
        payout_wei
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': 250000 # safe estimation cap for buyback swaps
    })

    print("✍️ Signing transaction...")
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    
    print("🚀 Broadcasting transaction...")
    raw_tx = getattr(signed_tx, "raw_transaction", None) or getattr(signed_tx, "rawTransaction")
    tx_hash = w3.eth.send_raw_transaction(raw_tx)
    print(f"Transaction sent! Hash: {tx_hash.hex()}")

    print("⏳ Waiting for transaction confirmation on-chain...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        print(f"\n✅ Success! Developer payout transaction mined successfully.")
        print(f"• Block Number: {receipt.blockNumber}")
        print(f"• Gas Used:     {receipt.gasUsed}")
    else:
        print(f"\n❌ Transaction execution failed on-chain. Check transaction logs.")

if __name__ == "__main__":
    main()
