# MCP Server Integration Guide

**Version**: 1.0
**Date**: 2026-07-20
**Project**: Robinhood Chain EVM MCP Server with Oracles and Staking

---

## 📋 Overview

The MCP Server has been extended with three major features:

1. **Oracles Integration**
   - Pyth Network (GOLD, SILVER)
   - Chainlink Oracles (AAPL, TSLA, etc.)
   - Unified Oracles Interface

2. **Staking Contract Integration**
   - StakingYield contract
   - Stake/Unstake/Rewards
   - Oracle-based yield calculation

3. **Telegram Mini-App Integration**
   - Frontend HTML
   - Backend API
   - Health checks

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/liunix/workspace/robinhood-evm-mcp
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env and add:
# ROBINHOOD_CHAIN_PRIVATE_KEY=your_private_key
# ROBINHOOD_CHAIN_RPC_URL=https://your_rpc_url
# PYTH_ORACLE_ADDRESS=0x...
# CHAINLINK_ORACLE_ADDRESS=0x...
```

### 3. Deploy Staking Contract

```bash
python deploy_staking_complete.py
```

### 4. Start MCP Server

```bash
python mcp_server_with_integration.py
```

---

## 🔧 Tools Available

### Oracles Tools

#### `get_pyth_price`
Get current price from Pyth Network for GOLD or SILVER.

**Parameters:**
```json
{
  "commodity": "GOLD" // or "SILVER"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "price": 2000.50,
    "confidence": 0.99,
    "source": "Pyth Network"
  },
  "message": "Successfully fetched GOLD price from Pyth Network"
}
```

#### `get_chainlink_price`
Get current price from Chainlink Oracles for stock tickers.

**Parameters:**
```json
{
  "ticker": "AAPL"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "price": 175.25,
    "confidence": 0.999,
    "source": "Chainlink Oracles"
  },
  "message": "Successfully fetched AAPL price from Chainlink Oracles"
}
```

#### `get_all_prices`
Get all prices from Pyth (GOLD, SILVER) and Chainlink (AAPL, TSLA) oracles.

**Response:**
```json
{
  "success": true,
  "data": {
    "GOLD": { ... },
    "SILVER": { ... },
    "AAPL": { ... },
    "TSLA": { ... }
  },
  "message": "Successfully fetched all prices from Pyth and Chainlink oracles"
}
```

### Staking Tools

#### `stake_tokens`
Stake native tokens (ETH/USDG) in the StakingYield contract.

**Parameters:**
```json
{
  "amount_wei": 1000000000000000000 // 1 ETH in Wei
}
```

**Response:**
```json
{
  "success": true,
  "tx_hash": "0x...",
  "tx_receipt": {
    "status": 1,
    "gas_used": 150000,
    "block_number": 12345678
  },
  "message": "Successfully staked 1000000000000000000 wei"
}
```

#### `unstake_tokens`
Unstake tokens from the StakingYield contract.

**Parameters:**
```json
{
  "amount_wei": 1000000000000000000 // 1 ETH in Wei
}
```

#### `claim_staking_rewards`
Claim staking rewards without unstaking tokens.

**Response:**
```json
{
  "success": true,
  "tx_hash": "0x...",
  "message": "Successfully claimed staking rewards"
}
```

#### `get_staking_info`
Get staking information for a given address.

**Parameters:**
```json
{
  "address": "0x..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "address": "0x...",
    "stakedAmount": 1000000000000000000,
    "pendingRewards": 50000000000000000,
    "totalRewards": 1000000000000000000,
    "contractBalance": 10000000000000000000,
    "rewardRate": 5,
    "rewardRatePercent": 0.05
  },
  "message": "Successfully fetched staking information"
}
```

#### `get_staking_contract_balance`
Get the total balance of the StakingYield contract.

**Response:**
```json
{
  "success": true,
  "data": {
    "balance": 10000000000000000000,
    "balance_eth": 10.0,
    "rewardRate": 5,
    "rewardRatePercent": 0.05
  },
  "message": "Successfully fetched contract balance"
}
```

### Telegram Mini-App Tools

#### `get_telegram_minapp_url`
Get the URL for the Telegram Mini-App frontend.

**Response:**
```json
{
  "success": true,
  "url": "file:///home/liunix/workspace/robinhood-evm-mcp/telegram_minapp.html",
  "message": "Telegram Mini-App frontend file path"
}
```

#### `get_telegram_backend_url`
Get the URL for the Telegram Mini-App backend API.

**Response:**
```json
{
  "success": true,
  "url": "file:///home/liunix/workspace/robinhood-evm-mcp/telegram_backend.py",
  "message": "Telegram Mini-App backend API file path"
}
```

#### `get_telegram_minapp_health`
Check if the Telegram Mini-App backend is running.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2026-07-20T10:00:00",
    "web3_connected": true
  },
  "message": "Telegram Mini-App backend is running"
}
```

---

## 🔌 Integration with Claude Desktop

### Configuration

Create or edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "robinhood-evm": {
      "command": "python3",
      "args": ["/home/liunix/workspace/robinhood-evm-mcp/mcp_server_with_integration.py"],
      "env": {
        "ROBINHOOD_CHAIN_PRIVATE_KEY": "your_private_key",
        "ROBINHOOD_CHAIN_RPC_URL": "https://your_rpc_url",
        "PYTH_ORACLE_ADDRESS": "0x...",
        "CHAINLINK_ORACLE_ADDRESS": "0x..."
      }
    }
  }
}
```

### Restart Claude Desktop

After updating the configuration, restart Claude Desktop for changes to take effect.

---

## 📊 Testing

### Test Oracles

```bash
python test_pyth_oracle.py
python test_chainlink_oracle.py
python test_unified_oracles.py
```

### Test Staking

```bash
python test_staking_integration.py
```

### Test MCP Server

```bash
python mcp_server_with_integration.py
```

---

## 📝 API Documentation

### Oracles

- **Pyth Network**: https://docs.pyth.network/price-feeds
- **Chainlink Oracles**: https://docs.chain.link/

### Staking Contract

See `contracts/STAKING_README.md` for contract documentation.

### Telegram Mini-App

See `TELEGRAM_MINAPP_README.md` for frontend and backend documentation.

---

## 🐛 Troubleshooting

### Issue: "Session not initialized. Use async context manager."

**Solution**: Ensure you're using `async with UnifiedOracles() as oracles:` in your code.

### Issue: "Staking contract not deployed"

**Solution**: Run `python deploy_staking_complete.py` to deploy the contract.

### Issue: "Cannot fetch prices - API key missing"

**Solution**: Add API keys to `.env` file:
- `PYTH_API_KEY`: Pyth Network API key
- `CHAINLINK_API_KEY`: Chainlink Oracles API key

### Issue: "MCP server not responding"

**Solution**: Check that:
1. Dependencies are installed: `pip install -r requirements.txt`
2. Environment variables are set correctly
3. Claude Desktop is restarted after configuration changes

---

## 📚 Related Documentation

- [Oracles README](oracles/README.md)
- [Staking Contract](contracts/STAKING_README.md)
- [Telegram Mini-App](TELEGRAM_MINAPP_README.md)
- [Test Report](TEST_REPORT.md)

---

## 🎯 Next Steps

1. ✅ Oracles Integration
2. ✅ Staking Contract Integration
3. ✅ Telegram Mini-App Integration
4. ⏳ API Key Configuration
5. ⏳ Contract Deployment
6. ⏳ End-to-End Testing

---

**Status**: 🟡 In Progress
**Last Updated**: 2026-07-20
