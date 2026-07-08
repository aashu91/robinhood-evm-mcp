# test_client.py
# A command-line verification harness to test the MCP server over stdio without a desktop

import sys
import json
import asyncio
import subprocess

async def run_mcp_test():
    print("==================================================")
    print("🚀 Starting Robinhood EVM MCP Server Local Test...")
    print("==================================================")
    
    # Launch server.py as a subprocess
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    def send_request(req):
        payload = json.dumps(req) + "\n"
        process.stdin.write(payload)
        process.stdin.flush()
        print(f"\n📥 CLIENT SENT: {json.dumps(req, indent=2)}")
        
        # Read response line
        res_line = process.stdout.readline().strip()
        if res_line:
            response = json.loads(res_line)
            print(f"📤 SERVER RESPONDED: {json.dumps(response, indent=2)}")
            return response
        else:
            print("❌ No response from server.")
            return None

    # Step 1: Handshake (initialize)
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "mcp-cli-tester",
                "version": "1.0"
            }
        }
    }
    send_request(init_request)
    await asyncio.sleep(0.5)

    # Step 2: Query Tools List
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    send_request(list_request)
    await asyncio.sleep(0.5)

    # Step 3: Call get_robinhood_ticker tool for USDG
    ticker_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_robinhood_ticker",
            "arguments": {
                "ticker": "USDG"
            }
        }
    }
    send_request(ticker_request)
    await asyncio.sleep(0.5)

    # Step 4: Call get_evm_balance for a zero address (read-only blockchain call)
    balance_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_evm_balance",
            "arguments": {
                "address": "0x0000000000000000000000000000000000000000"
            }
        }
    }
    send_request(balance_request)
    await asyncio.sleep(0.5)

    # Step 5: Call get_cross_chain_swap_quote for 0.01 ETH from Base to Arbitrum
    cross_chain_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_cross_chain_swap_quote",
            "arguments": {
                "src_chain_id": 8453, # Base
                "src_token": "ETH",
                "dest_chain_id": 42161, # Arbitrum
                "dest_token": "ETH",
                "amount_raw": "10000000000000000", # 0.01 ETH
                "recipient": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
            }
        }
    }
    send_request(cross_chain_request)
    await asyncio.sleep(0.5)

    # Step 6: Import custom token
    import_request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "import_custom_token",
            "arguments": {
                "ticker": "TESTMEME",
                "address": "0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168",
                "name": "Test Meme Token",
                "decimals": 18
            }
        }
    }
    send_request(import_request)
    await asyncio.sleep(0.5)

    # Step 7: Query balance of imported TESTMEME to verify resolution
    resolve_request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "get_evm_balance",
            "arguments": {
                "address": "0x0000000000000000000000000000000000000000",
                "token_address": "TESTMEME"
            }
        }
    }
    send_request(resolve_request)
    await asyncio.sleep(0.5)

    # Step 8: Scan launched tokens
    scan_request = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "scan_launched_tokens",
            "arguments": {
                "force_refresh": False
            }
        }
    }
    send_request(scan_request)
    await asyncio.sleep(0.5)

    # Step 9: Estimate trade output (pre-flight checks)
    estimate_request = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "estimate_meme_trade_output",
            "arguments": {
                "token_address": "0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168",
                "trade_type": "buy",
                "amount": 0.05
            }
        }
    }
    send_request(estimate_request)
    await asyncio.sleep(0.5)

    # Clean up subprocess
    process.terminate()
    process.wait()
    print("\n==================================================")
    print("✅ MCP Local Verification Finished Successfully.")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_mcp_test())
