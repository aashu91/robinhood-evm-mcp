#!/usr/bin/env python3
# mcp_cli.py
# Interactive SDK wrapper and test client for robinhood-chain-evm-mcp
# ponytail: simple, self-contained CLI supporting direct imports or real JSON-RPC over subprocess.

import os
import sys
import json
import asyncio
import argparse
import subprocess

# Add current directory to path if importing directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import TOOLS, dispatch_tool

def print_banner():
    print("=" * 65)
    print("      ROBINHOOD CHAIN EVM MODEL CONTEXT PROTOCOL (MCP) CLI      ")
    print("=" * 65)

def list_tools():
    print("\nAvailable MCP Tools:")
    for idx, t in enumerate(TOOLS):
        print(f" [{idx}] {t['name']}")
        print(f"     Description: {t['description']}")
        print(f"     Required properties: {t['inputSchema'].get('required', [])}")

async def run_direct(tool_name, args_dict):
    print(f"\n[Direct Mode] Dispatching tool '{tool_name}'...")
    try:
        res = await dispatch_tool(tool_name, args_dict)
        return res
    except Exception as e:
        return f"Error: {str(e)}"

def run_rpc(tool_name, args_dict):
    print(f"\n[RPC Mode] Spawning mcp_server.py process...")
    # Formulate JSON-RPC message
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args_dict
        }
    }
    
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
    try:
        proc = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Write JSON-RPC payload followed by newline
        stdout_data, stderr_data = proc.communicate(input=json.dumps(payload) + "\n", timeout=10)
        
        if proc.returncode != 0:
            return f"Server process exited with code {proc.returncode}. Stderr:\n{stderr_data}"
            
        # Parse output line by line to locate JSON-RPC response
        for line in stdout_data.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                resp = json.loads(line)
                if "result" in resp:
                    content_list = resp["result"].get("content", [])
                    if content_list:
                        return content_list[0].get("text", "")
                    return json.dumps(resp["result"], indent=2)
                elif "error" in resp:
                    return f"JSON-RPC Error: {json.dumps(resp['error'], indent=2)}"
            except json.JSONDecodeError:
                continue
        return f"Could not find valid JSON-RPC response. Raw stdout:\n{stdout_data}"
    except Exception as e:
        return f"Process execution failed: {str(e)}"

def interactive_loop(use_rpc):
    print_banner()
    while True:
        list_tools()
        print("\nOptions:")
        print(" Enter tool index [0-N] to execute")
        print(" Enter 'q' to quit")
        choice = input("\nChoose an option: ").strip()
        
        if choice.lower() == 'q':
            break
            
        try:
            idx = int(choice)
            if idx < 0 or idx >= len(TOOLS):
                print("Invalid index choice.")
                continue
        except ValueError:
            print("Please enter a valid number or 'q'.")
            continue
            
        tool = TOOLS[idx]
        tool_name = tool["name"]
        schema = tool["inputSchema"]
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        print(f"\n--- Configuring arguments for '{tool_name}' ---")
        args_dict = {}
        for prop_name, prop_info in properties.items():
            req_marker = " (Required)" if prop_name in required else " (Optional)"
            desc = prop_info.get("description", "")
            default = prop_info.get("default")
            default_str = f" [default: {default}]" if default is not None else ""
            
            val = input(f" {prop_name}{req_marker} - {desc}{default_str}: ").strip()
            if not val:
                if prop_name in required:
                    print(f"  ❌ Error: '{prop_name}' is required.")
                    break
                if default is not None:
                    args_dict[prop_name] = default
            else:
                # Basic type coercion
                p_type = prop_info.get("type")
                try:
                    if p_type == "integer":
                        args_dict[prop_name] = int(val)
                    elif p_type == "number":
                        args_dict[prop_name] = float(val)
                    elif p_type == "boolean":
                        args_dict[prop_name] = val.lower() in ("true", "1", "yes")
                    elif p_type == "array":
                        args_dict[prop_name] = json.loads(val)
                    else:
                        args_dict[prop_name] = val
                except Exception as parse_err:
                    print(f"  ❌ Failed to parse input as type '{p_type}': {str(parse_err)}")
                    break
        else:
            # Executes if loop completes without breaking (i.e. all required fields present)
            if use_rpc:
                result = run_rpc(tool_name, args_dict)
            else:
                result = asyncio.run(run_direct(tool_name, args_dict))
                
            print("\n" + "="*30 + " TOOL RESULT " + "="*30)
            print(result)
            print("="*73 + "\n")
            input("Press Enter to continue...")

def main():
    parser = argparse.ArgumentParser(description="Test CLI client for the Robinhood Chain EVM MCP server.")
    parser.add_argument("--tool", type=str, help="Tool name to execute (runs non-interactively).")
    parser.add_argument("--args", type=str, help="JSON arguments string for the tool.")
    parser.add_argument("--rpc", action="store_true", help="Use standard JSON-RPC over stdin/stdout subprocess instead of direct Python imports.")
    args = parser.parse_args()

    if args.tool:
        args_dict = {}
        if args.args:
            try:
                args_dict = json.loads(args.args)
            except json.JSONDecodeError as err:
                print(f"Error parsing --args JSON: {str(err)}")
                sys.exit(1)
        
        if args.rpc:
            result = run_rpc(args.tool, args_dict)
        else:
            result = asyncio.run(run_direct(args.tool, args_dict))
        print(result)
    else:
        interactive_loop(args.rpc)

if __name__ == "__main__":
    main()
