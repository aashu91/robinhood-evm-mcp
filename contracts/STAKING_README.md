# Native Token Staking Contract for Robinhood Chain

A native token staking contract with oracle-based yield calculation, integrated with Pyth Network and Chainlink Oracles.

## 🎯 Features

### Core Functionality
- ✅ **Stake native tokens** (ETH/USDG) with automatic reward calculation
- ✅ **Unstake tokens** with rewards claimed automatically
- ✅ **Claim rewards** without unstaking
- ✅ **Oracle-based yield calculation** using Pyth and Chainlink prices
- ✅ **Configurable reward rate** (up to 100% daily)
- ✅ **Emergency withdrawal** for contract owner

### Oracle Integration
- ✅ **Pyth Network** for commodity prices (GOLD, SILVER)
- ✅ **Chainlink Oracles** for stock prices (AAPL, TSLA)
- ✅ **Automatic price fetching** for yield calculation
- ✅ **Price verification** for transaction safety

### Security Features
- ✅ **Owner-only functions** (update reward rate, oracle addresses)
- ✅ **Access control** with modifiers
- ✅ **Emergency withdrawal** for contract owner
- ✅ **Transaction verification** with gas estimation

## 📦 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your values
```

## 🔧 Configuration

### Environment Variables

```env
# Robinhood Chain Configuration
ROBINHOOD_CHAIN_RPC_URL="https://rpc.mainnet.chain.robinhood.com"
ROBINHOOD_CHAIN_PRIVATE_KEY="0x..."

# Oracle Addresses (after deployment)
PYTH_ORACLE_ADDRESS="0x..."
CHAINLINK_ORACLE_ADDRESS="0x..."
STAKING_CONTRACT_ADDRESS="0x..."
```

## 💻 Usage

### Deployment

```bash
# Deploy StakingYield contract
python deploy_staking.py
```

### Staking Tokens

```python
from web3_helper import Web3Helper
from constants import NETWORKS

# Initialize Web3 helper
web3_helper = Web3Helper()
web3_helper.connect()

# Stake 1 ETH/USDG
amount = 1 * 10**18  # 1 in wei
tx_hash = staking_contract.functions.stake(amount).transact({
    "from": account.address,
    "value": amount,
    "gas": 200000
})
```

### Claiming Rewards

```python
# Claim rewards without unstaking
tx_hash = staking_contract.functions.claimRewards().transact({
    "from": account.address,
    "gas": 200000
})
```

### Unstaking Tokens

```python
# Unstake tokens and claim rewards
amount = 1 * 10**18
tx_hash = staking_contract.functions.unstake(amount).transact({
    "from": account.address,
    "gas": 200000
})
```

### Getting User Info

```python
# Get user staking information
staked_amount, pending_rewards = staking_contract.functions.getUserStakingInfo(
    account.address
).call()

print(f"Staked: {staked_amount}")
print(f"Pending Rewards: {pending_rewards}")
```

### Updating Reward Rate

```python
# Update reward rate (only owner)
# 100 = 1% daily rate
new_rate = 50  # 0.5% daily
tx_hash = staking_contract.functions.updateRewardRate(new_rate).transact({
    "from": account.address,
    "gas": 100000
})
```

## 📊 Contract Functions

### External Functions

| Function | Description | Access |
|----------|-------------|--------|
| `stake(uint256 amount)` | Stake native tokens | Public |
| `unstake(uint256 amount)` | Unstake tokens and claim rewards | Staked |
| `claimRewards()` | Claim rewards without unstaking | Staked |
| `getGoldPrice()` | Get gold price from Pyth | View |
| `getSilverPrice()` | Get silver price from Chainlink | View |
| `calculateReward(address user)` | Calculate pending reward | View |
| `getUserStakingInfo(address user)` | Get user staking info | View |
| `updateRewardRate(uint256 newRate)` | Update reward rate | Owner |
| `updateOracleAddresses(...)` | Update oracle addresses | Owner |
| `emergencyWithdraw()` | Emergency withdraw (owner) | Owner |

### View Functions

| Function | Description |
|----------|-------------|
| `getContractBalance()` | Get contract balance |
| `getTotalRewards()` | Get total rewards distributed |
| `getRewardRate()` | Get current reward rate |
| `getUserRewardDebt(address user)` | Get user reward debt |

## 🧪 Testing

```bash
# Run tests
python test_staking.py
```

### Test Coverage

- ✅ Get contract info
- ✅ Stake tokens
- ✅ Get user staking info
- ✅ Claim rewards
- ✅ Unstake tokens
- ✅ Update reward rate

## 📚 Integration with MCP Server

Integrate StakingYield into `mcp_server.py`:

```python
from contracts.StakingYield import StakingYield

async def stake_native_token(amount: int):
    """MCP tool: Stake native tokens"""
    tx_hash = staking_contract.functions.stake(amount).transact({
        "from": account.address,
        "value": amount,
        "gas": 200000
    })
    return {"tx_hash": web3_helper.w3.to_hex(tx_hash)}

async def claim_staking_rewards():
    """MCP tool: Claim staking rewards"""
    tx_hash = staking_contract.functions.claimRewards().transact({
        "from": account.address,
        "gas": 200000
    })
    return {"tx_hash": web3_helper.w3.to_hex(tx_hash)}
```

## 📄 Smart Contract Details

### Staking Logic

```solidity
// Reward calculation
userRewardDebt = userStakedAmount * rewardRate / 100

// Pending rewards
pendingRewards = currentRewardDebt - userRewardDebt
```

### Oracle Integration

- **Gold Price**: Pyth Network (low-latency)
- **Silver Price**: Chainlink Oracles (high-reliability)
- **Stock Prices**: Chainlink Oracles

## 🔒 Security Considerations

1. **Owner Control**: Owner can update reward rates and oracle addresses
2. **Emergency Withdraw**: Owner can withdraw all funds in emergencies
3. **Access Control**: Only staked users can unstake/claim
4. **Gas Estimation**: All transactions are gas-estimated before sending

## 📈 Example Workflow

```
1. User stakes 1 ETH/USDG
   → StakingYield contract receives 1 ETH/USDG
   → Reward debt is calculated: 1 * 100 / 100 = 1

2. After 1 day
   → Reward debt updates: 1 * 100 / 100 = 1
   → Pending rewards: 1 - previous_debt = 0.01 (1%)

3. User claims rewards
   → User receives: staked_amount + pending_rewards
   → Contract balance decreases by pending_rewards
```

## 🤝 Contributing

This is part of the Robinhood Chain EVM MCP Server project. See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## 📄 License

MIT License - See [LICENSE](../LICENSE) file for details.
