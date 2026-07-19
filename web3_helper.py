from web3 import Web3
import json

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))

# Load the ABI and contract address
with open('CommunityTrust.abi', 'r') as file:
    abi = json.load(file)

contract_address = 'YOUR_CONTRACT_ADDRESS'
contract = w3.eth.contract(address=contract_address, abi=abi)

def get_gold_price():
    return contract.functions.getGoldPrice().call()

def get_silver_price():
    return contract.functions.getSilverPrice().call()

def calculate_usd_valuation(gold_amount, silver_amount):
    gold_price = get_gold_price()
    silver_price = get_silver_price()
    gold_value = gold_amount * gold_price / 1e8  # Chainlink prices are in 8 decimals
    silver_value = silver_amount * silver_price / 1e8
    return gold_value + silver_value

# Example usage
gold_amount = 100  # in grams
silver_amount = 500  # in grams
usd_valuation = calculate_usd_valuation(gold_amount, silver_amount)
print(f"USD Valuation: {usd_valuation}")