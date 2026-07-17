# github_payout_bot.py
# Automated bot to reward contributors on-chain with $ROBIN_MCP tokens upon PR merge

import os
import re
import json
import asyncio
import subprocess
from web3_helper import Web3Helper

# Setup local env loader
def load_all_envs():
    for path in [os.path.expanduser("~/.env"), ".env"]:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_all_envs()

PAYOUT_DATABASE = "payouts.json"
BOUNTY_REWARD = 50000 # 50k $ROBIN_MCP per PR merge

# Load already paid PRs
def load_payouts():
    if os.path.exists(PAYOUT_DATABASE):
        with open(PAYOUT_DATABASE, "r") as f:
            return json.load(f)
    return {}

def save_payouts(payouts):
    with open(PAYOUT_DATABASE, "w") as f:
        json.dump(payouts, f, indent=2)

async def process_payouts():
    print("==============================================")
    print("🤖 Starting GitHub Bounty Payout Bot")
    print("==============================================")
    
    # 1. Initialize Web3
    helper = Web3Helper()
    w3 = helper.w3
    account = helper.get_account()
    
    token_address = os.getenv("ROBIN_MCP_TOKEN_ADDRESS")
    if not token_address:
        print("❌ Error: ROBIN_MCP_TOKEN_ADDRESS not set in .env")
        return
        
    token_address = w3.to_checksum_address(token_address)
    print(f"Deployer Wallet: {account.address}")
    print(f"Bounty Token Address: {token_address}")
    
    # Load past payouts
    payouts = load_payouts()
    
    # 2. Fetch merged PRs from GitHub via gh CLI
    print("\nFetching merged pull requests from GitHub...")
    repo = "aashu91/robinhood-evm-mcp"
    cmd = [
        "gh", "pr", "list",
        "--state", "merged",
        "--repo", repo,
        "--json", "number,title,body,author",
        "--limit", "50"
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"❌ Failed to fetch PRs: {res.stderr.strip()}")
        return
        
    try:
        prs = json.loads(res.stdout)
    except Exception as parse_err:
        print(f"❌ Failed to parse JSON output: {parse_err}")
        return
        
    print(f"Found {len(prs)} merged pull requests.")
    
    # 3. Process each PR
    wallet_regex = re.compile(r"wallet:\s*(0x[a-fA-F0-9]{40})", re.IGNORECASE)
    
    for pr in prs:
        pr_number = str(pr["number"])
        pr_title = pr["title"]
        pr_body = pr.get("body", "")
        author = pr.get("author", {}).get("login", "unknown")
        
        # Skip if already paid
        if pr_number in payouts:
            continue
            
        print(f"\nEvaluating PR #{pr_number} by @{author}: '{pr_title}'")
        
        # Search for wallet address in body
        match = wallet_regex.search(pr_body)
        if not match:
            print("⚠️ No wallet address found in PR description. Skipping...")
            continue
            
        contributor_wallet = w3.to_checksum_address(match.group(1))
        print(f"📍 Detected Contributor Wallet: {contributor_wallet}")
        
        # 4. Execute on-chain payout transfer
        amount_wei = BOUNTY_REWARD * (10**18)
        print(f"Broadcasting transfer of {BOUNTY_REWARD} $ROBIN_MCP...")
        
        try:
            # Build transfer call using MockAsset ABI (ERC20 standard signatures)
            tx = await helper.estimate_and_build_tx(
                contract_address=token_address,
                function_name="transfer",
                args=[contributor_wallet, amount_wei],
                abi_type="MockAsset"
            )
            
            tx_hash = await helper.sign_and_send_transaction(tx)
            print(f"Transaction sent. Hash: {w3.to_hex(tx_hash)}")
            
            # Wait for receipt
            receipt = await helper.wait_for_confirmation(tx_hash)
            if receipt.get("status") == 1:
                print(f"✅ Success! Paid 50,000 $ROBIN_MCP bounty to @{author}.")
                
                # Record payout
                payouts[pr_number] = {
                    "author": author,
                    "wallet": contributor_wallet,
                    "tx_hash": w3.to_hex(tx_hash),
                    "amount": BOUNTY_REWARD
                }
                save_payouts(payouts)
            else:
                print(f"❌ Transaction reverted.")
                
        except Exception as tx_err:
            print(f"❌ Transaction failed: {tx_err}")
            
    print("\n==============================================")
    print("🏁 Payout processing complete.")
    print("==============================================")

import argparse

async def main():
    parser = argparse.ArgumentParser(description="GitHub Payout Bot Daemon")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in a loop")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds (default: 60)")
    args = parser.parse_args()
    
    if args.daemon:
        print(f"Starting payout bot in daemon mode (polling every {args.interval}s)...")
        try:
            while True:
                await process_payouts()
                await asyncio.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nShutting down payout daemon gracefully.")
    else:
        await process_payouts()

if __name__ == "__main__":
    asyncio.run(main())
