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
        
        if self.w3.is_connected():
            try:
                # Dynamically match chain ID to prevent signature mismatches
                self.network_config = self.network_config.copy()
                self.network_config["chain_id"] = self.w3.eth.chain_id
            except Exception:
                pass
        
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

    async def load_abi_helper(self, contract_address, abi_type=None):
        """Helper to resolve ABI from constants, local JSON files, or DB cache."""
        import json
        if abi_type and abi_type in PREPACKAGED_ABIS:
            return PREPACKAGED_ABIS[abi_type]
            
        if abi_type:
            # Check if there is a local compiled JSON file
            local_paths = [
                os.path.join(os.path.dirname(__file__), f"{abi_type}.json"),
                os.path.join(os.path.dirname(__file__), "contracts", f"{abi_type}.json")
            ]
            for path in local_paths:
                if os.path.exists(path):
                    try:
                        with open(path, "r") as f:
                            data = json.load(f)
                            if "abi" in data:
                                return data["abi"]
                    except Exception:
                        pass
                        
        if contract_address:
            stored_abi, _ = await get_abi(contract_address)
            if stored_abi:
                return stored_abi
                
        return PREPACKAGED_ABIS["ERC20"]

    async def query_contract(self, contract_address, function_name, args=None, abi_type=None):
        """Performs a read-only query on a smart contract."""
        if not self.w3.is_connected():
            self.connect()
            
        contract_address = Web3.to_checksum_address(contract_address)
        args = args or []
        
        abi = await self.load_abi_helper(contract_address, abi_type)
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
        
        abi = await self.load_abi_helper(contract_address, abi_type)
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
        raw_tx = getattr(signed_tx, "raw_transaction", None) or getattr(signed_tx, "rawTransaction")
        tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
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
        
        # Inject affiliate fees if configured in environment
        fee_recipient = os.getenv("AFFILIATE_FEE_RECIPIENT")
        fee_percent = os.getenv("AFFILIATE_FEE_PERCENT", "0.1") # e.g. 0.1 for 0.1%
        if fee_recipient:
            params["affiliateFeePercent"] = fee_percent
            params["affiliateFeeRecipient"] = fee_recipient
        
        loop = asyncio.get_event_loop()
        def fetch():
            res = requests.get(url, params=params, headers={"accept": "application/json"})
            res.raise_for_status()
            return res.json()
            
        result = await loop.run_in_executor(None, fetch)
        return result

    async def deploy_meme_token(self, name, symbol, supply, value_wei=None):
        """Builds, signs, and executes the transaction to deploy a new meme token through the factory."""
        factory_address = os.getenv("MEME_FACTORY_ADDRESS")
        if not factory_address:
            raise ValueError("MEME_FACTORY_ADDRESS is not set in your .env configuration.")
            
        if value_wei is None:
            value_wei = Web3.to_wei(0.005, 'ether')
                
        # Supply formatting: raw decimals (18)
        supply_raw = int(supply) * (10**18)
        
        args = [name, symbol, supply_raw]
        tx = await self.estimate_and_build_tx(
            contract_address=factory_address,
            function_name="deployMemeToken",
            args=args,
            abi_type="MemeFactory",
            value_wei=value_wei
        )
        
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def get_meme_pool_reserves(self, token_address):
        """Queries the pools mapping in MemeFactory for a given meme token reserves."""
        factory_address = os.getenv("MEME_FACTORY_ADDRESS")
        if not factory_address:
            raise ValueError("MEME_FACTORY_ADDRESS is not set in your .env configuration.")
        
        token_address = Web3.to_checksum_address(token_address)
        # Query pools(tokenAddress)
        # Returns: (address tokenAddress, uint256 tokenReserves, uint256 ethReserves, bool tradingActive)
        res = await self.query_contract(factory_address, "pools", [token_address], "MemeFactory")
        return {
            "token_address": res[0],
            "token_reserves": res[1],
            "eth_reserves": res[2],
            "trading_active": res[3]
        }

    async def estimate_meme_trade_output(self, token_address, trade_type, amount):
        """Estimates output amount (in tokens or ETH) based on virtual bonding curve."""
        reserves = await self.get_meme_pool_reserves(token_address)
        token_reserves = reserves["token_reserves"]
        eth_reserves = reserves["eth_reserves"]
        
        if not reserves["trading_active"]:
            return {
                "error": "Trading is not active for this meme token.",
                "trading_active": False,
                "input_amount": float(amount),
                "estimated_output": 0.0,
                "price_impact_percent": 0.0
            }
            
        trade_type = trade_type.lower()
        if trade_type == "buy":
            # amount is in ETH
            eth_input_wei = Web3.to_wei(amount, 'ether')
            k = token_reserves * eth_reserves
            new_eth_reserves = eth_reserves + eth_input_wei
            new_token_reserves = k // new_eth_reserves
            tokens_out_raw = token_reserves - new_token_reserves
            
            return {
                "input_amount": float(amount),
                "input_symbol": "ETH",
                "estimated_output": tokens_out_raw / (10**18),
                "estimated_output_raw": tokens_out_raw,
                "output_symbol": "TOKEN",
                "price_impact_percent": ((eth_input_wei / eth_reserves) * 100)
            }
        elif trade_type == "sell":
            # amount is in tokens
            token_input_raw = int(float(amount) * (10**18))
            k = token_reserves * eth_reserves
            new_token_reserves = token_reserves + token_input_raw
            new_eth_reserves = k // new_token_reserves
            eth_out_wei = eth_reserves - new_eth_reserves
            
            return {
                "input_amount": float(amount),
                "input_symbol": "TOKEN",
                "estimated_output": float(Web3.from_wei(eth_out_wei, 'ether')),
                "estimated_output_raw": eth_out_wei,
                "output_symbol": "ETH",
                "price_impact_percent": ((token_input_raw / token_reserves) * 100)
            }
        else:
            raise ValueError(f"Invalid trade_type '{trade_type}'. Must be 'buy' or 'sell'.")

    async def buy_meme_token(self, token_address, eth_amount, max_slippage=0.01, min_output_amount=None):
        """Buys meme tokens by sending ETH to the buyMemeToken method on the factory with slippage protection."""
        factory_address = os.getenv("MEME_FACTORY_ADDRESS")
        if not factory_address:
            raise ValueError("MEME_FACTORY_ADDRESS is not set in your .env configuration.")
            
        token_address = Web3.to_checksum_address(token_address)
        value_wei = Web3.to_wei(eth_amount, 'ether')
        
        # Pre-flight slippage check
        estimate = await self.estimate_meme_trade_output(token_address, "buy", eth_amount)
        if min_output_amount is not None:
            if estimate["estimated_output"] < float(min_output_amount):
                raise ValueError(f"Slippage limit exceeded: estimated {estimate['estimated_output']} < minimum {min_output_amount}")
        
        args = [token_address]
        tx = await self.estimate_and_build_tx(
            contract_address=factory_address,
            function_name="buyMemeToken",
            args=args,
            abi_type="MemeFactory",
            value_wei=value_wei
        )
        
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def sell_meme_token(self, token_address, token_amount, max_slippage=0.01, min_output_amount=None):
        """Sells meme tokens by calling the sellMemeToken method on the factory with slippage protection."""
        factory_address = os.getenv("MEME_FACTORY_ADDRESS")
        if not factory_address:
            raise ValueError("MEME_FACTORY_ADDRESS is not set in your .env configuration.")
            
        token_address = Web3.to_checksum_address(token_address)
        
        # Pre-flight slippage check
        estimate = await self.estimate_meme_trade_output(token_address, "sell", token_amount)
        if min_output_amount is not None:
            if estimate["estimated_output"] < float(min_output_amount):
                raise ValueError(f"Slippage limit exceeded: estimated {estimate['estimated_output']} < minimum {min_output_amount}")
        
        # Format token input with 18 decimals
        token_amount_raw = int(float(token_amount) * (10**18))
        
        args = [token_address, token_amount_raw]
        tx = await self.estimate_and_build_tx(
            contract_address=factory_address,
            function_name="sellMemeToken",
            args=args,
            abi_type="MemeFactory",
            value_wei=0
        )
        
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def scan_factory_tokens(self, force_refresh=False):
        """Queries the MemeFactory contract to discover all launched tokens and registers them."""
        factory_address = os.getenv("MEME_FACTORY_ADDRESS")
        if not factory_address:
            raise ValueError("MEME_FACTORY_ADDRESS is not set in your .env configuration.")
        
        factory_address = Web3.to_checksum_address(factory_address)
        
        # Check if we already have tokens registered and not force_refresh
        from abi_manager import get_registered_tokens, register_token
        if not force_refresh:
            existing = await get_registered_tokens()
            # If we have scanned tokens, return them
            scanned = [t for t in existing if t["is_scanned"] == 1]
            if scanned:
                return scanned

        # Call getMemeCount on the factory
        try:
            count = await self.query_contract(factory_address, "getMemeCount", [], "MemeFactory")
        except Exception:
            count = 0
            
        scanned_tokens = []
        for i in range(count):
            try:
                token_addr = await self.query_contract(factory_address, "allMemeTokens", [i], "MemeFactory")
                token_addr = Web3.to_checksum_address(token_addr)
                
                # Fetch token symbol and name
                symbol = await self.query_contract(token_addr, "symbol", [], "ERC20")
                name = await self.query_contract(token_addr, "name", [], "ERC20")
                decimals = await self.query_contract(token_addr, "decimals", [], "ERC20")
                
                # Register in SQLite database
                await register_token(symbol, token_addr, name, decimals, is_scanned=1)
                scanned_tokens.append({
                    "ticker": symbol,
                    "address": token_addr,
                    "name": name,
                    "decimals": decimals,
                    "is_scanned": 1
                })
            except Exception:
                pass
                
        return scanned_tokens

    async def import_custom_token(self, ticker, address, name=None, decimals=18):
        """Manually registers a custom token mapping in the local database."""
        from abi_manager import register_token
        address = Web3.to_checksum_address(address)
        ticker = ticker.upper()
        
        # Try to verify decimals and name on-chain if not provided
        if not name:
            try:
                name = await self.query_contract(address, "name", [], "ERC20")
            except Exception:
                name = ticker
        if decimals == 18:
            try:
                decimals = await self.query_contract(address, "decimals", [], "ERC20")
            except Exception:
                decimals = 18
                
        await register_token(ticker, address, name, decimals, is_scanned=0)
        return {
            "ticker": ticker,
            "address": address,
            "name": name,
            "decimals": decimals,
            "is_scanned": 0
        }

    async def execute_cross_chain_bridge(self, src_chain_id, src_token, dest_chain_id, dest_token, amount_raw, recipient):
        """Fetches DLN bridging calldata and signs/broadcasts the bridging transaction on the source EVM chain."""
        # 1. Fetch DLN quote and calldata
        quote = await self.get_cross_chain_quote(src_chain_id, src_token, dest_chain_id, dest_token, amount_raw, recipient)
        
        tx_data = quote.get("tx")
        if not tx_data:
            raise ValueError(f"deBridge DLN API did not return transaction calldata: {quote}")
            
        bridge_to = Web3.to_checksum_address(tx_data["to"])
        bridge_calldata = tx_data["data"]
        bridge_value = int(tx_data["value"])
        
        # 2. Connect to source chain RPC
        chain_rpcs = {
            8453: "https://mainnet.base.org",
            42161: "https://arb1.arbitrum.io/rpc",
            10: "https://mainnet.optimism.io",
            1: "https://cloudflare-eth.com"
        }
        
        rpc_url = chain_rpcs.get(int(src_chain_id))
        if not rpc_url:
            raise ValueError(f"Source chain ID {src_chain_id} is not supported or needs a configured RPC.")
            
        src_w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not src_w3.is_connected():
            raise ValueError(f"Failed to connect to source chain RPC: {rpc_url}")
            
        # 3. Load account
        account = self.get_account()
        
        # 4. Check approvals if source token is ERC-20
        is_native = (src_token == "0x0000000000000000000000000000000000000000" or src_token.upper() == "ETH")
        if not is_native:
            src_token_checksum = src_w3.to_checksum_address(src_token)
            abi = PREPACKAGED_ABIS["ERC20"]
            token_contract = src_w3.eth.contract(address=src_token_checksum, abi=abi)
            
            # Check allowance
            allowance = token_contract.functions.allowance(account.address, bridge_to).call()
            amount_to_spend = int(amount_raw)
            if allowance < amount_to_spend:
                # Approve router
                approve_tx = token_contract.functions.approve(bridge_to, amount_to_spend).build_transaction({
                    'from': account.address,
                    'nonce': src_w3.eth.get_transaction_count(account.address),
                    'gasPrice': int(src_w3.eth.gas_price * 1.1),
                    'chainId': int(src_chain_id)
                })
                signed_approve = src_w3.eth.account.sign_transaction(approve_tx, private_key=account.key)
                raw_approve = getattr(signed_approve, "raw_transaction", None) or getattr(signed_approve, "rawTransaction")
                app_hash = src_w3.eth.send_raw_transaction(raw_approve)
                # Wait briefly
                await asyncio.sleep(5)
                
        # 5. Build, sign and broadcast the bridge transaction
        bridge_tx = {
            'from': account.address,
            'to': bridge_to,
            'data': bridge_calldata,
            'value': bridge_value,
            'nonce': src_w3.eth.get_transaction_count(account.address),
            'gasPrice': int(src_w3.eth.gas_price * 1.1),
            'chainId': int(src_chain_id)
        }
        
        try:
            gas_estimate = src_w3.eth.estimate_gas(bridge_tx)
            bridge_tx['gas'] = int(gas_estimate * 1.2)
        except Exception as e:
            return {
                "error": f"Gas estimation or pre-flight check failed: {str(e)}",
                "message": "Verify that your account has enough funds (gas + transfer amount) on the source chain.",
                "source_chain_id": src_chain_id,
                "router_address": bridge_to,
                "value_sent": bridge_value,
                "tx_preview": {
                    "from": account.address,
                    "to": bridge_to,
                    "value": bridge_value,
                    "data_preview": bridge_calldata[:66] + "..."
                }
            }
        
        signed_bridge = src_w3.eth.account.sign_transaction(bridge_tx, private_key=account.key)
        raw_bridge = getattr(signed_bridge, "raw_transaction", None) or getattr(signed_bridge, "rawTransaction")
        tx_hash = src_w3.eth.send_raw_transaction(raw_bridge)
        
        return {
            "source_chain_id": src_chain_id,
            "bridge_tx_hash": src_w3.to_hex(tx_hash),
            "router_address": bridge_to,
            "value_sent": bridge_value
        }

    async def get_meme_price_history(self, token_address, block_range=10000):
        """Queries historical events for a meme token and returns a price history chart dataset."""
        factory_address = os.getenv("MEME_FACTORY_ADDRESS")
        if not factory_address:
            raise ValueError("MEME_FACTORY_ADDRESS is not set in your .env configuration.")
            
        factory_address = Web3.to_checksum_address(factory_address)
        token_address = Web3.to_checksum_address(token_address)
        
        if not self.w3.is_connected():
            self.connect()
            
        token_bought_signature = self.w3.keccak(text="TokenBought(address,address,uint256,uint256)").hex()
        token_sold_signature = self.w3.keccak(text="TokenSold(address,address,uint256,uint256)").hex()
        
        token_topic = "0x" + token_address[2:].lower().zfill(64)
        latest_block = self.w3.eth.block_number
        from_block = max(0, latest_block - block_range)
        
        price_points = []
        
        # TokenBought Logs
        try:
            bought_logs = self.w3.eth.get_logs({
                "fromBlock": from_block,
                "toBlock": "latest",
                "address": factory_address,
                "topics": [token_bought_signature, token_topic]
            })
            for log in bought_logs:
                data = log["data"].hex() if isinstance(log["data"], bytes) else log["data"]
                if data.startswith("0x"):
                    data = data[2:]
                eth_amount = int(data[0:64], 16)
                token_amount = int(data[64:128], 16)
                
                eth_val = float(Web3.from_wei(eth_amount, 'ether'))
                token_val = token_amount / 10**18
                price = eth_val / token_val if token_val > 0 else 0
                
                price_points.append({
                    "block": log["blockNumber"],
                    "type": "buy",
                    "price": price,
                    "eth_volume": eth_val,
                    "token_volume": token_val,
                    "transaction_hash": log["transactionHash"].hex() if isinstance(log["transactionHash"], bytes) else log["transactionHash"]
                })
        except Exception:
            pass
            
        # TokenSold Logs
        try:
            sold_logs = self.w3.eth.get_logs({
                "fromBlock": from_block,
                "toBlock": "latest",
                "address": factory_address,
                "topics": [token_sold_signature, token_topic]
            })
            for log in sold_logs:
                data = log["data"].hex() if isinstance(log["data"], bytes) else log["data"]
                if data.startswith("0x"):
                    data = data[2:]
                token_amount = int(data[0:64], 16)
                eth_amount = int(data[64:128], 16)
                
                eth_val = float(Web3.from_wei(eth_amount, 'ether'))
                token_val = token_amount / 10**18
                price = eth_val / token_val if token_val > 0 else 0
                
                price_points.append({
                    "block": log["blockNumber"],
                    "type": "sell",
                    "price": price,
                    "eth_volume": eth_val,
                    "token_volume": token_val,
                    "transaction_hash": log["transactionHash"].hex() if isinstance(log["transactionHash"], bytes) else log["transactionHash"]
                })
        except Exception:
            pass
            
        price_points.sort(key=lambda x: x["block"])
        
        # Current Reserves
        try:
            reserves = await self.get_meme_pool_reserves(token_address)
            t_res = reserves["token_reserves"] / 10**18
            e_res = float(Web3.from_wei(reserves["eth_reserves"], 'ether'))
            current_price = e_res / t_res if t_res > 0 else 0
            price_points.append({
                "block": latest_block,
                "type": "current_reserves",
                "price": current_price,
                "token_reserves": t_res,
                "eth_reserves": e_res
            })
        except Exception:
            pass
            
        return price_points

    async def deploy_community_trust_factory(self):
        """Deploys a new CommunityTrustFactory contract."""
        import json
        json_path = os.path.join(os.path.dirname(__file__), "CommunityTrustFactory.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError("CommunityTrustFactory.json not found. Run compileTrust.cjs first.")
        
        with open(json_path, "r") as f:
            artifact = json.load(f)
            
        abi = artifact["abi"]
        bytecode = artifact["bytecode"]
        
        ContractFactory = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        account = self.get_account()
        
        nonce = self.w3.eth.get_transaction_count(account.address)
        gas_price = int(self.w3.eth.gas_price * 1.1)
        
        construct_tx = ContractFactory.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 3000000,
            'chainId': self.network_config["chain_id"]
        })
        
        tx_hash = await self.sign_and_send_transaction(construct_tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        
        if receipt.get("status") == "SUCCESS":
            raw_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            contract_address = raw_receipt.contractAddress
            os.environ["COMMUNITY_TRUST_FACTORY_ADDRESS"] = contract_address
            
            env_file_path = ".env" if os.path.exists(".env") else os.path.expanduser("~/.env")
            if os.path.exists(env_file_path):
                with open(env_file_path, "r") as f:
                    lines = f.readlines()
                new_lines = [l for l in lines if not l.strip().startswith("COMMUNITY_TRUST_FACTORY_ADDRESS=")]
                new_lines.append(f"\nCOMMUNITY_TRUST_FACTORY_ADDRESS={contract_address}\n")
                with open(env_file_path, "w") as f:
                    f.writelines(new_lines)
            return {
                "status": "SUCCESS",
                "contract_address": contract_address,
                "tx_hash": tx_hash
            }
        return {
            "status": "FAILED",
            "tx_hash": tx_hash
        }

    async def deploy_community_trust(self, factory_address, name, directors, required_signatures):
        """Deploys a new CommunityTrust contract through the factory."""
        directors = [self.w3.to_checksum_address(d) for d in directors]
        factory_address = self.w3.to_checksum_address(factory_address)
        
        tx = await self.estimate_and_build_tx(
            contract_address=factory_address,
            function_name="createTrust",
            args=[name, directors, int(required_signatures)],
            abi_type="CommunityTrustFactory",
            value_wei=0
        )
        
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        
        if receipt.get("status") == "SUCCESS":
            trusts_count = await self.query_contract(factory_address, "getTrustCount", [], "CommunityTrustFactory")
            trust_address = await self.query_contract(factory_address, "allTrusts", [trusts_count - 1], "CommunityTrustFactory")
            return {
                "status": "SUCCESS",
                "trust_address": trust_address,
                "tx_hash": tx_hash
            }
        return {
            "status": "FAILED",
            "tx_hash": tx_hash
        }

    async def deposit_to_trust(self, trust_address, eth_amount):
        """Deposits ETH to pool wealth in the trust."""
        trust_address = self.w3.to_checksum_address(trust_address)
        value_wei = self.w3.to_wei(eth_amount, 'ether')
        
        tx = await self.estimate_and_build_tx(
            contract_address=trust_address,
            function_name="deposit",
            args=[],
            abi_type="CommunityTrust",
            value_wei=value_wei
        )
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def propose_trust_transaction(self, trust_address, destination, value_wei, calldata_hex):
        """Proposes a transaction inside the trust (Directors only)."""
        trust_address = self.w3.to_checksum_address(trust_address)
        destination = self.w3.to_checksum_address(destination)
        
        calldata_bytes = bytes.fromhex(calldata_hex[2:]) if calldata_hex.startswith("0x") else bytes.fromhex(calldata_hex)
        
        tx = await self.estimate_and_build_tx(
            contract_address=trust_address,
            function_name="proposeTransaction",
            args=[destination, int(value_wei), calldata_bytes],
            abi_type="CommunityTrust",
            value_wei=0
        )
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def sign_trust_proposal(self, trust_address, proposal_id):
        """Signs a proposed transaction (Directors only)."""
        trust_address = self.w3.to_checksum_address(trust_address)
        
        tx = await self.estimate_and_build_tx(
            contract_address=trust_address,
            function_name="signTransaction",
            args=[int(proposal_id)],
            abi_type="CommunityTrust",
            value_wei=0
        )
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def execute_trust_proposal(self, trust_address, proposal_id):
        """Executes a proposed transaction once signature threshold is reached."""
        trust_address = self.w3.to_checksum_address(trust_address)
        
        tx = await self.estimate_and_build_tx(
            contract_address=trust_address,
            function_name="executeTransaction",
            args=[int(proposal_id)],
            abi_type="CommunityTrust",
            value_wei=0
        )
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def distribute_trust_dividends(self, trust_address, token_address, amount_wei):
        """Distributes dividends to depositors in the trust."""
        trust_address = self.w3.to_checksum_address(trust_address)
        token_address = self.w3.to_checksum_address(token_address) if token_address != "0x0000000000000000000000000000000000000000" and token_address != "0x0" else "0x0000000000000000000000000000000000000000"
        
        if token_address != "0x0000000000000000000000000000000000000000":
            account = self.get_account()
            abi = PREPACKAGED_ABIS["ERC20"]
            token_contract = self.w3.eth.contract(address=token_address, abi=abi)
            allowance = token_contract.functions.allowance(account.address, trust_address).call()
            if allowance < int(amount_wei):
                approve_tx = await self.estimate_and_build_tx(
                    contract_address=token_address,
                    function_name="approve",
                    args=[trust_address, int(amount_wei)],
                    abi_type="ERC20",
                    value_wei=0
                )
                approve_hash = await self.sign_and_send_transaction(approve_tx)
                await self.wait_for_confirmation(approve_hash)

        value_wei = int(amount_wei) if token_address == "0x0000000000000000000000000000000000000000" else 0
        tx = await self.estimate_and_build_tx(
            contract_address=trust_address,
            function_name="distributeDividends",
            args=[token_address, int(amount_wei)],
            abi_type="CommunityTrust",
            value_wei=value_wei
        )
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def claim_trust_dividends(self, trust_address, token_address):
        """Claims dividends accumulated in the trust for a given token (or ETH)."""
        trust_address = self.w3.to_checksum_address(trust_address)
        token_address = self.w3.to_checksum_address(token_address) if token_address != "0x0000000000000000000000000000000000000000" and token_address != "0x0" else "0x0000000000000000000000000000000000000000"
        
        tx = await self.estimate_and_build_tx(
            contract_address=trust_address,
            function_name="claimDividends",
            args=[token_address],
            abi_type="CommunityTrust",
            value_wei=0
        )
        tx_hash = await self.sign_and_send_transaction(tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        return receipt

    async def deploy_mock_asset(self, name, symbol):
        """Deploys a mock precious metal ERC20 asset (like cGOLD or cSILVER)."""
        import json
        json_path = os.path.join(os.path.dirname(__file__), "MockAsset.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError("MockAsset.json not found. Run compileTrust.cjs first.")
            
        with open(json_path, "r") as f:
            artifact = json.load(f)
            
        abi = artifact["abi"]
        bytecode = artifact["bytecode"]
        
        ContractFactory = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        account = self.get_account()
        
        nonce = self.w3.eth.get_transaction_count(account.address)
        gas_price = int(self.w3.eth.gas_price * 1.1)
        
        construct_tx = ContractFactory.constructor(name, symbol).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': 2000000,
            'chainId': self.network_config["chain_id"]
        })
        
        tx_hash = await self.sign_and_send_transaction(construct_tx)
        receipt = await self.wait_for_confirmation(tx_hash)
        
        if receipt.get("status") == "SUCCESS":
            raw_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            contract_address = raw_receipt.contractAddress
            await self.import_custom_token(symbol, contract_address, name, 18)
            return {
                "status": "SUCCESS",
                "contract_address": contract_address,
                "symbol": symbol,
                "tx_hash": tx_hash
            }
        return {
            "status": "FAILED",
            "tx_hash": tx_hash
        }







