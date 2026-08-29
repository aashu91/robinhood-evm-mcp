# constants.py
# Constants and default configurations for Robinhood Chain EVM Web3 MCP Server

NETWORKS = {
    "robinhood-mainnet": {
        "name": "Robinhood Chain Mainnet",
        "rpc_url": "https://rpc.mainnet.chain.robinhood.com",
        "chain_id": 4663,
        "symbol": "ETH",
        "explorer": "https://robinhoodchain.blockscout.com"
    },
    "robinhood-testnet": {
        "name": "Robinhood Chain Testnet",
        "rpc_url": "https://rpc.testnet.chain.robinhood.com",
        "chain_id": 46630,
        "symbol": "ETH",
        "explorer": "https://explorer.testnet.chain.robinhood.com"
    },
    "localhost": {
        "name": "Localhost Anvil/Hardhat",
        "rpc_url": "http://127.0.0.1:8545",
        "chain_id": 31337,
        "symbol": "ETH",
        "explorer": ""
    }
}

DEFAULT_NETWORK = "robinhood-mainnet"

# Canonical token addresses on Robinhood Chain Mainnet
TICKER_MAPPINGS = {
    # Stablecoin
    "USDG": "0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168",
    # Tokenized stocks/ETFs
    "AAPL": "0xaF3D76f1834A1d425780943C99Ea8A608f8a93f9",
    "TSLA": "0x322F0929c4625eD5bAd873c95208D54E1c003b2d",
    # Native Launchpad & Utility Token
    "ROBIN_MCP": "0xCFD635f82B75ab6c1a6725a54e9146FEe2c5A421",
    # Add common fallback testnet mocks here if needed
}

# Simple ABIs for standard ERC20 & swap integrations
PREPACKAGED_ABIS = {
    "ERC20": [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
            "name": "transfer",
            "outputs": [{"name": "success", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}],
            "name": "approve",
            "outputs": [{"name": "success", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_from", "type": "address"},
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transferFrom",
            "outputs": [{"name": "success", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {"name": "_owner", "type": "address"},
                {"name": "_spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"name": "remaining", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        }
    ],
    # Placeholder for standard USDG Earn/Lending contract functions
    "USDG_EARN": [
        {
            "inputs": [{"name": "amount", "type": "uint256"}],
            "name": "deposit",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "amount", "type": "uint256"}],
            "name": "withdraw",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "claimYield",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ],
    "MemeFactory": [
        {
            "inputs": [
                {"name": "name", "type": "string"},
                {"name": "symbol", "type": "string"},
                {"name": "supply", "type": "uint256"}
            ],
            "name": "deployMemeToken",
            "outputs": [{"name": "", "type": "address"}],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getMemeCount",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "", "type": "uint256"}],
            "name": "allMemeTokens",
            "outputs": [{"name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "tokenAddress", "type": "address"}],
            "name": "buyMemeToken",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [{"name": "", "type": "address"}],
            "name": "pools",
            "outputs": [
                {"name": "tokenAddress", "type": "address"},
                {"name": "tokenReserves", "type": "uint256"},
                {"name": "ethReserves", "type": "uint256"},
                {"name": "tradingActive", "type": "bool"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"name": "tokenAddress", "type": "address"},
                {"name": "tokenAmount", "type": "uint256"}
            ],
            "name": "sellMemeToken",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ],
    "StakingYield": [
        {
            "inputs": [{"name": "amount", "type": "uint256"}],
            "name": "stake",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "amount", "type": "uint256"}],
            "name": "unstake",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "claimRewards",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "claimReward",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "emergencyUnstake",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "depositRewards",
            "outputs": [],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [{"name": "account", "type": "address"}],
            "name": "getPendingReward",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "account", "type": "address"}],
            "name": "getStakingInfo",
            "outputs": [
                {"name": "userStaked", "type": "uint256"},
                {"name": "userPendingReward", "type": "uint256"},
                {"name": "poolTotalStaked", "type": "uint256"},
                {"name": "totalPoolRewards", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "totalStaked",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "", "type": "address"}],
            "name": "stakedBalance",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "rewardIndex",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "", "type": "address"}],
            "name": "userRewardIndex",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "", "type": "address"}],
            "name": "accumulatedRewards",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "totalRewardsDeposited",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "totalRewardsClaimed",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "stakingToken",
            "outputs": [{"name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
}
