# Robinhood Chain EVM Web3 MCP Server

A zero-dependency, pure Python **Model Context Protocol (MCP)** server specifically tailored for **Robinhood Chain** (and general Arbitrum Orbit Layer-2 networks). 

This server acts as a Web3/EVM bridge, allowing local AI agents (e.g., Claude, Cursor, Gemini CLI) to read states, estimate gas, simulate execution, and sign/broadcast transactions directly on-chain using simple JSON-RPC tools.

---

## Why This Matters 
Traditional developers entering a newly launched blockchain (like Robinhood Chain, launched July 2026) face significant friction:
1. **Context Window Bloat:** Passing complex, multi-thousand-line JSON ABIs to an LLM wastes tokens and causes memory degradation.
2. **AI-to-Web3 Gap:** AI models cannot natively compute gas, sign transactions, or verify contract logic without extensive boilerplate code.

This tool solves both:
- **Simplified Signatures:** Uses a local SQLite cache to store complex ABIs, exposing only human-readable, minimal signatures (e.g., `transfer(address,uint256)`) to the LLM.
- **Autonomous Execution:** Allows the agent to query, simulate (dry-run), sign, and verify transactions autonomously when a private key is provided in the environment variables.

---

## 🚀 Pitching for the $1M Arbitrum Open House Developer Grants
Robinhood Chain has committed **$1 Million** to support developer activity and ecosystem growth via the **Arbitrum Open House Program**. 

You can use this codebase to pitch for developer grants:
1. **Fork/Launch this server** as a standalone open-source developer tool.
2. **Build a demo dApp/agent** (e.g., a "Robinhood RWA Portfolio Manager Agent" that dynamically swaps USDG stablecoin yield into tokenized stocks like AAPL/TSLA).
3. **Submit to the Arbitrum / Robinhood Testnet Faucet and Open House program** as an active infrastructure contribution.

---

## 🛠️ Setup Instructions (Termux / Linux)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment variables
Create or update your `~/.env` file:
```env
# RPC Override (Default is Robinhood Mainnet)
ROBINHOOD_CHAIN_RPC_URL="https://rpc.mainnet.chain.robinhood.com"

# Private key for autonomous transaction signing (Keep this secure!)
ROBINHOOD_CHAIN_PRIVATE_KEY="0x..."
```

---

## 🔌 Connecting to AI Clients (MCP Setup)

### 1. Cursor
Go to **Settings > Models > MCP** and add a new server:
- **Name:** `Robinhood-EVM-MCP`
- **Type:** `command`
- **Command:** `python /data/data/com.termux/files/home/robinhood-evm-mcp/server.py`

### 2. Claude Desktop
Add this to your `claude_desktop_config.json` (usually at `~/.config/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "robinhood-evm-mcp": {
      "command": "python",
      "args": ["/data/data/com.termux/files/home/robinhood-evm-mcp/server.py"]
    }
  }
}
```

---

## 🛠️ Exposed MCP Tools

1. **`get_evm_balance(address, token_address)`**: Fetches native ETH or ERC-20 token balance. Supports ticker overrides (`USDG`, `AAPL`, `TSLA`).
2. **`query_smart_contract(contract_address, function_name, args, abi_type)`**: Executes a read-only query (call) on a smart contract.
3. **`simulate_evm_transaction(contract_address, function_name, args, value_wei)`**: Dry-runs a state-changing transaction and returns estimated gas details.
4. **`send_evm_transaction(contract_address, function_name, args, value_wei, wait_confirm)`**: Builds, signs, and broadcasts a transaction.
5. **`get_robinhood_ticker(ticker)`**: Retrieves the verified contract address of a tokenized stock or USDG.
6. **`switch_rpc_network(network_name)`**: Changes the active network configuration dynamically (options: `robinhood-mainnet`, `robinhood-testnet`, `localhost`).
7. **`register_custom_abi(contract_address, abi_json)`**: Saves custom smart contract ABIs to the local SQLite database mapping.
