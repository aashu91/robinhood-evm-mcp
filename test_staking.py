# test_staking.py
# Comprehensive unit tests for StakingYield contract, Web3Helper, and MCP Server integration.

import os
import sys
import json
import time
import asyncio
import subprocess
import pytest
from web3 import Web3
from eth_account import Account

# Add current repo directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from constants import NETWORKS, PREPACKAGED_ABIS
from web3_helper import Web3Helper
from mcp_server import dispatch_tool, helper as mcp_helper


class TestStakingSuite:
    anvil_process = None
    w3 = None
    helper = None
    account1 = None
    account2 = None
    token_address = None
    staking_address = None
    token_contract = None
    staking_contract = None

    @classmethod
    def setup_class(cls):
        """Starts an isolated local anvil node and initializes Web3 environment."""
        print("\nStarting local Anvil node...")
        cls.anvil_process = subprocess.Popen(
            ["/Users/solveetcoagula/.foundry/bin/anvil", "--port", "8545", "--chain-id", "31337", "--silent"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(1.5)

        cls.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        assert cls.w3.is_connected(), "Failed to connect to local Anvil RPC"

        # Standard Anvil Accounts
        # Account 1 (Deployer / User 1)
        cls.pk1 = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        cls.account1 = cls.w3.eth.account.from_key(cls.pk1)

        # Account 2 (User 2)
        cls.pk2 = "59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
        cls.account2 = cls.w3.eth.account.from_key(cls.pk2)

        os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = cls.pk1
        os.environ["ROBINHOOD_CHAIN_RPC_URL"] = "http://127.0.0.1:8545"

        cls.helper = Web3Helper()
        cls.helper.switch_network("localhost")
        mcp_helper.switch_network("localhost")

        # 1. Compile contracts if artifacts not present
        subprocess.run(["node", "compileTrust.cjs"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(["node", "compileStaking.cjs"], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))

        # 2. Deploy Mock Token ($ROBIN_MCP)
        with open("MockAsset.json", "r") as f:
            mock_artifact = json.load(f)
        TokenFactory = cls.w3.eth.contract(abi=mock_artifact["abi"], bytecode=mock_artifact["bytecode"])
        
        tx = TokenFactory.constructor("Robinhood MCP Token", "ROBIN_MCP").build_transaction({
            'from': cls.account1.address,
            'nonce': cls.w3.eth.get_transaction_count(cls.account1.address),
            'gas': 2000000,
            'gasPrice': cls.w3.eth.gas_price
        })
        signed = cls.w3.eth.account.sign_transaction(tx, cls.pk1)
        tx_hash = cls.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = cls.w3.eth.wait_for_transaction_receipt(tx_hash)
        cls.token_address = receipt.contractAddress
        cls.token_contract = cls.w3.eth.contract(address=cls.token_address, abi=mock_artifact["abi"])
        
        os.environ["ROBIN_MCP_TOKEN_ADDRESS"] = cls.token_address

        # Mint tokens to User 1 (100,000 tokens) and User 2 (100,000 tokens)
        mint_amt = 100000 * 10**18
        tx_mint1 = cls.token_contract.functions.mint(cls.account1.address, mint_amt).build_transaction({
            'from': cls.account1.address,
            'nonce': cls.w3.eth.get_transaction_count(cls.account1.address),
            'gas': 200000,
            'gasPrice': cls.w3.eth.gas_price
        })
        tx_mint2 = cls.token_contract.functions.mint(cls.account2.address, mint_amt).build_transaction({
            'from': cls.account1.address,
            'nonce': cls.w3.eth.get_transaction_count(cls.account1.address) + 1,
            'gas': 200000,
            'gasPrice': cls.w3.eth.gas_price
        })
        cls.w3.eth.send_raw_transaction(cls.w3.eth.account.sign_transaction(tx_mint1, cls.pk1).raw_transaction)
        cls.w3.eth.send_raw_transaction(cls.w3.eth.account.sign_transaction(tx_mint2, cls.pk1).raw_transaction)

        # 3. Deploy StakingYield contract
        with open("StakingYield.json", "r") as f:
            staking_artifact = json.load(f)
        StakingFactory = cls.w3.eth.contract(abi=staking_artifact["abi"], bytecode=staking_artifact["bytecode"])
        
        tx_stake = StakingFactory.constructor(cls.token_address).build_transaction({
            'from': cls.account1.address,
            'nonce': cls.w3.eth.get_transaction_count(cls.account1.address),
            'gas': 3000000,
            'gasPrice': cls.w3.eth.gas_price
        })
        signed_stake = cls.w3.eth.account.sign_transaction(tx_stake, cls.pk1)
        tx_hash_stake = cls.w3.eth.send_raw_transaction(signed_stake.raw_transaction)
        stake_receipt = cls.w3.eth.wait_for_transaction_receipt(tx_hash_stake)
        cls.staking_address = stake_receipt.contractAddress
        cls.staking_contract = cls.w3.eth.contract(address=cls.staking_address, abi=staking_artifact["abi"])
        os.environ["STAKING_YIELD_ADDRESS"] = cls.staking_address

        print(f"✅ Mock Token Deployed: {cls.token_address}")
        print(f"✅ StakingYield Deployed: {cls.staking_address}")

    @classmethod
    def teardown_class(cls):
        """Terminates the local Anvil node."""
        if cls.anvil_process:
            cls.anvil_process.terminate()
            cls.anvil_process.wait()

    @pytest.mark.asyncio
    async def test_01_initial_state(self):
        """Verifies initial parameters of the deployed StakingYield contract."""
        assert self.staking_contract.functions.totalStaked().call() == 0
        assert self.staking_contract.functions.rewardIndex().call() == 0
        assert self.staking_contract.functions.stakingToken().call() == self.token_address
        assert self.staking_contract.functions.stakedBalance(self.account1.address).call() == 0

    @pytest.mark.asyncio
    async def test_02_stake_tokens_user1(self):
        """Tests staking tokens for User 1."""
        stake_amount = 1000 * 10**18  # 1,000 ROBIN_MCP
        
        # Approve Staking contract
        tx_app = self.token_contract.functions.approve(self.staking_address, stake_amount).build_transaction({
            'from': self.account1.address,
            'nonce': self.w3.eth.get_transaction_count(self.account1.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_app, self.pk1).raw_transaction)

        # Stake
        tx_stake = self.staking_contract.functions.stake(stake_amount).build_transaction({
            'from': self.account1.address,
            'nonce': self.w3.eth.get_transaction_count(self.account1.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_stake, self.pk1).raw_transaction)

        assert self.staking_contract.functions.totalStaked().call() == stake_amount
        assert self.staking_contract.functions.stakedBalance(self.account1.address).call() == stake_amount
        assert self.staking_contract.functions.earned(self.account1.address).call() == 0

    @pytest.mark.asyncio
    async def test_03_stake_tokens_user2(self):
        """Tests staking tokens for User 2 (3,000 tokens, giving 75% pool share)."""
        stake_amount = 3000 * 10**18  # 3,000 ROBIN_MCP
        
        tx_app = self.token_contract.functions.approve(self.staking_address, stake_amount).build_transaction({
            'from': self.account2.address,
            'nonce': self.w3.eth.get_transaction_count(self.account2.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_app, self.pk2).raw_transaction)

        tx_stake = self.staking_contract.functions.stake(stake_amount).build_transaction({
            'from': self.account2.address,
            'nonce': self.w3.eth.get_transaction_count(self.account2.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_stake, self.pk2).raw_transaction)

        assert self.staking_contract.functions.totalStaked().call() == 4000 * 10**18
        assert self.staking_contract.functions.stakedBalance(self.account2.address).call() == 3000 * 10**18

    @pytest.mark.asyncio
    async def test_04_proportional_reward_distribution(self):
        """Tests proportional ETH reward distribution across multiple stakers."""
        # Deposit 4 ETH rewards into StakingYield
        reward_eth = Web3.to_wei(4, 'ether')
        
        tx_deposit = {
            'from': self.account1.address,
            'to': self.staking_address,
            'value': reward_eth,
            'nonce': self.w3.eth.get_transaction_count(self.account1.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        }
        self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_deposit, self.pk1).raw_transaction)

        # Check earned amounts
        # User 1 has 1,000 / 4,000 = 25% share -> should earn 1.0 ETH
        # User 2 has 3,000 / 4,000 = 75% share -> should earn 3.0 ETH
        earned1 = self.staking_contract.functions.earned(self.account1.address).call()
        earned2 = self.staking_contract.functions.earned(self.account2.address).call()

        assert earned1 == Web3.to_wei(1, 'ether'), f"User1 earned expected 1 ETH, got {Web3.from_wei(earned1, 'ether')}"
        assert earned2 == Web3.to_wei(3, 'ether'), f"User2 earned expected 3 ETH, got {Web3.from_wei(earned2, 'ether')}"

    @pytest.mark.asyncio
    async def test_05_claim_rewards(self):
        """Tests claiming accrued ETH rewards."""
        bal_before = self.w3.eth.get_balance(self.account1.address)

        tx_claim = self.staking_contract.functions.claimRewards().build_transaction({
            'from': self.account1.address,
            'nonce': self.w3.eth.get_transaction_count(self.account1.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        signed = self.w3.eth.account.sign_transaction(tx_claim, self.pk1)
        receipt = self.w3.eth.wait_for_transaction_receipt(self.w3.eth.send_raw_transaction(signed.raw_transaction))

        gas_spent = receipt.gasUsed * receipt.effectiveGasPrice
        bal_after = self.w3.eth.get_balance(self.account1.address)

        # Net balance increase should be 1.0 ETH - gas_spent
        expected_gain = Web3.to_wei(1, 'ether') - gas_spent
        assert bal_after - bal_before == expected_gain
        assert self.staking_contract.functions.earned(self.account1.address).call() == 0

        # User 2 earned should still remain 3.0 ETH unclaimed
        assert self.staking_contract.functions.earned(self.account2.address).call() == Web3.to_wei(3, 'ether')

    @pytest.mark.asyncio
    async def test_06_unstake_and_claim(self):
        """Tests unstaking a portion of staked tokens and verifying reward accrual continues."""
        # Unstake 1,000 tokens for User 2 (had 3,000 -> leaves 2,000)
        unstake_amt = 1000 * 10**18
        
        token_bal_before = self.token_contract.functions.balanceOf(self.account2.address).call()

        tx_unstake = self.staking_contract.functions.unstake(unstake_amt).build_transaction({
            'from': self.account2.address,
            'nonce': self.w3.eth.get_transaction_count(self.account2.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_unstake, self.pk2).raw_transaction)

        token_bal_after = self.token_contract.functions.balanceOf(self.account2.address).call()
        assert token_bal_after - token_bal_before == unstake_amt
        assert self.staking_contract.functions.stakedBalance(self.account2.address).call() == 2000 * 10**18
        assert self.staking_contract.functions.totalStaked().call() == 3000 * 10**18

        # Claim User 2 rewards (3 ETH)
        eth_bal_before = self.w3.eth.get_balance(self.account2.address)
        tx_claim = self.staking_contract.functions.claimRewards().build_transaction({
            'from': self.account2.address,
            'nonce': self.w3.eth.get_transaction_count(self.account2.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        receipt = self.w3.eth.wait_for_transaction_receipt(self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_claim, self.pk2).raw_transaction))
        gas_spent = receipt.gasUsed * receipt.effectiveGasPrice
        eth_bal_after = self.w3.eth.get_balance(self.account2.address)
        
        assert eth_bal_after - eth_bal_before == Web3.to_wei(3, 'ether') - gas_spent
        assert self.staking_contract.functions.earned(self.account2.address).call() == 0

    @pytest.mark.asyncio
    async def test_07_emergency_unstake(self):
        """Tests emergency unstake withdrawing full balance instantly."""
        # User 1 has 1,000 tokens staked
        token_bal_before = self.token_contract.functions.balanceOf(self.account1.address).call()
        staked_before = self.staking_contract.functions.stakedBalance(self.account1.address).call()
        assert staked_before == 1000 * 10**18

        tx_emerg = self.staking_contract.functions.emergencyUnstake().build_transaction({
            'from': self.account1.address,
            'nonce': self.w3.eth.get_transaction_count(self.account1.address),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        self.w3.eth.send_raw_transaction(self.w3.eth.account.sign_transaction(tx_emerg, self.pk1).raw_transaction)

        token_bal_after = self.token_contract.functions.balanceOf(self.account1.address).call()
        assert token_bal_after - token_bal_before == staked_before
        assert self.staking_contract.functions.stakedBalance(self.account1.address).call() == 0
        assert self.staking_contract.functions.totalStaked().call() == 2000 * 10**18

    @pytest.mark.asyncio
    async def test_08_error_conditions(self):
        """Tests require assertions and reverts for invalid inputs."""
        # 1. Cannot stake 0
        with pytest.raises(Exception):
            self.staking_contract.functions.stake(0).call({'from': self.account1.address})

        # 2. Cannot unstake 0 or more than staked
        with pytest.raises(Exception):
            self.staking_contract.functions.unstake(0).call({'from': self.account1.address})
            
        with pytest.raises(Exception):
            self.staking_contract.functions.unstake(100).call({'from': self.account1.address})

        # 3. Emergency unstake with 0 staked balance fails
        with pytest.raises(Exception):
            self.staking_contract.functions.emergencyUnstake().call({'from': self.account1.address})

        # 4. Claim reward with 0 rewards fails
        with pytest.raises(Exception):
            self.staking_contract.functions.claimRewards().call({'from': self.account1.address})

    @pytest.mark.asyncio
    async def test_09_web3_helper_methods(self):
        """Tests Web3Helper Python wrapper methods for staking operations."""
        # Query staking info via helper
        info = await self.helper.get_staking_info(
            staking_contract_address=self.staking_address,
            user_address=self.account2.address
        )
        assert info["staking_contract"] == self.staking_address
        assert info["total_staked"] == 2000.0
        assert info["user_staked"] == 2000.0
        assert info["pool_share_percent"] == 100.0
        assert info["token_symbol"] == "ROBIN_MCP"

        # Stake 500 tokens using helper from account 1
        # First ensure helper is configured with account 1 key
        os.environ["ROBINHOOD_CHAIN_PRIVATE_KEY"] = self.pk1
        receipt_stake = await self.helper.stake_tokens(500, self.staking_address)
        assert receipt_stake["status"] == "SUCCESS"

        info_after = await self.helper.get_staking_info(self.staking_address, self.account1.address)
        assert info_after["user_staked"] == 500.0
        assert info_after["total_staked"] == 2500.0

        # Unstake 200 tokens
        receipt_unstake = await self.helper.unstake_tokens(200, self.staking_address)
        assert receipt_unstake["status"] == "SUCCESS"
        info_un = await self.helper.get_staking_info(self.staking_address, self.account1.address)
        assert info_un["user_staked"] == 300.0

        # Deposit reward ETH via helper
        receipt_dep = await self.helper.deposit_staking_reward(0.5, self.staking_address)
        assert receipt_dep["status"] == "SUCCESS"

        # Claim rewards via helper
        receipt_claim = await self.helper.claim_rewards(self.staking_address)
        assert receipt_claim["status"] == "SUCCESS"

    @pytest.mark.asyncio
    async def test_10_mcp_server_dispatch_tools(self):
        """Tests MCP tool dispatcher execution for all staking tools."""
        # 1. get_staking_info tool
        info_json = await dispatch_tool("get_staking_info", {
            "staking_contract_address": self.staking_address,
            "user_address": self.account1.address
        })
        info_data = json.loads(info_json)
        assert "user_staked" in info_data
        assert "total_staked" in info_data
        assert "pool_share_percent" in info_data

        # 2. stake_tokens tool
        stake_res = await dispatch_tool("stake_tokens", {
            "amount": 100,
            "staking_contract_address": self.staking_address
        })
        assert "Tokens staked successfully!" in stake_res

        # 3. unstake_tokens tool
        unstake_res = await dispatch_tool("unstake_tokens", {
            "amount": 50,
            "staking_contract_address": self.staking_address
        })
        assert "Tokens unstaked successfully!" in unstake_res

        # 4. deposit_staking_reward tool
        dep_res = await dispatch_tool("deposit_staking_reward", {
            "eth_amount": 0.05,
            "staking_contract_address": self.staking_address
        })
        assert "Staking reward ETH deposited successfully!" in dep_res

        # 5. claim_rewards tool
        claim_res = await dispatch_tool("claim_rewards", {
            "staking_contract_address": self.staking_address
        })
        assert "Rewards claimed successfully!" in claim_res

        # 6. emergency_unstake tool
        emerg_res = await dispatch_tool("emergency_unstake", {
            "staking_contract_address": self.staking_address
        })
        assert "Emergency unstake executed successfully!" in emerg_res
