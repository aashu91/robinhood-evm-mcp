#!/usr/bin/env python3
"""
Robinhood Chain EVM MCP Server with Oracles, Staking, and Telegram Mini-App
Integrated with Pyth Network and Chainlink Oracles
"""

import sys
import os
import json
import asyncio
import traceback
from web3 import Web3
from web3_helper import Web3Helper
from abi_manager import save_abi, get_abi, resolve_ticker_to_address

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import oracles
from oracles.pyth_oracle import PythOracle
from oracles.chainlink_oracle import ChainlinkOracle
from oracles.unified_oracles import UnifiedOracles

# Import staking contract
import importlib.util
import inspect

# Initialize Web3Helper instance
helper = Web3Helper()

# Global oracles instances
pyth_oracle = None
chainlink_oracle = None
unified_oracles = None

# Global staking contract
staking_contract = None

# Load environment variables
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


async def initialize_oracles():
    """Initialize oracles on first use"""
    global pyth_oracle, chainlink_oracle, unified_oracles

    if pyth_oracle is None:
        pyth_oracle = PythOracle()
        chainlink_oracle = ChainlinkOracle()
        unified_oracles = UnifiedOracles()

    return pyth_oracle, chainlink_oracle, unified_oracles


def initialize_staking_contract():
    """Initialize StakingYield contract"""
    global staking_contract

    if staking_contract is None:
        try:
            contract_path = os.path.join(
                os.path.dirname(__file__),
                "contracts",
                "StakingYield.json"
            )

            if os.path.exists(contract_path):
                with open(contract_path, "r") as f:
                    contract_abi = json.load(f)

                staking_contract = helper.w3.eth.contract(
                    address=web3_helper.w3.to_checksum_address(os.getenv("STAKING_CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")),
                    abi=contract_abi
                )
        except Exception as e:
            print(f"⚠️  Failed to load staking contract: {e}")

    return staking_contract


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
        "name": "get_pyth_price",
        "description": "Get current price from Pyth Network for GOLD or SILVER (low-latency commodity prices).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "commodity": {"type": "string", "description": "Commodity symbol ('GOLD' or 'SILVER').", "enum": ["GOLD", "SILVER"]}
            },
            "required": ["commodity"]
        }
    },
    {
        "name": "get_chainlink_price",
        "description": "Get current price from Chainlink Oracles for stock tickers (AAPL, TSLA, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, TSLA)."}
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_all_prices",
        "description": "Get all prices from Pyth (GOLD, SILVER) and Chainlink (AAPL, TSLA) oracles.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "stake_tokens",
        "description": "Stake native tokens (ETH/USDG) in the StakingYield contract with oracle-based yield calculation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount_wei": {"type": "integer", "description": "Amount of tokens to stake in Wei."}
            },
            "required": ["amount_wei"]
        }
    },
    {
        "name": "unstake_tokens",
        "description": "Unstake tokens from the StakingYield contract and claim rewards.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount_wei": {"type": "integer", "description": "Amount of tokens to unstake in Wei."}
            },
            "required": ["amount_wei"]
        }
    },
    {
        "name": "claim_staking_rewards",
        "description": "Claim staking rewards without unstaking tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_staking_info",
        "description": "Get staking information for a given address (staked amount, pending rewards, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "address": {"type": "string", "description": "Wallet address to query staking info."}
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_staking_contract_balance",
        "description": "Get the total balance of the StakingYield contract.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_telegram_minapp_url",
        "description": "Get the URL for the Telegram Mini-App (frontend HTML file).",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_telegram_backend_url",
        "description": "Get the URL for the Telegram Mini-App backend API.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_telegram_minapp_health",
        "description": "Check if the Telegram Mini-App backend is running and healthy.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
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
        "name": "deploy_mock_asset",
        "description": "Deploys a mock precious metal ERC-20 token (like cGOLD or cSILVER) for testing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the asset (e.g. Mock Gold)."},
                "symbol": {"type": "string", "description": "Symbol of the asset (e.g. cGOLD)."}
            },
            "required": ["name", "symbol"]
        }
    },
    {
        "name": "deploy_community_trust_factory",
        "description": "Deploys the CommunityTrustFactory contract for creating Community Trusts.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_trust_proposal",
        "description": "Creates a new proposal within a Community Trust.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trust_address": {"type": "string", "description": "The trust address."},
                "description": {"type": "string", "description": "Description of the proposal."},
                "amount_wei": {"type": "string", "description": "Amount to propose in Wei."}
            },
            "required": ["trust_address", "description", "amount_wei"]
        }
    },
    {
        "name": "vote_on_trust_proposal",
        "description": "Votes on an existing proposal within a Community Trust.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trust_address": {"type": "string", "description": "The trust address."},
                "proposal_id": {"type": "integer", "description": "The index of the proposal to vote on."},
                "vote": {"type": "string", "description": "Vote choice ('yes', 'no', 'abstain')."}
            },
            "required": ["trust_address", "proposal_id", "vote"]
        }
    },
    {
        "name": "execute_trust_proposal",
        "description": "Executes a proposal once signature threshold is reached (Directors only).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trust_address": {"type": "string", "description": "The trust address."},
                "proposal_id": {"type": "integer", "description": "The index of the proposal to execute."}
            },
            "required": ["trust_address", "proposal_id"]
        }
    },
    {
        "name": "distribute_trust_dividends",
        "description": "Distributes ETH or ERC-20 dividends to the trust depositors proportionally.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trust_address": {"type": "string", "description": "The trust address."},
                "token_address": {"type": "string", "description": "The dividend token address (or '0x0000000000000000000000000000000000000000' for ETH)."},
                "amount_wei": {"type": "string", "description": "Amount to distribute in raw unit/wei."}
            },
            "required": ["trust_address", "token_address", "amount_wei"]
        }
    },
    {
        "name": "claim_trust_dividends",
        "description": "Claims accumulated dividends in the trust.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trust_address": {"type": "string", "description": "The trust address."},
                "token_address": {"type": "string", "description": "The dividend token address (or '0x0000000000000000000000000000000000000000' for ETH)."}
            },
            "required": ["trust_address", "token_address"]
        }
    },
]


