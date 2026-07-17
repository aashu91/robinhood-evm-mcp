# Robinhood Chain EVM-MCP Server Setup Guide
This guide details how to install, configure, test, and integrate the EVM Model Context Protocol (MCP) server into your AI agent workflows (Cursor, Claude Code, and Sweep).

---

## 1. Prerequisites
- **Python 3.11+**
- **pip** package manager
- **Node.js** (optional, only if compiling Solidity contracts locally)

Install Python dependencies:
```bash
pip install -r requirements.txt
```
*Note: Key dependencies include `web3`, `eth-account`, and `requests`.*

---

## 2. Environment Configuration
Create a `.env` file in the root of the server directory:
```env
# Active EVM Wallet Private Key (for signing transactions)
PRIVATE_KEY=0xYOUR_WALLET_PRIVATE_KEY

# Optional RPC Overrides
ROBINHOOD_MAINNET_RPC=https://rpc.mainnet.chain.robinhood.com
ROBINHOOD_TESTNET_RPC=https://rpc.testnet.chain.robinhood.com

# Address of Staking/Utility token (for token gating checks)
ROBIN_MCP_TOKEN_ADDRESS=0xB6579E6489afC53Cd3eEb14eEF0EF039c65914bd

# Address of MemeFactory contract (V2 curve deployments)
MEME_FACTORY_ADDRESS=0xAb783574A8B12d580659e86F01dEA310Fb300113
```

---

## 3. Integration with IDEs and AI Agents

### 3.1. Cursor IDE
1. Open Cursor and navigate to **Settings** -> **Features** -> **MCP**.
2. Click **+ Add New MCP Server**.
3. Fill in the parameters:
   - **Name:** `robinhood-evm`
   - **Type:** `command`
   - **Command:** `python /absolute/path/to/robinhood-evm-mcp/mcp_server.py`
4. Click **Save**. Cursor will start the server and load the tool schemas automatically.

### 3.2. Claude Code
Run the following CLI command inside your terminal:
```bash
claude mcp add robinhood-evm python /absolute/path/to/robinhood-evm-mcp/mcp_server.py
```
To verify active tools, run `claude mcp list`.

### 3.3. Sweep Agent
Add the following block to your `.github/sweep.yaml` configuration file:
```yaml
mcp_servers:
  - name: "robinhood-evm"
    command: ["python", "/absolute/path/to/robinhood-evm-mcp/mcp_server.py"]
    env:
      PRIVATE_KEY: "0x..."
```

---

## 4. Local Testing and Verification
The server includes a local interactive SDK tool wrapper `mcp_cli.py` to verify that tool execution, ABI registry cache, and curves function properly:

#### Run Interactive Prompt
```bash
python mcp_cli.py
```
This launches a CLI text prompt. You can choose a tool, input parameters, and receive outputs.

#### Direct Single Tool Test
```bash
python mcp_cli.py --tool get_evm_balance --args '{"address": "0xAb783574A8B12d580659e86F01dEA310Fb300113"}'
```

#### JSON-RPC Over Subprocess Test
Verify that stdio JSON-RPC messaging is fully compliant by adding the `--rpc` flag:
```bash
python mcp_cli.py --rpc --tool get_evm_balance --args '{"address": "0xAb783574A8B12d580659e86F01dEA310Fb300113"}'
```
This starts `mcp_server.py` as a subprocess, streams raw JSON-RPC 2.0 payloads to its stdin, and prints the resolved standard output response.
