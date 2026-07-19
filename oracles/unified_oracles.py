#!/usr/bin/env python3
"""
Unified Oracles Integration for Robinhood Chain
Combines Pyth Network (low-latency) and Chainlink Oracles (high-reliability)
"""

import asyncio
from typing import Dict, Optional, Any
from pyth_oracle import PythOracle
from chainlink_oracle import ChainlinkOracle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedOracles:
    """Unified Oracle Client combining Pyth and Chainlink"""
    
    def __init__(
        self,
        pyth_api_key: Optional[str] = None,
        pyth_use_pro: bool = True,
        chainlink_api_key: Optional[str] = None
    ):
        """
        Initialize Unified Oracles
        
        Args:
            pyth_api_key: Pyth Pro API key (optional for Pyth Core)
            pyth_use_pro: Use Pyth Pro (requires API key) or Pyth Core (free)
            chainlink_api_key: Chainlink API key (optional)
        """
        self.pyth_oracle = PythOracle(api_key=pyth_api_key, use_pro=pyth_use_pro)
        self.chainlink_oracle = ChainlinkOracle(api_key=chainlink_api_key)
        self.current_prices = {}
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass
    
    async def get_gold_price(self) -> Dict[str, Any]:
        """
        Get gold price from Pyth Network (low-latency)
        
        Returns:
            Price data with price, confidence, and timestamp
        """
        logger.info("Fetching gold price from Pyth Network...")
        result = await self.pyth_oracle.get_gold_price()
        
        if result.get("status") == "success":
            self.current_prices["GOLD"] = result
            return result
        else:
            logger.warning(f"Pyth Network failed, trying Chainlink...")
            return await self.chainlink_oracle.get_price_by_ticker("GOLD")
    
    async def get_silver_price(self) -> Dict[str, Any]:
        """
        Get silver price from Pyth Network (low-latency)
        
        Returns:
            Price data with price, confidence, and timestamp
        """
        logger.info("Fetching silver price from Pyth Network...")
        result = await self.pyth_oracle.get_silver_price()
        
        if result.get("status") == "success":
            self.current_prices["SILVER"] = result
            return result
        else:
            logger.warning(f"Pyth Network failed, trying Chainlink...")
            return await self.chainlink_oracle.get_price_by_ticker("SILVER")
    
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
            "timestamp": asyncio.get_event_loop().time()
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
        
        if ticker in ["GOLD", "SILVER"]:
            # Use Pyth Network for commodities (low-latency)
            return await self.get_commodity_prices()
        else:
            # Use Chainlink for other tickers (high-reliability)
            return await self.chainlink_oracle.get_price_by_ticker(ticker)
    
    async def get_all_prices(self) -> Dict[str, Any]:
        """
        Get prices for all supported tickers
        
        Returns:
            Dict with prices for all supported tickers
        """
        tickers = ["GOLD", "SILVER", "AAPL", "TSLA"]
        tasks = [self.get_price_by_ticker(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks)
        
        return {
            ticker: results[i]
            for i, ticker in enumerate(tickers)
        }


# 单例模式
_unified_oracles_instance = None

def get_unified_oracles(
    pyth_api_key: Optional[str] = None,
    pyth_use_pro: bool = True,
    chainlink_api_key: Optional[str] = None
) -> UnifiedOracles:
    """Get singleton Unified Oracles instance"""
    global _unified_oracles_instance
    if _unified_oracles_instance is None:
        _unified_oracles_instance = UnifiedOracles(
            pyth_api_key=pyth_api_key,
            pyth_use_pro=pyth_use_pro,
            chainlink_api_key=chainlink_api_key
        )
    return _unified_oracles_instance


if __name__ == "__main__":
    # 测试代码
    async def test_unified_oracles():
        async with UnifiedOracles() as oracles:
            print("=== Testing Unified Oracles ===")
            
            # 测试黄金价格
            gold = await oracles.get_gold_price()
            print(f"\nGold Price: {gold}")
            
            # 测试白银价格
            silver = await oracles.get_silver_price()
            print(f"\nSilver Price: {silver}")
            
            # 测试商品价格
            prices = await oracles.get_commodity_prices()
            print(f"\n=== All Commodity Prices ===")
            print(f"Gold: {prices['gold']}")
            print(f"Silver: {prices['silver']}")
            
            # 测试股票价格
            aapl = await oracles.get_price_by_ticker("AAPL")
            print(f"\nAAPL Price: {aapl}")
    
    asyncio.run(test_unified_oracles())
