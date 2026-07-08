# server.py
# Pure Python, zero-dependency MCP server handling JSON-RPC over Standard I/O (stdio)

import sys
import json
import traceback
import asyncio
from web3 import Web3
from constants import TICKER_MAPPINGS, NETWORKS
from abi_manager import save_abi, get_abi
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
    }
]

# Helper tool dispatcher
async def dispatch_tool(name, arguments):
    # Resolve ticker shortcuts in addresses
    for key in ["contract_address", "token_address"]:
        if key in arguments and arguments[key] in TICKER_MAPPINGS:
            arguments[key] = TICKER_MAPPINGS[arguments[key]]

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

    else:
        raise ValueError(f"Unknown tool: {name}")

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
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

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
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
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
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

        except Exception as e:
            # Global syntax or formatting error
            err_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": f"Invalid Request: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(err_response) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        asyncio.run(stdio_loop())
    except KeyboardInterrupt:
        pass
