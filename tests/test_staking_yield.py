import pytest
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3_helper import *

@pytest.fixture
def w3():
    w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

@pytest.fixture
def contract(w3):
    abi_file = 'StakingYield.abi.json'
    abi = load_contract_abi(abi_file)
    contract_address = '0xYourContractAddress'
    return w3.eth.contract(address=contract_address, abi=abi)

@pytest.fixture
def account():
    return '0xYourAccountAddress'

@pytest.fixture
def private_key():
    return 'YourPrivateKey'

def test_stake(contract, account, private_key):
    receipt = stake_tokens(contract, 100, account)
    assert receipt.status == 1

def test_unstake(contract, account, private_key):
    receipt = unstake_tokens(contract, 50, account)
    assert receipt.status == 1

def test_claim_rewards(contract, account, private_key):
    receipt = claim_rewards(contract, account)
    assert receipt.status == 1

def test_get_staking_info(contract, account):
    staking_info = get_staking_info(contract, account)
    assert staking_info[0] > 0
    assert staking_info[1] >= 0
    assert staking_info[2] > 0
