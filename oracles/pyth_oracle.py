#!/usr/bin/env python3
"""
Pyth Network Oracle Integration for Robinhood Chain
Provides real-time gold and silver prices via Pyth Network
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Optional, Any
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PythOracle:
    """Pyth Network Oracle Client"""
    
    # Pyth Network Hermes API endpoints
    PYTH_PROD_URL = "https://hermes.pyth.network"
    PYTH_PRO_URL = "https://pyth.dourolabs.app/hermes"
    
    # Gold and Silver price feed IDs (Pyth Pro)
    GOLD_FEED_ID = "0x0000000000000000000000000000000000000000000000000000000000000000"  # 需要更新为实际ID
    SILVER_FEED_ID = "0x0000000000000000000000000000000000000000000000000000000000000000"  # 需要更新为实际ID
    
    def __init__(self, api_key: Optional[str] = None, use_pro: bool = True):
        """
        Initialize Pyth Oracle
        
        Args:
            api_key: Pyth Pro API key (optional for Pyth Core)
            use_pro: Use Pyth Pro (requires API key) or Pyth Core (free)
        """
        self.api_key = api_key or os.getenv("PYTH_API_KEY")
        self.use_pro = use_pro
        self.session = None
        self.current_prices = {}
        
        # Set endpoint
        self.endpoint = self.PYTH_PRO_URL if use_pro else self.PYTH_PROD_URL
        
        # Load price feed IDs from config
        self._load_feed_ids()
    
    def _load_feed_ids(self):
        """Load price feed IDs from config file"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), "pyth_feeds.json")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = json.load(f)
                    self.GOLD_FEED_ID = config.get("gold_feed_id", self.GOLD_FEED_ID)
                    self.SILVER_FEED_ID = config.get("silver_feed_id", self.SILVER_FEED_ID)
                    logger.info(f"Loaded price feed IDs: {config}")
        except Exception as e:
            logger.warning(f"Failed to load feed IDs from config: {e}")
            logger.info("Using default feed IDs")
    
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
    
    async def get_latest_price_updates(self, price_ids: list) -> Dict[str, Any]:
        """
        Fetch latest price updates from Pyth Network
        
        Args:
            price_ids: List of price feed IDs
            
        Returns:
            Price updates including price, confidence, and timestamp
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        endpoint = f"{self.endpoint}/latest-price-feeds"
        payload = {"ids": price_ids}
        
        try:
            async with self.session.post(
                endpoint,
                json=payload,
                headers=await self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Pyth API error: {response.status} - {error_text}")
                    return {"error": f"API error {response.status}", "status": "failed"}
                
                data = await response.json()
                return {
                    "status": "success",
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except asyncio.TimeoutError:
            logger.error("Pyth API timeout")
            return {"error": "Timeout", "status": "failed"}
        except Exception as e:
            logger.error(f"Pyth API request failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_gold_price(self) -> Dict[str, Any]:
        """Get current gold price (USD per ounce)"""
        logger.info(f"Fetching gold price from Pyth Network...")
        
        result = await self.get_latest_price_updates([self.GOLD_FEED_ID])
        
        if result.get("status") == "success":
            price_data = result["data"].get("price_feeds", [])
            if price_data:
                feed = price_data[0]
                price = float(feed.get("price", 0))
                conf = float(feed.get("conf", 0))
                expo = int(feed.get("expo", 0))
                
                self.current_prices["GOLD"] = {
                    "price": price,
                    "confidence": conf,
                    "exponent": expo,
                    "timestamp": result["timestamp"],
                    "status": "success"
                }
                logger.info(f"Gold price: ${price:,.2f} ± {conf:.4f}")
                return self.current_prices["GOLD"]
        
        return {"error": result.get("error", "Unknown error"), "status": "failed"}
    
    async def get_silver_price(self) -> Dict[str, Any]:
        """Get current silver price (USD per ounce)"""
        logger.info(f"Fetching silver price from Pyth Network...")
        
        result = await self.get_latest_price_updates([self.SILVER_FEED_ID])
        
        if result.get("status") == "success":
            price_data = result["data"].get("price_feeds", [])
            if price_data:
                feed = price_data[0]
                price = float(feed.get("price", 0))
                conf = float(feed.get("conf", 0))
                expo = int(feed.get("expo", 0))
                
                self.current_prices["SILVER"] = {
                    "price": price,
                    "confidence": conf,
                    "exponent": expo,
                    "timestamp": result["timestamp"],
                    "status": "success"
                }
                logger.info(f"Silver price: ${price:,.2f} ± {conf:.4f}")
                return self.current_prices["SILVER"]
        
        return {"error": result.get("error", "Unknown error"), "status": "failed"}
    
    async def get_commodity_prices(self) -> Dict[str, Any]:
        """
        Get both gold and silver prices
        
        Returns:
            Dict with gold and silver price data
        """
        gold_task = self.get_gold_price()
        silver_task = self.get_silver_price()
        
        gold_result, silver_result = await asyncio.gather(gold_task, silver_task)
        
        return {
            "gold": gold_result,
            "silver": silver_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_price_by_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Get price for a specific ticker symbol
        
        Args:
            ticker: Ticker symbol (e.g., "GOLD", "SILVER", "AAPL", "TSLA")
            
        Returns:
            Price data for the ticker
        """
        ticker = ticker.upper()
        
        if ticker == "GOLD":
            return await self.get_gold_price()
        elif ticker == "SILVER":
            return await self.get_silver_price()
        else:
            # For other tickers, use Chainlink Oracles
            from chainlink_oracle import ChainlinkOracle
            chainlink = ChainlinkOracle()
            return await chainlink.get_price_by_ticker(ticker)


# 单例模式
_pyth_oracle_instance = None

def get_pyth_oracle(api_key: Optional[str] = None, use_pro: bool = True) -> PythOracle:
    """Get singleton Pyth Oracle instance"""
    global _pyth_oracle_instance
    if _pyth_oracle_instance is None:
        _pyth_oracle_instance = PythOracle(api_key=api_key, use_pro=use_pro)
    return _pyth_oracle_instance


if __name__ == "__main__":
    # 测试代码
    async def test_pyth_oracle():
        async with PythOracle(use_pro=True) as oracle:
            print("=== Testing Pyth Oracle ===")
            
            # 测试黄金价格
            gold = await oracle.get_gold_price()
            print(f"\nGold Price: {gold}")
            
            # 测试白银价格
            silver = await oracle.get_silver_price()
            print(f"\nSilver Price: {silver}")
            
            # 测试商品价格
            prices = await oracle.get_commodity_prices()
            print(f"\n=== All Commodity Prices ===")
            print(json.dumps(prices, indent=2, default=str))
    
    asyncio.run(test_pyth_oracle())
