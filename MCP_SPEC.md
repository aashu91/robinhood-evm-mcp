# Robinhood Chain EVM Model Context Protocol (EVM-MCP) Specification
This document outlines the JSON-RPC tools and schema specifications for the **Robinhood Chain EVM Model Context Protocol** server. This server exposes Layer 2 operations, bonding curve trading, and Community Trust multi-sig banks to standard LLM clients (like Cursor, Claude Code, and Sweep).

---

## 1. Protocol Architecture
The EVM-MCP server implements the Model Context Protocol (MCP) over Standard Input/Output (stdio). 

All communication adheres to JSON-RPC 2.0. The server supports the following standard lifecycle methods:
- `initialize`: Establishes protocol version and reports capabilities.
- `tools/list`: Exposes all available EVM tools and input validation schemas.
- `tools/call`: Executes a tool by name with arbitrary parameters.

---

## 2. Token-Gating Constraint
To drive developer and platform adoption, tool execution on `robinhood-mainnet` is token-gated:
- **Requirement:** User must hold at least **100 $ROBIN_MCP** tokens in the active wallet address configured under `.env` (`PRIVATE_KEY`).
- **Bypass:** The gateway automatically bypasses checks when the active RPC network is switched to `robinhood-testnet` or `localhost` to facilitate fee-free local development.

---

## 3. Tool Specifications

### 3.1. Core EVM Utilities
#### `get_evm_balance`
Fetches native ETH or ERC-20 token balances.
- **Arguments:**
  - `address` (string, required): Ethereum address to inspect.
  - `token_address` (string, optional): ERC-20 address or registered ticker (e.g. `USDG`, `AAPL`).

#### `query_smart_contract`
Performs read-only viewing calls to on-chain methods.
- **Arguments:**
  - `contract_address` (string, required): Smart contract target address.
  - `function_name` (string, required): pure/view function name.
  - `args` (array, optional): Function arguments list.
  - `abi_type` (string, optional): ABI mapping shortcut (e.g., `ERC20`).

#### `simulate_evm_transaction`
Simulates state changes and estimates transaction gas usage without modifying on-chain state.
- **Arguments:**
  - `contract_address` (string, required)
  - `function_name` (string, required)
  - `args` (array, optional)
  - `value_wei` (integer, optional)

#### `send_evm_transaction`
Signs and broadcasts a transaction.
- **Arguments:**
  - `contract_address` (string, required)
  - `function_name` (string, required)
  - `args` (array, optional)
  - `value_wei` (integer, optional)
  - `wait_confirm` (boolean, optional)

---

### 3.2. Registry & RPC Configuration
#### `switch_rpc_network`
Switches active RPC network and updates the underlying web3 provider.
- **Arguments:**
  - `network_name` (string, required): `robinhood-mainnet`, `robinhood-testnet`, or `localhost`.

#### `register_custom_abi`
Caches raw JSON ABI strings in the local SQLite db mapped by contract address.
- **Arguments:**
  - `contract_address` (string, required)
  - `abi_json` (string, required)

#### `import_custom_token`
Registers symbols or stock tickers to address locations.
- **Arguments:**
  - `ticker` (string, required)
  - `address` (string, required)
  - `name` (string, optional)
  - `decimals` (integer, optional)

---

### 3.3. Meme Launchpad (Virtual Bonding Curves)
#### `deploy_meme_coin`
Deploys a custom ERC-20 token and registers curve parameters with `MemeFactoryV2`.
- **Arguments:**
  - `name` (string, required)
  - `symbol` (string, required)
  - `supply` (integer, optional)

#### `buy_meme_coin` / `sell_meme_coin`
Executes token swaps directly against the constant product bonding curves.
- **Arguments:**
  - `token_address` (string, required)
  - `eth_amount` / `token_amount` (required)
  - `max_slippage` (number, optional)

#### `estimate_meme_trade_output`
Calculates expected output tokens/ETH given trade parameters.

---

### 3.4. Community Trust Multi-Sig Bank
#### `deploy_community_trust`
Spawns a new Community Trust bank contract through the factory.
- **Arguments:**
  - `factory_address` (string, required)
  - `name` (string, required)
  - `directors` (array of strings, required)
  - `required_signatures` (integer, required)

#### `propose_trust_transaction`
Proposes an investment or payout transaction (directors only).
- **Arguments:**
  - `trust_address` (string, required)
  - `destination` (string, required)
  - `calldata_hex` (string, required)

#### `sign_trust_proposal` / `execute_trust_proposal`
Signs/executes proposed transactions once threshold is reached.

#### `distribute_trust_dividends` / `claim_trust_dividends`
Enables distributing pooled wealth dividends or claiming user stakes proportionally.
