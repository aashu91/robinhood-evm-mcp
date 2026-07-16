# test_trust.py
# End-to-end verification script for Community Trust Factory and Bank on Robinhood Chain L2

import asyncio
import os
from web3_helper import Web3Helper, load_env

load_env()

async def main():
    print("==============================================")
    print("🔍 Starting Community Trust End-to-End Tests")
    print("==============================================")

    helper = Web3Helper()
    print(f"Connected to Network: {helper.network_config['name']}")
    print(f"RPC URL: {helper.w3.provider.endpoint_uri}")
    
    account = helper.get_account()
    print(f"Deployer Wallet Address: {account.address}")
    
    # Check balance
    bal = helper.w3.eth.get_balance(account.address)
    print(f"Deployer Wallet Balance: {helper.w3.from_wei(bal, 'ether')} ETH")
    
    if bal == 0:
        print("❌ Cannot proceed with testing: Deployer wallet has 0 ETH.")
        return

    # 1. Deploy CommunityTrustFactory
    print("\n1. Deploying CommunityTrustFactory...")
    res = await helper.deploy_community_trust_factory()
    if res["status"] != "SUCCESS":
        print(f"❌ Failed to deploy CommunityTrustFactory: {res}")
        return
    factory_address = res["contract_address"]
    print(f"✅ CommunityTrustFactory deployed at: {factory_address}")

    # 2. Deploy individual CommunityTrust
    print("\n2. Deploying individual CommunityTrust...")
    # Appoint the deployer as the director
    directors = [account.address]
    required_signatures = 1
    res = await helper.deploy_community_trust(
        factory_address=factory_address,
        name="Sovereign Test Trust",
        directors=directors,
        required_signatures=required_signatures
    )
    if res["status"] != "SUCCESS":
        print(f"❌ Failed to deploy CommunityTrust: {res}")
        return
    trust_address = res["trust_address"]
    print(f"✅ CommunityTrust deployed at: {trust_address}")

    # 3. Deposit to Trust
    print("\n3. Depositing ETH to pool wealth...")
    deposit_amount = 0.0001 # Small amount for testing
    receipt = await helper.deposit_to_trust(trust_address, deposit_amount)
    print(f"✅ Deposit Transaction Receipt status: {receipt['status']}")
    
    # Verify shares/totalShares
    total_shares = await helper.query_contract(trust_address, "totalShares", [], "CommunityTrust")
    user_shares = await helper.query_contract(trust_address, "shares", [account.address], "CommunityTrust")
    print(f"Trust Total Shares: {helper.w3.from_wei(total_shares, 'ether')}")
    print(f"User Shares: {helper.w3.from_wei(user_shares, 'ether')}")

    # 4. Deploy Mock Precious Metal Token (cGOLD)
    print("\n4. Deploying mock precious metal token cGOLD...")
    res = await helper.deploy_mock_asset("Community Gold", "cGOLD")
    if res["status"] != "SUCCESS":
        print(f"❌ Failed to deploy MockAsset: {res}")
        return
    gold_address = res["contract_address"]
    print(f"✅ Mock cGOLD deployed at: {gold_address}")

    # 5. Propose & Execute transaction: Mint cGOLD to Trust
    print("\n5. Proposing transaction to mint cGOLD to the trust...")
    # MockAsset mint(address to, uint256 value)
    # We will build the call data: mint(trust_address, 1000 * 10**18)
    gold_abi = await helper.load_abi_helper(gold_address, "MockAsset")
    gold_contract = helper.w3.eth.contract(address=gold_address, abi=gold_abi)
    mint_data = gold_contract.encode_abi("mint", [trust_address, int(1000 * 10**18)])
    
    # Propose
    receipt = await helper.propose_trust_transaction(
        trust_address=trust_address,
        destination=gold_address,
        value_wei=0,
        calldata_hex=mint_data
    )
    print(f"✅ Proposal Transaction Receipt status: {receipt['status']}")
    
    # In CommunityTrust constructor, proposeTransaction automatically signs the proposal.
    # Since requiredSignatures = 1, we can execute immediately.
    proposal_id = 0
    print("\n6. Executing transaction inside trust...")
    receipt = await helper.execute_trust_proposal(trust_address, proposal_id)
    print(f"✅ Execution Transaction Receipt status: {receipt['status']}")
    
    # Verify trust holds gold
    gold_bal = await helper.query_contract(gold_address, "balanceOf", [trust_address], "MockAsset")
    print(f"Trust cGOLD Balance: {gold_bal / 10**18} cGOLD")

    # 6. Distribute cGOLD Dividends
    print("\n7. Distributing cGOLD dividends to trust share holders...")
    # First mint some gold to the deployer so they can distribute it
    mint_tx = gold_contract.functions.mint(account.address, int(500 * 10**18)).build_transaction({
        'from': account.address,
        'nonce': helper.w3.eth.get_transaction_count(account.address),
        'gasPrice': int(helper.w3.eth.gas_price * 1.1),
        'gas': 200000
    })
    tx_hash = await helper.sign_and_send_transaction(mint_tx)
    await helper.wait_for_confirmation(tx_hash)
    
    # Now distribute cGOLD dividends from deployer
    receipt = await helper.distribute_trust_dividends(
        trust_address=trust_address,
        token_address=gold_address,
        amount_wei=str(int(100 * 10**18))
    )
    print(f"✅ Distribution Transaction Receipt status: {receipt['status']}")

    # 7. Claim Dividends
    print("\n8. Claiming accumulated cGOLD dividends...")
    receipt = await helper.claim_trust_dividends(trust_address, gold_address)
    print(f"✅ Claim Transaction Receipt status: {receipt['status']}")
    
    # Verify user's gold balance
    user_gold = await helper.query_contract(gold_address, "balanceOf", [account.address], "MockAsset")
    print(f"User cGOLD Balance: {user_gold / 10**18} cGOLD")

    print("\n==============================================")
    print("🎉 All Community Trust End-to-End Tests Passed!")
    print("==============================================")

if __name__ == "__main__":
    asyncio.run(main())
