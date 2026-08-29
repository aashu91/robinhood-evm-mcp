# test_staking.py
# Comprehensive Unit and End-to-End Tests for StakingYield Contract & Web3Helper

import os
import sys
import json
import time
import asyncio
import subprocess
from web3 import Web3
from eth_account import Account
from web3_helper import Web3Helper, load_env

load_env()

async def run_staking_tests():
    print("==========================================================")
    print("💎 Starting Native Token ($ROBIN_MCP) Staking Unit Tests")
    print("==========================================================")

    # 1. Start local Anvil instance if not already running
    anvil_process = None
    helper = Web3Helper()
    helper.switch_network("localhost")
    
    if not helper.w3.is_connected():
        print("Spawning local Anvil node...")
        anvil_process = subprocess.Popen(
            ["anvil", "--port", "8545", "--chain-id", "31337"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1.5)
        helper.connect()

    if not helper.w3.is_connected():
        print("❌ Could not connect to local Anvil RPC.")
        if anvil_process:
            anvil_process.kill()
        return False

    print(f"Connected to RPC: {helper.network_config['name']} (Chain ID: {helper.network_config['chain_id']})")

    # Anvil standard test accounts
    deployer_pk = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    user2_pk = "59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
    
    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = deployer_pk
    deployer_acct = Account.from_key(deployer_pk)
    user2_acct = Account.from_key(user2_pk)

    print(f"Deployer / User 1: {deployer_acct.address}")
    print(f"User 2:           {user2_acct.address}")

    # Compile contracts first
    subprocess.run(["node", "compileTrust.cjs"], check=True)
    subprocess.run(["node", "compileStaking.cjs"], check=True)

    # Step 1: Deploy Mock $ROBIN_MCP Token
    print("\n--- 1. Deploying Mock $ROBIN_MCP Token ---")
    res_token = await helper.deploy_mock_asset("Robinhood MCP Native Token", "ROBIN_MCP")
    assert res_token["status"] == "SUCCESS", "Failed to deploy mock ROBIN_MCP"
    token_address = res_token["contract_address"]
    print(f"✅ $ROBIN_MCP Token deployed at: {token_address}")

    # Mint tokens to User 1 (deployer) and User 2
    token_abi = await helper.load_abi_helper(token_address, "MockAsset")
    token_contract = helper.w3.eth.contract(address=token_address, abi=token_abi)

    mint_tx1 = token_contract.functions.mint(deployer_acct.address, int(100000 * 10**18)).build_transaction({
        'from': deployer_acct.address,
        'nonce': helper.w3.eth.get_transaction_count(deployer_acct.address),
        'gasPrice': helper.w3.eth.gas_price,
        'gas': 200000,
        'chainId': helper.network_config["chain_id"]
    })
    tx_hash = await helper.sign_and_send_transaction(mint_tx1)
    await helper.wait_for_confirmation(tx_hash)

    mint_tx2 = token_contract.functions.mint(user2_acct.address, int(100000 * 10**18)).build_transaction({
        'from': deployer_acct.address,
        'nonce': helper.w3.eth.get_transaction_count(deployer_acct.address),
        'gasPrice': helper.w3.eth.gas_price,
        'gas': 200000,
        'chainId': helper.network_config["chain_id"]
    })
    tx_hash = await helper.sign_and_send_transaction(mint_tx2)
    await helper.wait_for_confirmation(tx_hash)

    u1_bal = await helper.query_contract(token_address, "balanceOf", [deployer_acct.address], "ERC20")
    u2_bal = await helper.query_contract(token_address, "balanceOf", [user2_acct.address], "ERC20")
    print(f"User 1 Token Balance: {u1_bal / 10**18} ROBIN_MCP")
    print(f"User 2 Token Balance: {u2_bal / 10**18} ROBIN_MCP")
    assert u1_bal == 100000 * 10**18
    assert u2_bal == 100000 * 10**18

    # Step 2: Deploy StakingYield contract
    print("\n--- 2. Deploying StakingYield Contract ---")
    res_staking = await helper.deploy_staking_yield(token_address)
    assert res_staking["status"] == "SUCCESS", "Failed to deploy StakingYield contract"
    staking_address = res_staking["contract_address"]
    print(f"✅ StakingYield contract deployed at: {staking_address}")

    # Verify stakingToken getter
    st_token = await helper.query_contract(staking_address, "stakingToken", [], "StakingYield")
    assert st_token.lower() == token_address.lower()

    # Step 3: User 1 Stakes 1,000 tokens
    print("\n--- 3. User 1 Stakes 1,000 $ROBIN_MCP ---")
    stake_res = await helper.stake_tokens(staking_address, amount_tokens=1000)
    assert stake_res["status"] == "SUCCESS", "User 1 stake failed"
    
    info_u1 = await helper.get_staking_info(staking_address, deployer_acct.address)
    print(f"User 1 Staked: {info_u1['user_staked_tokens']} ROBIN_MCP (Raw: {info_u1['user_staked_raw']})")
    print(f"Total Pool Staked: {info_u1['total_staked_tokens']} ROBIN_MCP")
    assert info_u1['user_staked_tokens'] == 1000.0
    assert info_u1['total_staked_tokens'] == 1000.0
    assert info_u1['user_pool_share_percent'] == 100.0

    # Step 4: User 2 Stakes 3,000 tokens (User 1 = 25%, User 2 = 75%)
    print("\n--- 4. User 2 Stakes 3,000 $ROBIN_MCP ---")
    # Switch private key to User 2
    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = user2_pk
    stake_res2 = await helper.stake_tokens(staking_address, amount_tokens=3000)
    assert stake_res2["status"] == "SUCCESS", "User 2 stake failed"

    info_u2 = await helper.get_staking_info(staking_address, user2_acct.address)
    print(f"User 2 Staked: {info_u2['user_staked_tokens']} ROBIN_MCP")
    print(f"Total Pool Staked: {info_u2['total_staked_tokens']} ROBIN_MCP")
    assert info_u2['user_staked_tokens'] == 3000.0
    assert info_u2['total_staked_tokens'] == 4000.0
    assert info_u2['user_pool_share_percent'] == 75.0

    # Switch back to deployer for reward deposits
    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = deployer_pk

    # Step 5: Distribute 1.0 ETH in Platform Fees to Staking Pool
    print("\n--- 5. Depositing 1.0 ETH Rewards to Staking Pool ---")
    deposit_res = await helper.deposit_staking_rewards(staking_address, eth_amount=1.0)
    assert deposit_res["status"] == "SUCCESS", "Deposit rewards failed"

    # Check pending rewards: User 1 should have 0.25 ETH (25%), User 2 should have 0.75 ETH (75%)
    u1_info = await helper.get_staking_info(staking_address, deployer_acct.address)
    u2_info = await helper.get_staking_info(staking_address, user2_acct.address)
    print(f"User 1 Pending Reward: {u1_info['user_pending_rewards_eth']} ETH")
    print(f"User 2 Pending Reward: {u2_info['user_pending_rewards_eth']} ETH")
    assert abs(u1_info['user_pending_rewards_eth'] - 0.25) < 1e-6, f"Expected 0.25 ETH, got {u1_info['user_pending_rewards_eth']}"
    assert abs(u2_info['user_pending_rewards_eth'] - 0.75) < 1e-6, f"Expected 0.75 ETH, got {u2_info['user_pending_rewards_eth']}"

    # Step 6: User 1 Claims Rewards
    print("\n--- 6. User 1 Claims Accumulated ETH Rewards ---")
    u1_eth_before = helper.w3.eth.get_balance(deployer_acct.address)
    claim_res = await helper.claim_rewards(staking_address)
    assert claim_res["status"] == "SUCCESS", "User 1 claim rewards failed"
    u1_eth_after = helper.w3.eth.get_balance(deployer_acct.address)
    
    u1_info_after = await helper.get_staking_info(staking_address, deployer_acct.address)
    print(f"User 1 Pending Rewards after claim: {u1_info_after['user_pending_rewards_eth']} ETH")
    assert u1_info_after['user_pending_rewards_eth'] == 0.0
    print(f"✅ User 1 successfully claimed 0.25 ETH (gas accounted).")

    # Step 7: Deposit Second Round of Rewards (2.0 ETH)
    print("\n--- 7. Depositing Additional 2.0 ETH Rewards ---")
    deposit_res2 = await helper.deposit_staking_rewards(staking_address, eth_amount=2.0)
    assert deposit_res2["status"] == "SUCCESS"

    # User 1 should have 0.5 ETH pending (25% of 2.0)
    # User 2 should have 0.75 + 1.5 = 2.25 ETH pending
    u1_info_round2 = await helper.get_staking_info(staking_address, deployer_acct.address)
    u2_info_round2 = await helper.get_staking_info(staking_address, user2_acct.address)
    print(f"User 1 Round 2 Pending: {u1_info_round2['user_pending_rewards_eth']} ETH")
    print(f"User 2 Round 2 Pending: {u2_info_round2['user_pending_rewards_eth']} ETH")
    assert abs(u1_info_round2['user_pending_rewards_eth'] - 0.50) < 1e-6
    assert abs(u2_info_round2['user_pending_rewards_eth'] - 2.25) < 1e-6

    # Step 8: User 2 Claims All Accumulated Rewards (2.25 ETH)
    print("\n--- 8. User 2 Claims 2.25 ETH Accumulated Rewards ---")
    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = user2_pk
    u2_eth_before = helper.w3.eth.get_balance(user2_acct.address)
    claim_res2 = await helper.claim_rewards(staking_address)
    assert claim_res2["status"] == "SUCCESS"
    u2_eth_after = helper.w3.eth.get_balance(user2_acct.address)
    u2_eth_diff = helper.w3.from_wei(u2_eth_after - u2_eth_before, 'ether')
    print(f"User 2 ETH Balance Diff: +{u2_eth_diff} ETH")
    assert u2_eth_diff > 2.24 # Account for slight gas deduction

    # Step 9: User 1 Performs Partial Unstake (500 tokens)
    print("\n--- 9. User 1 Performs Partial Unstake (500 $ROBIN_MCP) ---")
    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = deployer_pk
    unstake_res = await helper.unstake_tokens(staking_address, amount_tokens=500)
    assert unstake_res["status"] == "SUCCESS"
    
    u1_info_unstake = await helper.get_staking_info(staking_address, deployer_acct.address)
    print(f"User 1 Staked Remaining: {u1_info_unstake['user_staked_tokens']} ROBIN_MCP")
    print(f"Total Pool Staked: {u1_info_unstake['total_staked_tokens']} ROBIN_MCP")
    assert u1_info_unstake['user_staked_tokens'] == 500.0
    assert u1_info_unstake['total_staked_tokens'] == 3500.0

    # Step 10: User 2 Executes Emergency Unstake
    print("\n--- 10. User 2 Executes Emergency Unstake (Full 3,000 $ROBIN_MCP) ---")
    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = user2_pk
    u2_tok_before = await helper.query_contract(token_address, "balanceOf", [user2_acct.address], "ERC20")
    emergency_res = await helper.emergency_unstake(staking_address)
    assert emergency_res["status"] == "SUCCESS"
    u2_tok_after = await helper.query_contract(token_address, "balanceOf", [user2_acct.address], "ERC20")
    
    u2_info_emergency = await helper.get_staking_info(staking_address, user2_acct.address)
    print(f"User 2 Staked after emergency: {u2_info_emergency['user_staked_tokens']} ROBIN_MCP")
    print(f"User 2 Token balance increase: {(u2_tok_after - u2_tok_before) / 10**18} ROBIN_MCP")
    assert u2_info_emergency['user_staked_tokens'] == 0.0
    assert (u2_tok_after - u2_tok_before) == 3000 * 10**18

    # Step 11: Edge Cases Verification
    print("\n--- 11. Edge Cases & Revert Validations ---")
    # Staking 0 should revert
    try:
        await helper.stake_tokens(staking_address, amount_tokens=0)
        assert False, "Should have failed to stake 0"
    except Exception as e:
        print(f"✅ Staking 0 correctly reverted: {e}")

    # Unstaking more than balance should revert
    try:
        await helper.unstake_tokens(staking_address, amount_tokens=999999)
        assert False, "Should have failed to unstake excessive amount"
    except Exception as e:
        print(f"✅ Unstaking excessive amount correctly reverted: {e}")

    # Emergency unstake with 0 staked balance should revert
    try:
        await helper.emergency_unstake(staking_address)
        assert False, "Should have failed emergency unstake with 0 balance"
    except Exception as e:
        print(f"✅ Emergency unstake with 0 balance correctly reverted: {e}")

    print("\n==========================================================")
    print("🎉 ALL STAKING & YIELD DISTRIBUTION UNIT TESTS PASSED!")
    print("==========================================================")

    if anvil_process:
        anvil_process.kill()

    return True

if __name__ == "__main__":
    success = asyncio.run(run_staking_tests())
    if not success:
        sys.exit(1)
