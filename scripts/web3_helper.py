from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

def load_contract_abi(contract_file):
    with open(contract_file) as f:
        abi = json.load(f)
    return abi

def get_contract_instance(contract_address, abi):
    return w3.eth.contract(address=contract_address, abi=abi)

def stake_tokens(contract, amount, account):
    tx = contract.functions.stake(amount).buildTransaction({
        'from': account,
        'gas': 2000000,
        'nonce': w3.eth.getTransactionCount(account),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

def unstake_tokens(contract, amount, account):
    tx = contract.functions.unstake(amount).buildTransaction({
        'from': account,
        'gas': 2000000,
        'nonce': w3.eth.getTransactionCount(account),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

def claim_rewards(contract, account):
    tx = contract.functions.claimRewards().buildTransaction({
        'from': account,
        'gas': 2000000,
        'nonce': w3.eth.getTransactionCount(account),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

def get_staking_info(contract, account):
    return contract.functions.getStakingInfo(account).call()
