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
    """
    Executes unit and integration test suite for StakingYield contract and Web3Helper methods.
    """
    anvil_process = None
    helper = Web3Helper()
    helper.switch_network("localhost")

    if not helper.w3.is_connected():
        anvil_process = subprocess.Popen(
            ["anvil", "--port", "8545", "--chain-id", "31337"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1.5)
        helper.connect()

    if not helper.w3.is_connected():
        if anvil_process:
            anvil_process.kill()
        return False

    deployer_pk = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    user2_pk = "59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"

    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = deployer_pk
    deployer_acct = Account.from_key(deployer_pk)
    user2_acct = Account.from_key(user2_pk)

    subprocess.run(["node", "compileTrust.cjs"], check=True)
    subprocess.run(["node", "compileStaking.cjs"], check=True)

    res_token = await helper.deploy_mock_asset("Robinhood MCP Native Token", "ROBIN_MCP")
    assert res_token["status"] == "SUCCESS", "Failed to deploy mock ROBIN_MCP"
    token_address = res_token["contract_address"]

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
    assert u1_bal == 100000 * 10**18
    assert u2_bal == 100000 * 10**18

    res_staking = await helper.deploy_staking_yield(token_address)
    assert res_staking["status"] == "SUCCESS", "Failed to deploy StakingYield contract"
    staking_address = res_staking["contract_address"]

    st_token = await helper.query_contract(staking_address, "stakingToken", [], "StakingYield")
    assert st_token.lower() == token_address.lower()

    stake_res = await helper.stake_tokens(staking_address, amount_tokens=1000)
    assert stake_res["status"] == "SUCCESS", "User 1 stake failed"

    info_u1 = await helper.get_staking_info(staking_address, deployer_acct.address)
    assert info_u1['user_staked_tokens'] == 1000.0
    assert info_u1['total_staked_tokens'] == 1000.0
    assert info_u1['user_pool_share_percent'] == 100.0

    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = user2_pk
    stake_res2 = await helper.stake_tokens(staking_address, amount_tokens=3000)
    assert stake_res2["status"] == "SUCCESS", "User 2 stake failed"

    info_u2 = await helper.get_staking_info(staking_address, user2_acct.address)
    assert info_u2['user_staked_tokens'] == 3000.0
    assert info_u2['total_staked_tokens'] == 4000.0
    assert info_u2['user_pool_share_percent'] == 75.0

    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = deployer_pk

    deposit_res = await helper.deposit_staking_rewards(staking_address, eth_amount=1.0)
    assert deposit_res["status"] == "SUCCESS", "Deposit rewards failed"

    u1_info = await helper.get_staking_info(staking_address, deployer_acct.address)
    u2_info = await helper.get_staking_info(staking_address, user2_acct.address)
    assert abs(u1_info['user_pending_rewards_eth'] - 0.25) < 1e-6, f"Expected 0.25 ETH, got {u1_info['user_pending_rewards_eth']}"
    assert abs(u2_info['user_pending_rewards_eth'] - 0.75) < 1e-6, f"Expected 0.75 ETH, got {u2_info['user_pending_rewards_eth']}"

    claim_res = await helper.claim_rewards(staking_address)
    assert claim_res["status"] == "SUCCESS", "User 1 claim rewards failed"

    u1_info_after = await helper.get_staking_info(staking_address, deployer_acct.address)
    assert u1_info_after['user_pending_rewards_eth'] == 0.0

    deposit_res2 = await helper.deposit_staking_rewards(staking_address, eth_amount=2.0)
    assert deposit_res2["status"] == "SUCCESS"

    u1_info_round2 = await helper.get_staking_info(staking_address, deployer_acct.address)
    u2_info_round2 = await helper.get_staking_info(staking_address, user2_acct.address)
    assert abs(u1_info_round2['user_pending_rewards_eth'] - 0.50) < 1e-6
    assert abs(u2_info_round2['user_pending_rewards_eth'] - 2.25) < 1e-6

    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = user2_pk
    u2_eth_before = helper.w3.eth.get_balance(user2_acct.address)
    claim_res2 = await helper.claim_rewards(staking_address)
    assert claim_res2["status"] == "SUCCESS"
    u2_eth_after = helper.w3.eth.get_balance(user2_acct.address)
    u2_eth_diff = helper.w3.from_wei(u2_eth_after - u2_eth_before, 'ether')
    assert u2_eth_diff > 2.24

    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = deployer_pk
    unstake_res = await helper.unstake_tokens(staking_address, amount_tokens=500)
    assert unstake_res["status"] == "SUCCESS"

    u1_info_unstake = await helper.get_staking_info(staking_address, deployer_acct.address)
    assert u1_info_unstake['user_staked_tokens'] == 500.0
    assert u1_info_unstake['total_staked_tokens'] == 3500.0

    os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = user2_pk
    u2_tok_before = await helper.query_contract(token_address, "balanceOf", [user2_acct.address], "ERC20")
    emergency_res = await helper.emergency_unstake(staking_address)
    assert emergency_res["status"] == "SUCCESS"
    u2_tok_after = await helper.query_contract(token_address, "balanceOf", [user2_acct.address], "ERC20")

    u2_info_emergency = await helper.get_staking_info(staking_address, user2_acct.address)
    assert u2_info_emergency['user_staked_tokens'] == 0.0
    assert (u2_tok_after - u2_tok_before) == 3000 * 10**18

    try:
        await helper.stake_tokens(staking_address, amount_tokens=0)
        assert False, "Should have failed to stake 0"
    except Exception:
        pass

    try:
        await helper.unstake_tokens(staking_address, amount_tokens=999999)
        assert False, "Should have failed to unstake excessive amount"
    except Exception:
        pass

    try:
        await helper.emergency_unstake(staking_address)
        assert False, "Should have failed emergency unstake with 0 balance"
    except Exception:
        pass

    if anvil_process:
        anvil_process.kill()

    return True

if __name__ == "__main__":
    success = asyncio.run(run_staking_tests())
    if not success:
        sys.exit(1)
    print("All staking tests passed successfully.")
