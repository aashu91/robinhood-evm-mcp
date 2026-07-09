# server.py
# Pure Python, zero-dependency MCP server handling JSON-RPC over Standard I/O (stdio)

import sys
import json
import traceback
import asyncio
from web3 import Web3
from constants import TICKER_MAPPINGS, NETWORKS
from abi_manager import save_abi, get_abi, resolve_ticker_to_address
from web3_helper import Web3Helper

# Initialize Web3Helper instance
helper = Web3Helper()

# List of tools to register with the MCP client
TOOLS = [
    {
        "name": "get_evm_balance",
        "description": "Fetches the ETH (native) or ERC-20 token balance for a given address on the active chain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "The Ethereum wallet address (0x...)."},
                "token_address": {"type": "string", "description": "Optional: ERC-20 contract address (or ticker like USDG, AAPL, TSLA) to fetch token balance instead of native ETH."}
            },
            "required": ["address"]
        }
    },
    {
        "name": "query_smart_contract",
        "description": "Performs a read-only call (query) to a smart contract method.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_address": {"type": "string", "description": "Smart contract address (0x...)."},
                "function_name": {"type": "string", "description": "Name of the view/pure function to query."},
                "args": {"type": "array", "description": "Optional: Array of arguments to pass to the function.", "default": []},
                "abi_type": {"type": "string", "description": "Optional: Prepackaged ABI type ('ERC20', 'USDG_EARN')."}
            },
            "required": ["contract_address", "function_name"]
        }
    },
    {
        "name": "simulate_evm_transaction",
        "description": "Simulates a transaction locally (dry-run) and estimates gas usage without writing state on-chain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_address": {"type": "string", "description": "Smart contract address (0x...)."},
                "function_name": {"type": "string", "description": "Name of the write function to execute."},
                "args": {"type": "array", "description": "Optional: Array of arguments to pass to the function.", "default": []},
                "abi_type": {"type": "string", "description": "Optional: Prepackaged ABI type ('ERC20', 'USDG_EARN')."},
                "value_wei": {"type": "integer", "description": "Optional: Native ETH value in Wei to send with the transaction.", "default": 0}
            },
            "required": ["contract_address", "function_name"]
        }
    },
    {
        "name": "send_evm_transaction",
        "description": "Builds, signs with environment private key, and broadcasts a state-changing transaction on-chain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_address": {"type": "string", "description": "Smart contract address (0x...)."},
                "function_name": {"type": "string", "description": "Name of the function to execute."},
                "args": {"type": "array", "description": "Optional: Array of arguments to pass to the function.", "default": []},
                "abi_type": {"type": "string", "description": "Optional: Prepackaged ABI type ('ERC20', 'USDG_EARN')."},
                "value_wei": {"type": "integer", "description": "Optional: Native ETH value in Wei to send.", "default": 0},
                "wait_confirm": {"type": "boolean", "description": "Optional: Poll for receipt until confirmed (default: true).", "default": True}
            },
            "required": ["contract_address", "function_name"]
        }
    },
    {
        "name": "get_robinhood_ticker",
        "description": "Retrieves the contract address for a pre-packaged Robinhood Chain ticker asset.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The stock ticker symbol (e.g., AAPL, TSLA, USDG)."}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "switch_rpc_network",
        "description": "Changes the active RPC network configuration dynamically.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "network_name": {"type": "string", "description": "Network ID ('robinhood-mainnet', 'robinhood-testnet', 'localhost')."}
            },
            "required": ["network_name"]
        }
    },
    {
        "name": "register_custom_abi",
        "description": "Saves a custom smart contract ABI to the local SQLite database mapping, allowing dynamic execution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contract_address": {"type": "string", "description": "Smart contract address (0x...)."},
                "abi_json": {"type": "string", "description": "JSON string containing the full contract ABI."}
            },
            "required": ["contract_address", "abi_json"]
        }
    },
    {
        "name": "get_cross_chain_swap_quote",
        "description": "Estimates and returns transaction details for cross-chain swaps (e.g. Solana to Robinhood Chain) using the deBridge DLN API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "src_chain_id": {"type": "integer", "description": "Source chain ID (e.g., 7565164 for Solana, 8453 for Base, 42161 for Arbitrum)."},
                "src_token": {"type": "string", "description": "Address or ticker (SOL/ETH) of token on the source chain."},
                "dest_chain_id": {"type": "integer", "description": "Destination chain ID (e.g., 42161 for Arbitrum, 4663 for Robinhood Chain)."},
                "dest_token": {"type": "string", "description": "Address or ticker of token on the destination chain."},
                "amount_raw": {"type": "string", "description": "Raw input amount including token decimals (string to prevent int overflow)."},
                "recipient": {"type": "string", "description": "Wallet address that will receive the tokens on the destination chain."},
                "sender": {"type": "string", "description": "Optional: Wallet address managing the swap on the source chain."}
            },
            "required": ["src_chain_id", "src_token", "dest_chain_id", "dest_token", "amount_raw", "recipient"]
        }
    },
    {
        "name": "deploy_meme_coin",
        "description": "Deploys a standard ERC-20 meme coin on Robinhood Chain L2 via our custom MemeFactory launchpad (charges 0.005 ETH fee).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The name of the meme token (e.g. Robinhood Doge)."},
                "symbol": {"type": "string", "description": "The ticker symbol of the token (e.g. RHDOGE)."},
                "supply": {"type": "integer", "description": "Total initial supply of the token (e.g. 1000000000 for 1 Billion).", "default": 1000000000},
                "value_wei": {"type": "integer", "description": "Optional: Deployment fee in Wei (defaults to 0.005 ETH contract fee)."}
            },
            "required": ["name", "symbol"]
        }
    },
    {
        "name": "buy_meme_coin",
        "description": "Buys a meme coin launched on our MemeFactory platform by sending a specified amount of ETH with pre-flight slippage checks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "The contract address of the target meme token (0x...)."},
                "eth_amount": {"type": "number", "description": "The amount of ETH to spend on the swap (e.g. 0.05)."},
                "max_slippage": {"type": "number", "description": "Optional: Slippage tolerance percent e.g. 0.01 for 1% (default: 0.01).", "default": 0.01},
                "min_output_amount": {"type": "string", "description": "Optional: Enforce a minimum tokens to receive (string to avoid float errors)."}
            },
            "required": ["token_address", "eth_amount"]
        }
    },
    {
        "name": "sell_meme_coin",
        "description": "Sells a specified amount of meme coin tokens back to the MemeFactory virtual bonding curve with pre-flight slippage checks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "The contract address of the target meme token (0x...)."},
                "token_amount": {"type": "string", "description": "The number of tokens to sell (string to prevent decimal errors, e.g. 500000)."},
                "max_slippage": {"type": "number", "description": "Optional: Slippage tolerance percent e.g. 0.01 for 1% (default: 0.01).", "default": 0.01},
                "min_output_amount": {"type": "string", "description": "Optional: Enforce a minimum ETH to receive (string to avoid float errors)."}
            },
            "required": ["token_address", "token_amount"]
        }
    },
    {
        "name": "estimate_meme_trade_output",
        "description": "Calculates the expected output of a trade using the MemeFactory virtual constant product bonding curve reserves.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "The contract address of the target meme token (0x...)."},
                "trade_type": {"type": "string", "description": "The type of trade: 'buy' (spend ETH to get token) or 'sell' (spend token to get ETH)."},
                "amount": {"type": "number", "description": "The input amount (in ETH for buy, or tokens for sell)."}
            },
            "required": ["token_address", "trade_type", "amount"]
        }
    },
    {
        "name": "scan_launched_tokens",
        "description": "Queries the MemeFactory contract to discover all launched tokens, fetches their metadata on-chain, and caches/registers them.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "force_refresh": {"type": "boolean", "description": "Optional: Force a full on-chain refresh instead of returning cached SQLite lists.", "default": False}
            }
        }
    },
    {
        "name": "import_custom_token",
        "description": "Manually imports a custom token by symbol and contract address, caching it dynamically for resolution by ticker.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "The symbol/ticker of the token (e.g. DAPP)."},
                "address": {"type": "string", "description": "The contract address of the token (0x...)."},
                "name": {"type": "string", "description": "Optional: The human-readable name of the token."},
                "decimals": {"type": "integer", "description": "Optional: Number of decimals (default: 18).", "default": 18}
            },
            "required": ["ticker", "address"]
        }
    },
    {
        "name": "execute_cross_chain_bridge",
        "description": "Fetches cross-chain swap routing and transaction details, then builds, signs, and executes the bridging transaction directly on the source EVM chain.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "src_chain_id": {"type": "integer", "description": "Source chain ID (e.g. 8453 for Base, 42161 for Arbitrum)."},
                "src_token": {"type": "string", "description": "Source token contract address (or symbol)."},
                "dest_chain_id": {"type": "integer", "description": "Destination chain ID (e.g. 4663 for Robinhood Chain)."},
                "dest_token": {"type": "string", "description": "Destination token contract address (or symbol)."},
                "amount_raw": {"type": "string", "description": "Raw input amount (string to prevent float/int overflow)."},
                "recipient": {"type": "string", "description": "Wallet address that will receive the tokens on the destination chain."}
            },
            "required": ["src_chain_id", "src_token", "dest_chain_id", "dest_token", "amount_raw", "recipient"]
        }
    },
    {
        "name": "get_meme_price_chart",
        "description": "Queries historical event logs (TokenBought, TokenSold) and current bonding reserves for a meme token to reconstruct chronological OHLC/line price points.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "token_address": {"type": "string", "description": "The contract address of the target meme token (0x...)."},
                "block_range": {"type": "integer", "description": "Optional: How many blocks back to scan for logs (default: 10000).", "default": 10000}
            },
            "required": ["token_address"]
        }
    }
]

