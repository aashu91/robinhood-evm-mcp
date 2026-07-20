# Oracles Integration for Robinhood Chain

Unified oracle integration combining **Pyth Network** (low-latency) and **Chainlink Oracles** (high-reliability) for Robinhood Chain.

## 🎯 Features

### Pyth Network
- ✅ Real-time gold and silver prices
- ✅ Low-latency price updates (sub-second)
- ✅ High-precision price feeds
- ✅ Pyth Pro (paid) or Pyth Core (free)

### Chainlink Oracles
- ✅ Reliable external data feeds
- ✅ Multiple data types (prices, weather, sports, etc.)
- ✅ Multi-source verification
- ✅ Industry-standard oracle network

### Unified Oracles
- ✅ Automatic failover between Pyth and Chainlink
- ✅ Single API for both oracle networks
- ✅ Support for commodities (GOLD, SILVER) and stocks (AAPL, TSLA)
- ✅ Async/await for high performance

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

Create a `.env` file in your project root:

```env
# Pyth Network (optional for Pyth Core)
PYTH_API_KEY="your_pyth_api_key_here"

# Chainlink Oracles (optional)
CHAINLINK_API_KEY="your_chainlink_api_key_here"
```

## 💻 Usage

### Basic Usage

```python
import asyncio
from oracles.unified_oracles import get_unified_oracles

async def main():
    async with get_unified_oracles() as oracles:
        # Get gold price
        gold = await oracles.get_gold_price()
        print(f"Gold: ${gold['price']}")
        
        # Get silver price
        silver = await oracles.get_silver_price()
        print(f"Silver: ${silver['price']}")
        
        # Get stock price
        aapl = await oracles.get_price_by_ticker("AAPL")
        print(f"AAPL: ${aapl['value']}")

asyncio.run(main())
```

### Advanced Usage

```python
async with get_unified_oracles() as oracles:
    # Get all commodity prices
    commodities = await oracles.get_commodity_prices()
    print(f"Gold: {commodities['gold']}")
    print(f"Silver: {commodities['silver']}")
    
    # Get all prices
    all_prices = await oracles.get_all_prices()
    print(f"All prices: {all_prices}")
```

## 📊 Supported Tickers

| Ticker | Source | Description |
|--------|--------|-------------|
| `GOLD` | Pyth Network | Gold price (USD/oz) |
| `SILVER` | Pyth Network | Silver price (USD/oz) |
| `AAPL` | Chainlink | Apple stock price |
| `TSLA` | Chainlink | Tesla stock price |

## 🔌 Integration with MCP Server

The oracles can be integrated into the existing `mcp_server.py`:

```python
from oracles.unified_oracles import get_unified_oracles

async def get_gold_price(address, token_address=None):
    """MCP tool: Get gold price from Pyth Network"""
    async with get_unified_oracles() as oracles:
        return await oracles.get_gold_price()
```

## 📝 API Reference

### `get_gold_price()`
Get current gold price (USD per ounce).

**Returns:** `Dict[str, Any]` with keys:
- `price`: float
- `confidence`: float
- `exponent`: int
- `timestamp`: str
- `status`: str

### `get_silver_price()`
Get current silver price (USD per ounce).

**Returns:** `Dict[str, Any]` (same format as `get_gold_price()`)

### `get_commodity_prices()`
Get both gold and silver prices.

**Returns:** `Dict[str, Any]` with:
- `gold`: Dict
- `silver`: Dict
- `timestamp`: float

### `get_price_by_ticker(ticker)`
Get price for a specific ticker.

**Args:**
- `ticker`: str (e.g., "GOLD", "SILVER", "AAPL", "TSLA")

**Returns:** `Dict[str, Any]` with price data

### `get_all_prices()`
Get prices for all supported tickers.

**Returns:** `Dict[str, Dict]` with all prices

## 🚀 Testing

Run the test suite:

```bash
# Test Pyth Oracle
cd oracles && python pyth_oracle.py

# Test Chainlink Oracle
cd oracles && python chainlink_oracle.py

# Test Unified Oracles
cd oracles && python unified_oracles.py
```

## 📚 Documentation

- [Pyth Network Documentation](https://docs.pyth.network/)
- [Chainlink Oracles Documentation](https://docs.chain.link/)
- [MCP Server Integration](../mcp_server.py)

## 🤝 Contributing

This is part of the Robinhood Chain EVM MCP Server project. See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## 📄 License

MIT License - See [LICENSE](../LICENSE) file for details.
