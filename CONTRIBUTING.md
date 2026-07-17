# Contributing to Robinhood Chain EVM-MCP

Thank you for contributing! This project programmatically tracks issues and automates bounty distributions upon merging Pull Requests. 

We support and encourage contributions from **human developers** and **AI coding agents** (e.g., Antigravity, Claude Code, Cursor, Sweep).

---

## 1. Quick Setup for Development

### 1.1. Prerequisites
- **Python 3.11+**
- **pip** package manager
- **Node.js** (for Solidity compilation tools)

Clone the repository and install dependencies:
```bash
git clone https://github.com/salvationfinder/robinhood-evm-mcp.git
cd robinhood-evm-mcp
pip install -r requirements.txt
npm install solc
```

### 1.2. Environment Configuration
Configure local variables by creating a `.env` file:
```env
PRIVATE_KEY=0xYOUR_TEST_PRIVATE_KEY
ROBIN_MCP_TOKEN_ADDRESS=0xB6579E6489afC53Cd3eEb14eEF0EF039c65914bd
MEME_FACTORY_ADDRESS=0xAb783574A8B12d580659e86F01dEA310Fb300113
```

---

## 2. Test-Driven Development (TDD) Workflow

To prevent regression and ensure code quality, we enforce strict verification before merging.

### 2.1. Compilation
To compile contract modifications, run the local compilation node scripts:
```bash
node compileV2.cjs
node compileTrust.cjs
```
This updates the build artifacts in the root directory (`MemeFactoryV2.json`, `CommunityTrust.json`, etc.).

### 2.2. Running Tests
Verify your changes by running the unit tests:
```bash
python -m unittest test_trust.py
```
Ensure all tests pass on-chain (using the default testnet/mainnet parameters).

---

## 3. Pull Request Submission & Auto-Payouts

The repository runs a continuous curation daemon `github_payout_bot.py`. The daemon monitors merged pull requests, extracts the payout address, and executes the ERC-20 transfers instantly on-chain.

### 3.1. Formatting your Pull Request
To claim a bounty, the PR body **MUST** contain a valid EVM address formatted as:
`Wallet: 0xYourEVMWalletAddress`

#### Example PR Body:
> This PR implements Pyth Network oracle price feeds inside `CommunityTrust.sol`.
> 
> Closes #1
> 
> Wallet: 0x71C4B445C3B1d425780943C99Ea8A608f8a93f9

### 3.2. Programmatic Execution Check
The payout bot handles:
1. Fetching recent merged PRs using `gh pr list --state merged`.
2. Locating the matching wallet format.
3. Transferring **50,000 $ROBIN_MCP** from the treasury to the wallet on-chain.
4. Logging the receipt hash to the SQLite ledger database.
