# deploy_v2_and_native.py
import asyncio
import os
import json
from web3 import Web3
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

async def main():
    print("==============================================")
    print("🚀 Deploying MemeFactoryV2 & Native Token")
    print("==============================================")
    
    # 1. Initialize Web3
    rpc_url = "https://rpc.mainnet.chain.robinhood.com"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("❌ Failed to connect to Mainnet RPC.")
        return
        
    chain_id = w3.eth.chain_id
    print(f"Connected to Mainnet (Chain ID: {chain_id})")

    # 2. Get Account
    private_key = os.getenv("ROBINHOOD_CHAIN_PRIVATE_KEY")
    if not private_key:
        print("❌ Error: ROBINHOOD_CHAIN_PRIVATE_KEY not set in .env")
        return
    if private_key.startswith("0x"):
        private_key = private_key[2:]
        
    account = w3.eth.account.from_key(private_key)
    print(f"Deployer Wallet Address: {account.address}")
    
    # Check balance
    bal = w3.eth.get_balance(account.address)
    bal_eth = w3.from_wei(bal, 'ether')
    print(f"Wallet Balance: {bal_eth} ETH")
    
    if bal < w3.to_wei(0.001, 'ether'):
        print("❌ Error: Balance too low. Need at least 0.001 ETH to cover gas and fees.")
        return

    # 3. Load V2 Artifacts
    artifact_path = "MemeFactoryV2.json"
    if not os.path.exists(artifact_path):
        print(f"❌ Error: {artifact_path} not found. Run 'node compileV2.cjs' first.")
        return
        
    with open(artifact_path, "r") as f:
        artifact = json.load(f)
        
    abi = artifact["abi"]
    bytecode = artifact["bytecode"]

    # 4. Get Payout Fee Recipient
    fee_recipient = os.getenv("AFFILIATE_FEE_RECIPIENT") or account.address
    fee_recipient = w3.to_checksum_address(fee_recipient)
    print(f"Fee Recipient: {fee_recipient}")

    # 5. Deploy MemeFactoryV2
    print("\nDeploying MemeFactoryV2...")
    ContractFactory = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = int(w3.eth.gas_price * 1.1)
    
    construct_tx = ContractFactory.constructor(fee_recipient).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': 8000000,
        'chainId': chain_id
    })
    
    signed_tx = w3.eth.account.sign_transaction(construct_tx, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Deploy Tx Hash: {w3.to_hex(tx_hash)}")
    
    print("Waiting for deployment confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    
    if receipt.get("status") != 1:
        print("❌ Deployment failed.")
        return
        
    factory_address = receipt.contractAddress
    print(f"✅ MemeFactoryV2 deployed at: {factory_address}")
    
    # 6. Save new address to .env
    env_file_path = ".env"
    env_lines = []
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as f:
            env_lines = f.readlines()
            
    new_lines = []
    for line in env_lines:
        if not line.strip().startswith("MEME_FACTORY_ADDRESS="):
            new_lines.append(line)
    new_lines.append(f"\nMEME_FACTORY_ADDRESS={factory_address}\n")
    
    with open(env_file_path, "w") as f:
        f.writelines(new_lines)
    print("✅ Updated MEME_FACTORY_ADDRESS in .env")

    # 7. Deploy ROBIN_MCP Native Token
    print("\nDeploying Native Utility Token (ROBIN_MCP)...")
    factory_contract = w3.eth.contract(address=factory_address, abi=abi)
    
    token_name = "Robinhood MCP Token"
    token_symbol = "ROBIN_MCP"
    token_supply = 1000000000 # 1 Billion (V2 scales inside constructor)
    
    deploy_fee = w3.to_wei(0.0001, 'ether') # V2 deploy fee is 0.0001 ETH
    
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = int(w3.eth.gas_price * 1.1)
    
    token_tx = factory_contract.functions.deployMemeToken(
        token_name, token_symbol, token_supply
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': 4000000,
        'value': deploy_fee,
        'chainId': chain_id
    })
    
    signed_token_tx = w3.eth.account.sign_transaction(token_tx, private_key=private_key)
    token_tx_hash = w3.eth.send_raw_transaction(signed_token_tx.raw_transaction)
    print(f"Token Deploy Tx Hash: {w3.to_hex(token_tx_hash)}")
    
    print("Waiting for token deployment confirmation...")
    token_receipt = w3.eth.wait_for_transaction_receipt(token_tx_hash, timeout=120)
    
    if token_receipt.get("status") != 1:
        print("❌ Token deployment transaction reverted.")
        return
        
    print("✅ Token deployment transaction confirmed.")
    
    # Query deployed token address
    meme_count = factory_contract.functions.getMemeCount().call()
    token_address = factory_contract.functions.allMemeTokens(meme_count - 1).call()
    
    print("\n==============================================")
    print("🎉 Success! Launchpad Native Token Launched!")
    print("==============================================")
    print(f"Factory Address: {factory_address}")
    print(f"Token Name:      {token_name}")
    print(f"Token Ticker:    {token_symbol}")
    print(f"Token Address:   {token_address}")
    print(f"Remaining Bal:   {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} ETH")
    print("==============================================")

if __name__ == "__main__":
    asyncio.run(main())