# Helper tool dispatcher
async def dispatch_tool(name, arguments):
    # Resolve ticker shortcuts in addresses
    for key in ["contract_address", "token_address"]:
        if key in arguments:
            resolved = await resolve_ticker_to_address(arguments[key])
            if resolved:
                arguments[key] = resolved

    if name == "get_evm_balance":
        address = arguments["address"]
        token_address = arguments.get("token_address")
        res = await helper.get_balance(address, token_address)
        return json.dumps(res, indent=2)

    elif name == "query_smart_contract":
        contract_addr = arguments["contract_address"]
        func_name = arguments["function_name"]
        args = arguments.get("args", [])
        abi_type = arguments.get("abi_type")
        res = await helper.query_contract(contract_addr, func_name, args, abi_type)
        return f"Query returned: {str(res)}"

    elif name == "simulate_evm_transaction":
        contract_addr = arguments["contract_address"]
        func_name = arguments["function_name"]
        args = arguments.get("args", [])
        abi_type = arguments.get("abi_type")
        val = arguments.get("value_wei", 0)
        res = await helper.estimate_and_build_tx(contract_addr, func_name, args, abi_type, val)
        # Strip large/complex parameters for clean response
        sim_summary = {
            "to": res.get("to"),
            "data_length": len(res.get("data", "")),
            "estimated_gas": res.get("gas"),
            "gasPrice_gwei": res.get("gasPrice", 0) / 10**9,
            "value_wei": res.get("value", 0)
        }
        return f"Simulation successful!\n{json.dumps(sim_summary, indent=2)}"

    elif name == "send_evm_transaction":
        contract_addr = arguments["contract_address"]
        func_name = arguments["function_name"]
        args = arguments.get("args", [])
        abi_type = arguments.get("abi_type")
        val = arguments.get("value_wei", 0)
        wait_confirm = arguments.get("wait_confirm", True)
        
        # Build
        tx = await helper.estimate_and_build_tx(contract_addr, func_name, args, abi_type, val)
        # Sign and Send
        tx_hash = await helper.sign_and_send_transaction(tx)
        
        if wait_confirm:
            receipt = await helper.wait_for_confirmation(tx_hash)
            return f"Transaction Broadcasted & Confirmed!\n{json.dumps(receipt, indent=2)}"
        else:
            return f"Transaction Broadcasted!\nTx Hash: {tx_hash}"

    elif name == "get_robinhood_ticker":
        ticker = arguments["ticker"].upper()
        if ticker in TICKER_MAPPINGS:
            return f"Canonical address for {ticker} on Robinhood Chain: {TICKER_MAPPINGS[ticker]}"
        else:
            return f"Ticker '{ticker}' not pre-packaged. Use 'register_custom_abi' if deploying a custom asset."

    elif name == "switch_rpc_network":
        network_name = arguments["network_name"]
        helper.switch_network(network_name)
        return f"Successfully switched active network to: {helper.network_config['name']} (Chain ID: {helper.network_config['chain_id']})"

    elif name == "register_custom_abi":
        contract_addr = arguments["contract_address"]
        abi_json = arguments["abi_json"]
        signatures = await save_abi(contract_addr, abi_json)
        return f"Successfully cached ABI for {contract_addr}.\nExposed function signatures:\n{signatures}"

    elif name == "get_cross_chain_swap_quote":
        src_id = arguments["src_chain_id"]
        src_tok = arguments["src_token"]
        dest_id = arguments["dest_chain_id"]
        dest_tok = arguments["dest_token"]
        amt = arguments["amount_raw"]
        recip = arguments["recipient"]
        snd = arguments.get("sender")
        res = await helper.get_cross_chain_quote(src_id, src_tok, dest_id, dest_tok, amt, recip, snd)
        return json.dumps(res, indent=2)

    elif name == "deploy_meme_coin":
        m_name = arguments["name"]
        m_symbol = arguments["symbol"]
        m_supply = arguments.get("supply", 1000000000)
        m_val = arguments.get("value_wei")
        receipt = await helper.deploy_meme_token(m_name, m_symbol, m_supply, m_val)
        return f"Meme coin deployed successfully!\nReceipt:\n{json.dumps(receipt, indent=2)}"

    elif name == "buy_meme_coin":
        t_addr = arguments["token_address"]
        eth_amt = arguments["eth_amount"]
        max_slip = arguments.get("max_slippage", 0.01)
        min_out = arguments.get("min_output_amount")
        receipt = await helper.buy_meme_token(t_addr, eth_amt, max_slip, min_out)
        return f"Meme coin purchased successfully!\nReceipt:\n{json.dumps(receipt, indent=2)}"

    elif name == "sell_meme_coin":
        t_addr = arguments["token_address"]
        t_amt = arguments["token_amount"]
        max_slip = arguments.get("max_slippage", 0.01)
        min_out = arguments.get("min_output_amount")
        receipt = await helper.sell_meme_token(t_addr, t_amt, max_slip, min_out)
        return f"Meme coin sold successfully!\nReceipt:\n{json.dumps(receipt, indent=2)}"

    elif name == "estimate_meme_trade_output":
        t_addr = arguments["token_address"]
        t_type = arguments["trade_type"]
        amt = arguments["amount"]
        res = await helper.estimate_meme_trade_output(t_addr, t_type, amt)
        return json.dumps(res, indent=2)

    elif name == "scan_launched_tokens":
        force_refresh = arguments.get("force_refresh", False)
        tokens = await helper.scan_factory_tokens(force_refresh)
        return json.dumps(tokens, indent=2)

    elif name == "import_custom_token":
        ticker = arguments["ticker"]
        addr = arguments["address"]
        t_name = arguments.get("name")
        dec = arguments.get("decimals", 18)
        res = await helper.import_custom_token(ticker, addr, t_name, dec)
        return f"Successfully imported custom token!\n{json.dumps(res, indent=2)}"

    elif name == "execute_cross_chain_bridge":
        src_id = arguments["src_chain_id"]
        src_tok = arguments["src_token"]
        dest_id = arguments["dest_chain_id"]
        dest_tok = arguments["dest_token"]
        amt = arguments["amount_raw"]
        recip = arguments["recipient"]
        res = await helper.execute_cross_chain_bridge(src_id, src_tok, dest_id, dest_tok, amt, recip)
        return f"Cross-chain bridge executed successfully!\n{json.dumps(res, indent=2)}"

    elif name == "get_meme_price_chart":
        t_addr = arguments["token_address"]
        b_range = arguments.get("block_range", 10000)
        res = await helper.get_meme_price_history(t_addr, b_range)
        return json.dumps(res, indent=2)

    else:
        raise ValueError(f"Unknown tool: {name}")

