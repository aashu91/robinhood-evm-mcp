#!/usr/bin/env python3
"""
Telegram Mini-App Backend API
FastAPI server for Telegram Mini-App integration
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from web3 import Web3
from web3_helper import Web3Helper

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oracles.unified_oracles import get_unified_oracles

# Initialize FastAPI
app = FastAPI(
    title="Robinhood Staking API",
    description="API for Telegram Mini-App - Staking, Oracles, and Rewards",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# Models
class StakeRequest(BaseModel):
    amount: int
    userAddress: str


class ClaimRequest(BaseModel):
    userAddress: str


class UnstakeRequest(BaseModel):
    amount: int
    userAddress: str


class PriceHistoryRequest(BaseModel):
    ticker: str
    hours: int = 24


# Initialize Web3 Helper
web3_helper = Web3Helper()
web3_helper.connect()

# Load Staking Contract
try:
    contract_path = os.path.join(
        os.path.dirname(__file__),
        "contracts",
        "StakingYield.json"
    )

    if os.path.exists(contract_path):
        with open(contract_path, "r") as f:
            contract_abi = json.load(f)

        staking_contract = web3_helper.w3.eth.contract(
            address=web3_helper.w3.to_checksum_address(os.getenv("STAKING_CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")),
            abi=contract_abi
        )
    else:
        staking_contract = None
        print("⚠️  Staking contract not found. Run deploy_staking.py first.")
except Exception as e:
    print(f"⚠️  Failed to load staking contract: {e}")
    staking_contract = None

# Initialize Unified Oracles
async def get_oracles():
    """Get oracle instance"""
    async with get_unified_oracles() as oracles:
        return oracles


# API Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "web3_connected": web3_helper.w3.is_connected()
    }


@app.get("/api/prices")
async def get_prices():
    """Get current commodity and stock prices"""
    try:
        oracles = await get_oracles()

        # Get gold price
        gold = await oracles.get_gold_price()

        # Get silver price
        silver = await oracles.get_silver_price()

        # Get AAPL price
        aapl = await oracles.get_price_by_ticker("AAPL")

        # Get TSLA price
        tsla = await oracles.get_price_by_ticker("TSLA")

        return {
            "gold": gold,
            "silver": silver,
            "aapl": aapl,
            "tsla": tsla,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prices/history")
async def get_price_history(ticker: str = "GOLD", hours: int = 24):
    """Get price history for a ticker"""
    try:
        oracles = await get_oracles()

        # Generate historical data
        prices = []
        labels = []

        base_time = datetime.utcnow()
        for i in range(hours):
            time = base_time - timedelta(hours=hours - i)
            labels.append(time.isoformat())

            # Fetch current price (simplified - in real app, would fetch historical)
            price_data = await oracles.get_price_by_ticker(ticker)
            price = price_data.get("value") or price_data.get("price", 0)
            prices.append(float(price))

        return {
            "ticker": ticker,
            "labels": labels,
            "prices": prices,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/staking/{user_address}")
async def get_staking_info(user_address: str):
    """Get user staking information"""
    if not staking_contract:
        raise HTTPException(status_code=503, detail="Staking contract not available")

    try:
        staked_amount, pending_rewards = staking_contract.functions.getUserStakingInfo(
            web3_helper.w3.to_checksum_address(user_address)
        ).call()

        total_rewards = staking_contract.functions.getTotalRewards().call()
        reward_rate = staking_contract.functions.getRewardRate().call()
        contract_balance = staking_contract.functions.getContractBalance().call()

        return {
            "stakedAmount": staked_amount,
            "pendingRewards": pending_rewards,
            "totalRewards": total_rewards,
            "rewardRate": reward_rate,
            "contractBalance": contract_balance,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stake")
async def stake_tokens(request: StakeRequest):
    """Stake tokens"""
    if not staking_contract:
        raise HTTPException(status_code=503, detail="Staking contract not available")

    try:
        tx_hash = staking_contract.functions.stake(request.amount).transact({
            "from": web3_helper.w3.to_checksum_address(request.userAddress),
            "value": request.amount,
            "gas": 200000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "success": True,
            "tx_hash": web3_helper.w3.to_hex(tx_hash),
            "tx_receipt": {
                "status": tx_receipt.status,
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/claim")
async def claim_rewards(request: ClaimRequest):
    """Claim rewards"""
    if not staking_contract:
        raise HTTPException(status_code=503, detail="Staking contract not available")

    try:
        tx_hash = staking_contract.functions.claimRewards().transact({
            "from": web3_helper.w3.to_checksum_address(request.userAddress),
            "gas": 200000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "success": True,
            "tx_hash": web3_helper.w3.to_hex(tx_hash),
            "tx_receipt": {
                "status": tx_receipt.status,
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/unstake")
async def unstake_tokens(request: UnstakeRequest):
    """Unstake tokens"""
    if not staking_contract:
        raise HTTPException(status_code=503, detail="Staking contract not available")

    try:
        tx_hash = staking_contract.functions.unstake(request.amount).transact({
            "from": web3_helper.w3.to_checksum_address(request.userAddress),
            "gas": 200000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "success": True,
            "tx_hash": web3_helper.w3.to_hex(tx_hash),
            "tx_receipt": {
                "status": tx_receipt.status,
                "gas_used": tx_receipt.gasUsed,
                "block_number": tx_receipt.blockNumber
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reward-rate")
async def get_reward_rate():
    """Get current reward rate"""
    if not staking_contract:
        raise HTTPException(status_code=503, detail="Staking contract not available")

    try:
        reward_rate = staking_contract.functions.getRewardRate().call()
        return {
            "rewardRate": reward_rate,
            "rate_percent": reward_rate / 100,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/update-reward-rate")
async def update_reward_rate(rate: int):
    """Update reward rate (admin only)"""
    if not staking_contract:
        raise HTTPException(status_code=503, detail="Staking contract not available")

    try:
        tx_hash = staking_contract.functions.updateRewardRate(rate).transact({
            "gas": 100000
        })

        tx_receipt = web3_helper.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

        return {
            "success": True,
            "tx_hash": web3_helper.w3.to_hex(tx_hash),
            "new_rate": rate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contract-balance")
async def get_contract_balance():
    """Get contract balance"""
    if not staking_contract:
        raise HTTPException(status_code=503, detail="Staking contract not available")

    try:
        balance = staking_contract.functions.getContractBalance().call()
        return {
            "balance": balance,
            "balance_eth": web3_helper.w3.from_wei(balance, 'ether')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
