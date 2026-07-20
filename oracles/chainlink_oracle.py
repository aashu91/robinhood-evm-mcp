#!/usr/bin/env python3
"""
Chainlink Oracles Integration for Robinhood Chain
Provides reliable external data feeds (prices, weather, sports results, etc.)
"""

import os
import asyncio
import aiohttp
from typing import Dict, Optional, Any
from datetime import datetime
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChainlinkOracle:
    """Chainlink Oracle Client"""
    
    # Chainlink Data Feeds (example endpoints - need actual feed IDs for Robinhood Chain)
    CHAINLINK_DATA_FEEDS = {
        "GOLD": {
            "id": "0x0000000000000000000000000000000000000000000000000000000000000000",  # 需要更新为实际ID
            "description": "Gold price feed (USD per ounce)"
        },
        "SILVER": {
            "id": "0x0000000000000000000000000000000000000000000000000000000000000000",  # 需要更新为实际ID
            "description": "Silver price feed (USD per ounce)"
        },
        "AAPL": {
            "id": "0x0000000000000000000000000000000000000000000000000000000000000000",  # 需要更新为实际ID
            "description": "Apple Inc. stock price feed"
        },
        "TSLA": {
            "id": "0x0000000000000000000000000000000000000000000000000000000000000000",  # 需要更新为实际ID
            "description": "Tesla Inc. stock price feed"
        }
    }
    
    # Chainlink Automation API endpoints
    CHAINLINK_AUTOMATION_API = "https://automation.chain.link/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Chainlink Oracle
        
        Args:
            api_key: Chainlink API key (optional)
        """
        self.api_key = api_key or os.getenv("CHAINLINK_API_KEY")
        self.session = None
        self.current_prices = {}
        
        # Load feed IDs from config
        self._load_feed_ids()
    
    def _load_feed_ids(self):
        """Load price feed IDs from config file"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), "chainlink_feeds.json")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = json.load(f)
                    for ticker, feed_id in config.items():
                        if ticker in self.CHAINLINK_DATA_FEEDS:
                            self.CHAINLINK_DATA_FEEDS[ticker]["id"] = feed_id
                    logger.info(f"Loaded Chainlink feed IDs: {config}")
        except Exception as e:
            logger.warning(f"Failed to load feed IDs from config: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def get_price_from_chainlink(self, feed_id: str) -> Dict[str, Any]:
        """
        Get price from Chainlink Data Feed
        
        Args:
            feed_id: Chainlink feed ID
            
        Returns:
            Price data including value, round ID, and timestamp
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        # Chainlink Data Feed API endpoint
        endpoint = f"{self.CHAINLINK_AUTOMATION_API}/price/{feed_id}"
        
        try:
            async with self.session.get(
                endpoint,
                headers=await self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Chainlink API error: {response.status} - {error_text}")
                    return {"error": f"API error {response.status}", "status": "failed"}
                
                data = await response.json()
                
                # Extract price information
                price_data = {
                    "value": float(data.get("value", 0)),
                    "round_id": data.get("round_id", 0),
                    "updated_at": data.get("updated_at", datetime.utcnow().isoformat()),
                    "status": "success"
                }
                
                logger.info(f"Chainlink price fetched: {price_data}")
                return price_data
                
        except asyncio.TimeoutError:
            logger.error("Chainlink API timeout")
            return {"error": "Timeout", "status": "failed"}
        except Exception as e:
            logger.error(f"Chainlink API request failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_price_by_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Get price for a specific ticker symbol
        
        Args:
            ticker: Ticker symbol (e.g., "GOLD", "SILVER", "AAPL", "TSLA")
            
        Returns:
            Price data for the ticker
        """
        ticker = ticker.upper()
        
        if ticker not in self.CHAINLINK_DATA_FEEDS:
            return {
                "error": f"Ticker {ticker} not supported",
                "status": "failed",
                "supported_tickers": list(self.CHAINLINK_DATA_FEEDS.keys())
            }
        
        feed_id = self.CHAINLINK_DATA_FEEDS[ticker]["id"]
        logger.info(f"Fetching {ticker} price from Chainlink...")
        
        return await self.get_price_from_chainlink(feed_id)
    
    async def get_multiple_prices(self, tickers: list) -> Dict[str, Any]:
        """
        Get prices for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dict with price data for all tickers
        """
        tasks = [self.get_price_by_ticker(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        
        return {
            ticker: results[i]
            for i, ticker in enumerate(tickers)
        }
    
    async def get_chainlink_data_feeds(self) -> Dict[str, Any]:
        """
        Get all available Chainlink Data Feeds
        
        Returns:
            Dict with all configured feeds and their status
        """
        feeds_info = {}
        
        for ticker, feed_info in self.CHAINLINK_DATA_FEEDS.items():
            price = await self.get_price_by_ticker(ticker)
            feeds_info[ticker] = {
                "feed_id": feed_info["id"],
                "description": feed_info["description"],
                "price": price
            }
        
        return {
            "feeds": feeds_info,
            "timestamp": datetime.utcnow().isoformat()
        }


# 单例模式
_chainlink_oracle_instance = None

def get_chainlink_oracle(api_key: Optional[str] = None) -> ChainlinkOracle:
    """Get singleton Chainlink Oracle instance"""
    global _chainlink_oracle_instance
    if _chainlink_oracle_instance is None:
        _chainlink_oracle_instance = ChainlinkOracle(api_key=api_key)
    return _chainlink_oracle_instance


if __name__ == "__main__":
    # 测试代码
    async def test_chainlink_oracle():
        async with ChainlinkOracle() as oracle:
            print("=== Testing Chainlink Oracle ===")
            
            # 测试AAPL价格
            aapl = await oracle.get_price_by_ticker("AAPL")
            print(f"\nAAPL Price: {aapl}")
            
            # 测试TSLA价格
            tsla = await oracle.get_price_by_ticker("TSLA")
            print(f"\nTSLA Price: {tsla}")
            
            # 测试多个价格
            prices = await oracle.get_multiple_prices(["GOLD", "SILVER", "AAPL", "TSLA"])
            print(f"\n=== All Prices ===")
            print(json.dumps(prices, indent=2, default=str))
    
    asyncio.run(test_chainlink_oracle())