# ponytail: Centralized response writer with private key redaction to secure trust boundaries
def write_response(response_dict):
    res_str = json.dumps(response_dict)
    try:
        pk = helper.get_private_key()
        if pk:
            if pk in res_str:
                res_str = res_str.replace(pk, "[REDACTED_PRIVATE_KEY]")
            if f"0x{pk}" in res_str:
                res_str = res_str.replace(f"0x{pk}", "[REDACTED_PRIVATE_KEY]")
    except Exception:
        pass
    sys.stdout.write(res_str + "\n")
    sys.stdout.flush()

async def stdio_loop():
    """Asynchronous stdin/stdout communication loop implementing MCP over stdio."""
    # Setup async stdin reader
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
                
            request = json.loads(line.decode("utf-8"))
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            # Standard MCP Handshake
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "robinhood-chain-evm-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                write_response(response)

            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS
                    }
                }
                write_response(response)

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                try:
                    result_text = await dispatch_tool(tool_name, tool_args)
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": result_text
                                }
                            ],
                            "isError": False
                        }
                    }
                except Exception as tool_err:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error executing tool '{tool_name}': {str(tool_err)}\n{traceback.format_exc()}"
                                }
                            ],
                            "isError": True
                        }
                    }
                write_response(response)
                
            else:
                # Unsupported method
                if req_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                    write_response(response)

        except Exception as e:
            # Global syntax or formatting error
            err_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": f"Invalid Request: {str(e)}"
                }
            }
            write_response(err_response)

if __name__ == "__main__":
    try:
        asyncio.run(stdio_loop())
    except KeyboardInterrupt:
        pass
