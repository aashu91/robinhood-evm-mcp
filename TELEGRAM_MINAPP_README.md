# Telegram Mini-App for Robinhood Staking

A full-stack Telegram Mini-App for native token staking with oracle-based yield calculation.

## 🎯 Features

### Frontend (HTML/JS)
- ✅ **Real-time prices** from Pyth Network and Chainlink Oracles
- ✅ **Staking dashboard** with stats and charts
- ✅ **Stake/Unstake/Claim** functionality
- ✅ **Interactive charts** using Chart.js
- ✅ **Telegram WebApp integration**
- ✅ **Responsive design** with dark theme
- ✅ **Notifications** for user feedback

### Backend (FastAPI)
- ✅ **REST API** for frontend-backend communication
- ✅ **Staking contract integration**
- ✅ **Oracle price fetching**
- ✅ **Transaction management**
- ✅ **Error handling** and logging
- ✅ **CORS support** for development

## 📦 Architecture

```
Telegram Mini-App
├── telegram_minapp.html (Frontend)
│   ├── HTML Structure
│   ├── CSS Styling
│   └── JavaScript Logic
│
└── telegram_backend.py (Backend)
    ├── FastAPI Server
    ├── Oracle Integration
    └── Staking Contract Integration
```

## 💻 Installation

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- Robinhood Chain RPC endpoint
- Staking contract deployed

### Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**

```env
# Robinhood Chain
ROBINHOOD_CHAIN_RPC_URL="https://rpc.mainnet.chain.robinhood.com"
ROBINHOOD_CHAIN_PRIVATE_KEY="0x..."

# Staking Contract
STAKING_CONTRACT_ADDRESS="0x..."
PYTH_ORACLE_ADDRESS="0x..."
CHAINLINK_ORACLE_ADDRESS="0x..."
```

3. **Deploy Staking Contract:**

```bash
python deploy_staking.py
```

4. **Start Backend Server:**

```bash
python telegram_backend.py
```

5. **Open Telegram Mini-App:**

```bash
# Using ngrok (for testing)
ngrok http 8000

# Then open the HTML file in browser
open telegram_minapp.html
```

## 🚀 Usage

### Starting the Backend

```bash
# Start FastAPI server
python telegram_backend.py

# Server will start on http://0.0.0.0:8000
```

### Frontend Features

#### Dashboard
- View real-time prices (GOLD, SILVER, AAPL, TSLA)
- Check staking stats (staked amount, pending rewards, total rewards)
- Monitor contract balance

#### Stake Tokens
1. Enter amount in ETH/USDG
2. Click "Stake Tokens"
3. Confirm transaction in Telegram

#### Claim Rewards
1. Click "Claim Rewards"
2. Rewards will be transferred to your wallet

#### Unstake Tokens
1. Enter amount in ETH/USDG
2. Click "Unstake Tokens"
3. Tokens + rewards will be transferred

#### Price Chart
- View historical gold price chart
- Real-time updates
- Interactive zoom and pan

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/prices` | Get current prices |
| GET | `/api/prices/history` | Get price history |
| GET | `/api/staking/{user_address}` | Get user staking info |
| POST | `/api/stake` | Stake tokens |
| POST | `/api/claim` | Claim rewards |
| POST | `/api/unstake` | Unstake tokens |
| GET | `/api/reward-rate` | Get reward rate |
| POST | `/api/update-reward-rate` | Update reward rate (admin) |
| GET | `/api/contract-balance` | Get contract balance |

## 🎨 Frontend Customization

### Colors
Edit the CSS variables in `telegram_minapp.html`:

```css
--primary-color: #00d4ff;
--secondary-color: #7c3aed;
--background-gradient: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
```

### API Base URL
Edit the API base URL in the JavaScript:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Chart Configuration
Edit the Chart.js configuration in the `<script>` tag:

```javascript
goldChart.data.labels = [...];
goldChart.data.datasets[0].data = [...];
```

## 🔧 Backend Customization

### Adding New API Endpoints
Add new endpoints to `telegram_backend.py`:

```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"message": "Custom endpoint"}
```

### Customizing Oracle Integration
Modify the `get_oracles()` function:

```python
async def get_oracles():
    async with get_unified_oracles() as oracles:
        # Add custom oracle logic
        return oracles
```

## 🧪 Testing

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Get prices
curl http://localhost:8000/api/prices

# Get staking info
curl http://localhost:8000/api/staking/{user_address}
```

### Test Frontend

1. Start backend server
2. Open `telegram_minapp.html` in browser
3. Test all functionality

## 📊 Example Response

### Get Prices

```json
{
  "gold": {
    "price": 2000.50,
    "confidence": 0.05,
    "exponent": -4,
    "timestamp": "2026-07-19T12:00:00Z",
    "status": "success"
  },
  "silver": {
    "price": 25.30,
    "confidence": 0.02,
    "exponent": -2,
    "timestamp": "2026-07-19T12:00:00Z",
    "status": "success"
  },
  "aapl": {
    "value": 175.80,
    "round_id": 12345,
    "updated_at": "2026-07-19T12:00:00Z",
    "status": "success"
  },
  "timestamp": "2026-07-19T12:00:00Z"
}
```

### Stake Response

```json
{
  "success": true,
  "tx_hash": "0x1234...",
  "tx_receipt": {
    "status": 1,
    "gas_used": 150000,
    "block_number": 12345
  }
}
```

## 🔒 Security

### Environment Variables
- Never commit `.env` file to version control
- Use secure private key storage
- Enable HTTPS in production

### API Rate Limiting
Consider adding rate limiting:

```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/api/prices")
@limiter.limit("10/minute")
async def get_prices(...):
    ...
```

## 🚢 Deployment

### Vercel Deployment (Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### Railway/Render Deployment (Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway up
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY telegram_backend.py .
COPY telegram_minapp.html .

EXPOSE 8000

CMD ["python", "telegram_backend.py"]
```

## 🤝 Integration with MCP Server

Integrate Telegram Mini-App with existing MCP server:

```python
# In mcp_server.py
from telegram_backend import app

# Mount FastAPI app
from fastapi.middleware.cors import CORSMiddleware

# Add to existing MCP server
```

## 📚 Additional Resources

- [Telegram WebApp Documentation](https://core.telegram.org/bots/webapps)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Pyth Network Documentation](https://docs.pyth.network/)
- [Chainlink Oracles Documentation](https://docs.chain.link/)

## 🤝 Contributing

This is part of the Robinhood Chain EVM MCP Server project. See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## 📄 License

MIT License - See [LICENSE](../LICENSE) file for details.
