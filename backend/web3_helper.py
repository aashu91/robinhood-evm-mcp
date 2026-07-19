from web3 import Web3
import json

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider('YOUR_INFURA_OR_ALCHEMY_URL'))

# Load the ABI and contract address
with open('CommunityTrust.json', 'r') as file:
    abi = json.load(file)

contract_address = 'YOUR_CONTRACT_ADDRESS'
contract = w3.eth.contract(address=contract_address, abi=abi)

def get_latest_gold_price():
    return contract.functions.getLatestGoldPrice().call()

def get_latest_silver_price():
    return contract.functions.getLatestSilverPrice().call()

def calculate_usd_valuation(gold_amount, silver_amount):
    gold_price = get_latest_gold_price()
    silver_price = get_latest_silver_price()
    gold_value = gold_amount * gold_price / 1e8  # Convert from 8 decimals
    silver_value = silver_amount * silver_price / 1e8  # Convert from 8 decimals
    total_value = gold_value + silver_value
    return total_value

# Example usage
gold_amount = 10  # in grams
silver_amount = 50  # in grams
usd_valuation = calculate_usd_valuation(gold_amount, silver_amount)
print(f"Current USD valuation: {usd_valuation} USD")