# Tool handlers
async def handle_get_pyth_price(args):
    """Handle get_pyth_price tool"""
    try:
        pyth_oracle, _, _ = await initialize_oracles()

        commodity = args.get("commodity", "GOLD")
        result = await pyth_oracle.get_price_by_ticker(commodity)

        return {
            "success": True,
            "data": result,
            "message": f"Successfully fetched {commodity} price from Pyth Network"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to fetch {commodity} price from Pyth Network"
        }


async def handle_get_chainlink_price(args):
    """Handle get_chainlink_price tool"""
    try:
        _, chainlink_oracle, _ = await initialize_oracles()

        ticker = args.get("ticker", "AAPL")
        result = await chainlink_oracle.get_price_by_ticker(ticker)

        return {
            "success": True,
            "data": result,
            "message": f"Successfully fetched {ticker} price from Chainlink Oracles"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to fetch {ticker} price from Chainlink Oracles"
        }


async def handle_get_all_prices(args):
    """Handle get_all_prices tool"""
    try:
        _, _, unified_oracles = await initialize_oracles()

        result = await unified_oracles.get_all_prices()

        return {
            "success": True,
            "data": result,
            "message": "Successfully fetched all prices from Pyth and Chainlink oracles"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch all prices from oracles"
        }


async def handle_stake_tokens(args):
    """Handle stake_tokens tool"""
    try:
        if not initialize_staking_contract():
            return {
                "success": False,
                "error": "Staking contract not deployed",
                "message": "Please deploy the StakingYield contract first using deploy_staking.py"
            }

        amount_wei = args.get("amount_wei", 0)
        tx_hash = staking_contract.functions.stake(amount_wei).transact({
            "from": helper.get_account().address,
            "value": amount_wei,
            "gas": 200000
        })

        tx_receipt = helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "success": True,
            "tx_hash": helper.w3.to_hex(tx_hash),
            "tx_receipt": {
                "status": tx_receipt.status,
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            },
            "message": f"Successfully staked {amount_wei} wei"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to stake tokens"
        }


async def handle_unstake_tokens(args):
    """Handle unstake_tokens tool"""
    try:
        if not initialize_staking_contract():
            return {
                "success": False,
                "error": "Staking contract not deployed",
                "message": "Please deploy the StakingYield contract first using deploy_staking.py"
            }

        amount_wei = args.get("amount_wei", 0)
        tx_hash = staking_contract.functions.unstake(amount_wei).transact({
            "from": helper.get_account().address,
            "gas": 200000
        })

        tx_receipt = helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "success": True,
            "tx_hash": helper.w3.to_hex(tx_hash),
            "tx_receipt": {
                "status": tx_receipt.status,
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            },
            "message": f"Successfully unstaked {amount_wei} wei"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to unstake tokens"
        }


async def handle_claim_staking_rewards(args):
    """Handle claim_staking_rewards tool"""
    try:
        if not initialize_staking_contract():
            return {
                "success": False,
                "error": "Staking contract not deployed",
                "message": "Please deploy the StakingYield contract first using deploy_staking.py"
            }

        tx_hash = staking_contract.functions.claimRewards().transact({
            "from": helper.get_account().address,
            "gas": 200000
        })

        tx_receipt = helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "success": True,
            "tx_hash": helper.w3.to_hex(tx_hash),
            "tx_receipt": {
                "status": tx_receipt.status,
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            },
            "message": "Successfully claimed staking rewards"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to claim rewards"
        }


