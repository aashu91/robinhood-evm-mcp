# deploy_native_token.py
# Script to launch the native utility token ($ROBIN_MCP) on Robinhood Chain Mainnet

import asyncio
import os
import json
from web3_helper import Web3Helper, load_env

load_env()

async def main():
    print("==============================================")
    print("🚀 Launching Native Utility Token on Mainnet")
    print("==============================================")
    
    helper = Web3Helper()
    w3 = helper.w3
    
    account = helper.get_account()
    print(f"Deployer Wallet Address: {account.address}")
    
    # Check balance
    bal = w3.eth.get_balance(account.address)
    bal_eth = w3.from_wei(bal, 'ether')
    print(f"Current Wallet Balance: {bal_eth} ETH")
    
    factory_address = os.getenv("MEME_FACTORY_ADDRESS")
    if not factory_address:
        print("❌ Error: MEME_FACTORY_ADDRESS not set in .env")
        return
        
    print(f"Using MemeFactory at: {factory_address}")
    
    # Query deploy fee from factory on-chain
    try:
        deploy_fee = await helper.query_contract(factory_address, "deployFee", [], "MemeFactory")
        print(f"Factory Deploy Fee: {w3.from_wei(deploy_fee, 'ether')} ETH")
    except Exception as e:
        print(f"⚠️ Failed to query deploy fee: {e}. Defaulting to 0.005 ETH estimation.")
        deploy_fee = w3.to_wei(0.005, 'ether')

    if bal < deploy_fee:
        print(f"\n❌ Error: Insufficient balance.")
        print(f"You need at least {w3.from_wei(deploy_fee, 'ether')} ETH + gas to deploy.")
        print(f"Please transfer some ETH to: {account.address} on Robinhood Chain Mainnet and run this script again.")
        print("Command to run: python deploy_native_token.py")
        return
        
    token_name = "Robinhood MCP Token"
    token_symbol = "ROBIN_MCP"
    token_supply = 1000000000 # 1 Billion
    
    print(f"\nDeploying Token:")
    print(f"- Name: {token_name}")
    print(f"- Symbol: {token_symbol}")
    print(f"- Supply: {token_supply}")
    print("\nBroadcasting transaction...")
    
    try:
        receipt = await helper.deploy_meme_token(
            name=token_name,
            symbol=token_symbol,
            supply=token_supply,
            value_wei=deploy_fee
        )
        print("\n==============================================")
        print("🎉 Token Deployed Successfully!")
        print("==============================================")
        print(json.dumps(receipt, indent=2))
        
        # Query latest deployed token address
        count = await helper.query_contract(factory_address, "getMemeCount", [], "MemeFactory")
        token_address = await helper.query_contract(factory_address, "allMemeTokens", [count - 1], "MemeFactory")
        print(f"\nDeployed Token Contract Address: {token_address}")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
