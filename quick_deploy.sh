#!/bin/bash
# Quick deployment script for Robinhood EVM MCP Server
# Integrates Oracles, Staking Contract, and Telegram Mini-App

set -e

echo "🚀 Robinhood EVM MCP Server - Quick Deployment"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Please create .env file with the following variables:"
    echo "  - ROBINHOOD_CHAIN_PRIVATE_KEY"
    echo "  - ROBINHOOD_CHAIN_RPC_URL"
    echo "  - PYTH_API_KEY"
    echo "  - CHAINLINK_API_KEY"
    exit 1
fi

echo "✅ .env file found"

# Check if dependencies are installed
if ! python3 -c "import web3" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

# Deploy Staking Contract
echo ""
echo "📡 Deploying Staking Contract..."
echo "This may take a few minutes..."
python3 deploy_staking_complete.py

# Start MCP Server
echo ""
echo "🚀 Starting MCP Server..."
echo ""
echo "Server is running. Press Ctrl+C to stop."
echo ""
python3 mcp_server_with_integration.py