async def handle_get_staking_info(args):
    """Handle get_staking_info tool"""
    try:
        if not initialize_staking_contract():
            return {
                "success": False,
                "error": "Staking contract not deployed",
                "message": "Please deploy the StakingYield contract first using deploy_staking.py"
            }

        address = args.get("address", helper.get_account().address)
        staked_amount, pending_rewards = staking_contract.functions.getUserStakingInfo(
            helper.w3.to_checksum_address(address)
        ).call()

        total_rewards = staking_contract.functions.getTotalRewards().call()
        contract_balance = staking_contract.functions.getContractBalance().call()
        reward_rate = staking_contract.functions.getRewardRate().call()

        return {
            "success": True,
            "data": {
                "address": address,
                "stakedAmount": staked_amount,
                "pendingRewards": pending_rewards,
                "totalRewards": total_rewards,
                "contractBalance": contract_balance,
                "rewardRate": reward_rate,
                "rewardRatePercent": reward_rate / 100
            },
            "message": "Successfully fetched staking information"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch staking information"
        }


async def handle_get_staking_contract_balance(args):
    """Handle get_staking_contract_balance tool"""
    try:
        if not initialize_staking_contract():
            return {
                "success": False,
                "error": "Staking contract not deployed",
                "message": "Please deploy the StakingYield contract first using deploy_staking.py"
            }

        balance = staking_contract.functions.getContractBalance().call()
        reward_rate = staking_contract.functions.getRewardRate().call()

        return {
            "success": True,
            "data": {
                "balance": balance,
                "balance_eth": helper.w3.from_wei(balance, 'ether'),
                "rewardRate": reward_rate,
                "rewardRatePercent": reward_rate / 100
            },
            "message": "Successfully fetched contract balance"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to fetch contract balance"
        }


async def handle_get_telegram_minapp_url(args):
    """Handle get_telegram_minapp_url tool"""
    try:
        minapp_path = os.path.join(
            os.path.dirname(__file__),
            "telegram_minapp.html"
        )

        return {
            "success": True,
            "url": f"file://{minapp_path}",
            "message": "Telegram Mini-App frontend file path"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get Mini-App URL"
        }


async def handle_get_telegram_backend_url(args):
    """Handle get_telegram_backend_url tool"""
    try:
        backend_path = os.path.join(
            os.path.dirname(__file__),
            "telegram_backend.py"
        )

        return {
            "success": True,
            "url": f"file://{backend_path}",
            "message": "Telegram Mini-App backend API file path"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get backend URL"
        }


async def handle_get_telegram_minapp_health(args):
    """Handle get_telegram_minapp_health tool"""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/health") as response:
                data = await response.json()

                return {
                    "success": True,
                    "data": data,
                    "message": "Telegram Mini-App backend is running"
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Telegram Mini-App backend is not running or not accessible"
        }


# Tool execution handler
async def execute_tool(tool_name, arguments):
    """Execute a tool by name with arguments"""
    tool_handlers = {
        "get_pyth_price": handle_get_pyth_price,
        "get_chainlink_price": handle_get_chainlink_price,
        "get_all_prices": handle_get_all_prices,
        "stake_tokens": handle_stake_tokens,
        "unstake_tokens": handle_unstake_tokens,
        "claim_staking_rewards": handle_claim_staking_rewards,
        "get_staking_info": handle_get_staking_info,
        "get_staking_contract_balance": handle_get_staking_contract_balance,
        "get_telegram_minapp_url": handle_get_telegram_minapp_url,
        "get_telegram_backend_url": handle_get_telegram_backend_url,
        "get_telegram_minapp_health": handle_get_telegram_minapp_health,
    }

    if tool_name not in tool_handlers:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
            "message": f"Tool '{tool_name}' is not available"
        }

    handler = tool_handlers[tool_name]
    return await handler(arguments)


# Main server function
async def main():
    """Main server entry point"""
    print("🚀 Robinhood Chain EVM MCP Server with Oracles and Staking")
    print("=" * 70)

    # Initialize Web3 connection
    if not helper.connect():
        print("❌ Failed to connect to Web3")
        return

    print(f"✅ Connected to: {helper.network_config['name']}")
    print(f"📍 RPC URL: {helper.w3.provider.endpoint_uri}")

    # Load environment variables
    load_env()

    # Print available tools
    print(f"\n📋 Available Tools ({len(TOOLS)}):")
    for tool in TOOLS:
        print(f"  - {tool['name']}: {tool['description']}")

    print("\n" + "=" * 70)
    print("Server is ready. Listening for JSON-RPC requests over stdio...")
    print("=" * 70)

    # Read JSON-RPC requests from stdin
    while True:
        try:
            # Read request from stdin
            request_line = sys.stdin.readline()
            if not request_line:
                break

            request = json.loads(request_line)

            # Extract tool name and arguments
            tool_name = request.get("method", "")
            arguments = request.get("params", {})

            # Execute tool
            result = await execute_tool(tool_name, arguments)

            # Send response
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": result
            }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "details": str(e)
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "details": str(e)
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
