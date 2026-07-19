import pytest
from web3 import Web3
from web3_helper import get_gold_price, get_silver_price

@pytest.fixture
def w3():
    return Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'))

def test_gold_price(w3):
    price = get_gold_price()
    assert price > 0, "Gold price should be greater than 0"

def test_silver_price(w3):
    price = get_silver_price()
    assert price > 0, "Silver price should be greater than 0"