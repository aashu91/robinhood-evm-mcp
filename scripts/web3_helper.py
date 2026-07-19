from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load the ABI and contract address
with open('StakingYield.abi', 'r') as file:
    abi = json.load(file)
contract_address = '0xYourContractAddress'
staking_contract = w3.eth.contract(address=contract_address, abi=abi)

def stake_tokens(account, amount):
    tx = staking_contract.functions.stake(amount).buildTransaction({
        'from': account,
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key='your_private_key')
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def unstake_tokens(account, amount):
    tx = staking_contract.functions.unstake(amount).buildTransaction({
        'from': account,
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key='your_private_key')
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def claim_rewards(account):
    tx = staking_contract.functions.claimRewards().buildTransaction({
        'from': account,
        'gas': 2000000,
        'gasPrice': w3.toWei('50', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key='your_private_key')
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def get_staking_info(account):
    staked_amount, pending_rewards, total_staked = staking_contract.functions.getStakingInfo(account).call()
    return staked_amount, pending_rewards, total_staked
