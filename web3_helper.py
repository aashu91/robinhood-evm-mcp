# web3_helper.py
# Core Web3 wrapper for EVM interactions, querying, signing, and network routing

import os
import sys
import time
import asyncio
from web3 import Web3
from eth_account import Account
from constants import NETWORKS, DEFAULT_NETWORK, TICKER_MAPPINGS, PREPACKAGED_ABIS
from abi_manager import get_abi

# Load .env file manually to support zero-dependency environments
def load_env():
    env_path = os.path.expanduser("~/.env")
    if os.path.exists(".env"):
        env_path = ".env"
    
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env()

class Web3Helper:
    def __init__(self):
        self.active_network_name = DEFAULT_NETWORK
        self.network_config = NETWORKS[self.active_network_name]
        self.w3 = None
        self.connect()

    def connect(self):
        """Establish connection to the active RPC endpoint."""
        rpc_url = os.getenv("ROBINHOOD_CHAIN_RPC_URL", self.network_config["rpc_url"])
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Add Arbitrum L2 middleware if necessary (e.g., extra fee market fields)
        # Note: Arbitrum Orbit is standard EVM compatible, standard HTTP provider works out-of-the-box.
        return self.w3.is_connected()

    def switch_network(self, network_name):
        """Switches the active network dynamically."""
        if network_name not in NETWORKS:
            raise ValueError(f"Network '{network_name}' not configured. Available: {list(NETWORKS.keys())}")
        
        self.active_network_name = network_name
        self.network_config = NETWORKS[network_name]
        return self.connect()

    def get_private_key(self):
        """Safely fetches private key from environment variables."""
        # Try different names for maximum usability
        key = os.getenv("ROBINHOOD_CHAIN_PRIVATE_KEY") or os.getenv("EVM_PRIVATE_KEY") or os.getenv("PRIVATE_KEY")
        if not key:
            raise ValueError("No private key found. Set ROBINHOOD_CHAIN_PRIVATE_KEY in your env.")
        if key.startswith("0x"):
            key = key[2:]
        return key

    def get_account(self):
        """Constructs an Account object from the loaded private key."""
        pk = self.get_private_key()
        return Account.from_key(pk)

    async def get_balance(self, address, token_address=None):
        """Reads ETH or ERC-20 token balance for an address."""
        if not self.w3.is_connected():
            self.connect()
            
        address = Web3.to_checksum_address(address)
        
        # Native ETH balance
        if not token_address:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = Web3.from_wei(balance_wei, 'ether')
            return {
                "symbol": "ETH",
                "balance": float(balance_eth),
                "decimals": 18
            }
            
        # ERC-20 balance
        token_address = Web3.to_checksum_address(token_address)
        abi = PREPACKAGED_ABIS["ERC20"]
        contract = self.w3.eth.contract(address=token_address, abi=abi)
        
        try:
            balance_raw = contract.functions.balanceOf(address).call()
            decimals = contract.functions.decimals().call()
            symbol = contract.functions.symbol().call()
            balance_formatted = balance_raw / (10 ** decimals)
            return {
                "symbol": symbol,
                "balance": balance_formatted,
                "decimals": decimals
            }
        except Exception as e:
            # Fallback in case of ABI failure
            return {
                "symbol": "UNKNOWN",
                "balance": 0.0,
                "error": f"Failed to fetch ERC20 properties: {str(e)}"
            }

    async def query_contract(self, contract_address, function_name, args=None, abi_type=None):
        """Performs a read-only query on a smart contract."""
        if not self.w3.is_connected():
            self.connect()
            
        contract_address = Web3.to_checksum_address(contract_address)
        args = args or []
        
        # Retrieve ABI
        abi = None
        if abi_type and abi_type in PREPACKAGED_ABIS:
            abi = PREPACKAGED_ABIS[abi_type]
        else:
            # Check SQLite custom ABI cache
            stored_abi, _ = await get_abi(contract_address)
            if stored_abi:
                abi = stored_abi
            else:
                # Default to ERC-20 as generic fallback
                abi = PREPACKAGED_ABIS["ERC20"]

        contract = self.w3.eth.contract(address=contract_address, abi=abi)
        func = getattr(contract.functions, function_name)
        result = func(*args).call()
        return result

    async def estimate_and_build_tx(self, contract_address, function_name, args=None, abi_type=None, value_wei=0):
        """Estimates gas and builds the raw transaction transaction dict."""
        if not self.w3.is_connected():
            self.connect()
            
        contract_address = Web3.to_checksum_address(contract_address)
        args = args or []
        
        # Load signer details
        account = self.get_account()
        
        # Fetch ABI
        abi = None
        if abi_type and abi_type in PREPACKAGED_ABIS:
            abi = PREPACKAGED_ABIS[abi_type]
        else:
            stored_abi, _ = await get_abi(contract_address)
            if stored_abi:
                abi = stored_abi
            else:
                abi = PREPACKAGED_ABIS["ERC20"]
                
        contract = self.w3.eth.contract(address=contract_address, abi=abi)
        func = getattr(contract.functions, function_name)
        
        # Transaction structure
        tx_params = {
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gasPrice': int(self.w3.eth.gas_price * 1.1), # Add slight safety margin
            'value': value_wei,
            'chainId': self.network_config["chain_id"]
        }
        
        # Estimate gas
        gas_estimate = func(*args).estimate_gas(tx_params)
        tx_params['gas'] = int(gas_estimate * 1.2) # Add safety margin
        
        # Build transaction
        transaction = func(*args).build_transaction(tx_params)
        return transaction

    async def sign_and_send_transaction(self, tx):
        """Signs and broadcasts a pre-built transaction to the RPC."""
        account = self.get_account()
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return Web3.to_hex(tx_hash)

    async def wait_for_confirmation(self, tx_hash, timeout=60, poll_interval=2):
        """Polls for transaction receipt to verify execution state."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    status = receipt.get("status")
                    return {
                        "tx_hash": tx_hash,
                        "status": "SUCCESS" if status == 1 else "FAILED",
                        "blockNumber": receipt.get("blockNumber"),
                        "gasUsed": receipt.get("gasUsed"),
                        "logs": len(receipt.get("logs", []))
                    }
            except Exception:
                pass
            await asyncio.sleep(poll_interval)
            
        return {
            "tx_hash": tx_hash,
            "status": "TIMEOUT",
            "message": f"Transaction not mined within {timeout} seconds."
        }

    async def get_cross_chain_quote(self, src_chain_id, src_token, dest_chain_id, dest_token, amount_raw, recipient, sender=None):
        """Fetches cross-chain swap routing and transaction details using deBridge DLN API."""
        import requests
        
        # Resolve native tickers
        if src_token.upper() == "SOL":
            src_token = "11111111111111111111111111111111"
        elif src_token.upper() == "ETH":
            src_token = "0x0000000000000000000000000000000000000000"
            
        if dest_token.upper() == "ETH":
            dest_token = "0x0000000000000000000000000000000000000000"
            
        sender = sender or recipient
        
        url = "https://dln.debridge.finance/v1.0/dln/order/create-tx"
        params = {
            "srcChainId": int(src_chain_id),
            "srcChainTokenIn": src_token,
            "srcChainTokenInAmount": str(amount_raw),
            "dstChainId": int(dest_chain_id),
            "dstChainTokenOut": dest_token,
            "dstChainTokenOutAmount": "auto",
            "dstChainTokenOutRecipient": recipient,
            "srcChainOrderAuthorityAddress": sender,
            "dstChainOrderAuthorityAddress": recipient
        }
        
        loop = asyncio.get_event_loop()
        def fetch():
            res = requests.get(url, params=params, headers={"accept": "application/json"})
            res.raise_for_status()
            return res.json()
            
        result = await loop.run_in_executor(None, fetch)
        return result

