# generate_index_html.py
# Generates a state-of-the-art multi-page Web3 trading dApp dashboard for the Meme Launchpad

import json
import os

def generate():
    # 1. Load compiled contract JSON
    artifact_path = "MemeFactory.json"
    if not os.path.exists(artifact_path):
        print("❌ MemeFactory.json not found! Run compile.cjs first.")
        return

    with open(artifact_path, "r") as f:
        artifact = json.load(f)

    abi = artifact["abi"]
    
    # Deployed contract address
    factory_address = "0x322f214995d4808660557F5744Ae8792AE1129cA"

    # Token ABI needed for name, symbol, etc.
    with open("MemeToken.json", "r") as f:
        token_artifact = json.load(f)
    token_abi = token_artifact["abi"]

    # 2. HTML Template with premium styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robinhood Chain - Meme Launchpad & DEX</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <!-- Ethers.js v5 CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/5.7.2/ethers.umd.min.js" type="text/javascript"></script>
    <style>
        :root {{
            --bg-color: #060b18;
            --card-bg: rgba(15, 23, 42, 0.6);
            --border-color: rgba(245, 158, 11, 0.16);
            --gold: #fbbf24;
            --gold-glow: rgba(245, 158, 11, 0.25);
            --gold-dark: #b45309;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --success: #10b981;
            --error: #ef4444;
            --font-main: 'Outfit', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: var(--font-main);
        }}

        body {{
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(245, 158, 11, 0.08) 0px, transparent 40%),
                radial-gradient(at 100% 0%, rgba(30, 58, 138, 0.25) 0px, transparent 50%),
                radial-gradient(at 50% 100%, rgba(13, 148, 136, 0.04) 0px, transparent 60%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}

        /* Header Ticker */
        .ticker-bar {{
            background: rgba(245, 158, 11, 0.08);
            border-bottom: 1px solid rgba(245, 158, 11, 0.12);
            padding: 8px 20px;
            font-size: 12px;
            font-family: var(--font-mono);
            display: flex;
            gap: 30px;
            justify-content: center;
            overflow-x: auto;
            white-space: nowrap;
            color: var(--text-secondary);
        }}

        .ticker-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .ticker-val {{
            color: var(--gold);
            font-weight: 700;
        }}

        /* Navbar Layout */
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px 20px;
            z-index: 10;
        }}

        .logo-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .logo {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 22px;
            font-weight: 800;
            color: #060b18;
            box-shadow: 0 0 20px var(--gold-glow);
        }}

        .brand-name {{
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        /* Tab Navigation Links */
        .nav-links {{
            display: flex;
            gap: 8px;
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 4px;
        }}

        .nav-tab {{
            background: none;
            border: none;
            border-radius: 10px;
            padding: 10px 18px;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .nav-tab.active {{
            background: rgba(245, 158, 11, 0.12);
            color: var(--gold);
            border: 1px solid rgba(245, 158, 11, 0.15);
        }}

        .connect-btn {{
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 12px 24px;
            color: var(--gold);
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .connect-btn:hover {{
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            color: #060b18;
            box-shadow: 0 0 15px var(--gold-glow);
            transform: translateY(-1px);
        }}

        /* Page Layout & Container Views */
        .main-container {{
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            flex-grow: 1;
        }}

        .view-section {{
            display: none;
            animation: fadeIn 0.4s ease-out;
        }}

        .view-section.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Common Cards */
        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }}

        /* Grid for Cards */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }}

        @media (max-width: 900px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Token Card styling */
        .token-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        @media (max-width: 650px) {{
            .token-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .token-card {{
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(245, 158, 11, 0.08);
            border-radius: 20px;
            padding: 24px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        .token-card:hover {{
            border-color: var(--gold);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.08);
        }}

        .token-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }}

        .avatar-circle {{
            width: 42px;
            height: 42px;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(30, 41, 59, 0.5));
            border: 1px solid rgba(245, 158, 11, 0.2);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 18px;
            font-weight: 800;
            color: var(--gold);
        }}

        .token-info {{
            margin-left: 12px;
            flex-grow: 1;
        }}

        .progress-badge {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 600;
        }}

        .progress-bar-container {{
            background: rgba(255, 255, 255, 0.04);
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
            margin-top: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .progress-bar {{
            background: linear-gradient(90deg, var(--gold), var(--success));
            height: 100%;
            width: 0%;
            transition: width 0.5s ease;
        }}

        /* Forms inputs & fields */
        .form-group {{
            margin-bottom: 20px;
        }}

        .form-group label {{
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .form-input {{
            width: 100%;
            background: rgba(5, 10, 21, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 14px;
            color: #fff;
            outline: none;
            transition: all 0.3s;
        }}

        .form-input:focus {{
            border-color: var(--gold);
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.15);
        }}

        .action-btn {{
            width: 100%;
            background: linear-gradient(135deg, var(--gold) 0%, #d97706 100%);
            border: none;
            border-radius: 14px;
            padding: 16px;
            color: #060b18;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px var(--gold-glow);
        }}

        .action-btn:hover {{
            background: linear-gradient(135deg, #d97706 0%, var(--gold-dark) 100%);
            box-shadow: 0 0 20px var(--gold-glow);
        }}

        .action-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            box-shadow: none;
        }}

        /* DEX Swapper Panel styling */
        .dex-container {{
            max-width: 480px;
            margin: 0 auto;
        }}

        .token-selector-row {{
            display: flex;
            align-items: center;
            background: rgba(5, 10, 21, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 14px;
            padding: 12px 16px;
            margin-bottom: 12px;
        }}

        .token-select-dropdown {{
            background: none;
            border: none;
            color: #fff;
            font-size: 16px;
            font-weight: 700;
            outline: none;
            cursor: pointer;
        }}

        .token-select-dropdown option {{
            background: var(--bg-color);
            color: #fff;
        }}

        /* Portfolio / Wallet Panel */
        .portfolio-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }}

        .wallet-stat-card {{
            background: rgba(15, 23, 42, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            flex: 1;
        }}

        .balance-value {{
            font-size: 26px;
            font-weight: 800;
            color: var(--gold);
            margin: 8px 0;
        }}

        .asset-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .asset-table th, .asset-table td {{
            text-align: left;
            padding: 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .asset-table th {{
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 600;
        }}

        .asset-table td {{
            font-size: 14px;
        }}

        .trade-tabs {{
            display: flex;
            background: rgba(5, 10, 21, 0.6);
            border-radius: 12px;
            padding: 4px;
            margin-bottom: 20px;
        }}

        .trade-tab-btn {{
            flex: 1;
            background: none;
            border: none;
            border-radius: 10px;
            padding: 10px;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .trade-tab-btn.active.buy {{
            background: var(--success);
            color: #060b18;
        }}

        .trade-tab-btn.active.sell {{
            background: var(--error);
            color: #fff;
        }}

        .status-box {{
            background: rgba(5, 10, 21, 0.8);
            border-left: 3px solid var(--gold);
            border-radius: 10px;
            padding: 14px;
            font-size: 13px;
            display: none;
            word-break: break-all;
            margin-top: 15px;
        }}

        /* Live Activity Stream */
        .console-box {{
            background: rgba(5, 10, 21, 0.95);
            border: 1px solid rgba(245, 158, 11, 0.15);
            border-radius: 16px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            height: 180px;
            overflow-y: hidden;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8);
            margin-top: 40px;
        }}

        .console-line {{
            display: flex;
            align-items: center;
            gap: 10px;
            opacity: 0.9;
        }}

        .console-time {{
            color: var(--text-secondary);
        }}

        .console-tag {{
            color: var(--gold);
            font-weight: 700;
        }}

        .console-action-buy {{
            color: var(--success);
            font-weight: 700;
        }}

        .console-action-sell {{
            color: var(--error);
            font-weight: 700;
        }}
    </style>
</head>
<body>

<div class="ticker-bar">
    <div class="ticker-item">🌐 L2 Gas Price: <span class="ticker-val">0.05 Gwei</span></div>
    <div class="ticker-item">💰 Total Pools: <span class="ticker-val" id="tickerPools">Loading...</span></div>
    <div class="ticker-item">📊 Robinhood L2: <span class="ticker-val">Active</span></div>
</div>

<div class="navbar">
    <div class="logo-container">
        <div class="logo">R</div>
        <div class="brand-name">Robinhood Terminal</div>
    </div>
    
    <div class="nav-links">
        <button class="nav-tab active" onclick="switchView('launchpad')">🏠 Launchpad</button>
        <button class="nav-tab" onclick="switchView('launch')">🚀 Create Token</button>
        <button class="nav-tab" onclick="switchView('swap')">🔄 DEX Swap</button>
        <button class="nav-tab" onclick="switchView('portfolio')">💼 Portfolio</button>
    </div>

    <button id="connectBtn" class="connect-btn">Connect Wallet</button>
</div>

<div class="main-container">
    
    <!-- 🏠 VIEW: LAUNCHPAD -->
    <div id="view-launchpad" class="view-section active">
        <div class="dashboard-grid">
            <!-- Active Pools -->
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="font-size:24px; font-weight:800;">🔥 Active Bonding Pools</h2>
                    <input type="text" id="searchInput" class="form-input" style="width:250px; padding:10px 14px;" placeholder="Search tokens...">
                </div>
                <div class="token-grid" id="tokenGrid">
                    <!-- Loaded dynamically -->
                </div>
            </div>

            <!-- Trade Sidebar -->
            <div>
                <div class="trade-card" id="tradeCard" style="display:block; border-color:rgba(255,255,255,0.05);">
                    <div id="tradeCardContent">
                        <div class="panel-header">Select a Token</div>
                        <p style="color:var(--text-secondary); font-size:14px; text-align:center;">Click on any token in the active pools list to trade it on the bonding curve.</p>
                    </div>
                    
                    <div id="tradeControls" style="display:none;">
                        <div class="panel-header" id="tradeTitle">Trade Token</div>
                        <p id="tradeAddress" style="font-size:11px; font-family:var(--font-mono); color:var(--text-secondary); margin-bottom:20px; overflow-wrap:break-word;"></p>
                        
                        <div class="trade-tabs">
                            <button class="trade-tab-btn active buy" id="tabBuy">Buy</button>
                            <button class="trade-tab-btn" id="tabSell">Sell</button>
                        </div>

                        <div class="form-group">
                            <label id="inputLabel">Amount of ETH to spend</label>
                            <input type="number" id="tradeAmount" class="form-input" placeholder="0.01" step="0.005">
                        </div>

                        <button class="action-btn" id="tradeBtn" style="background:var(--success); color:#060b18;">Swap</button>
                        
                        <div id="statusBox" class="status-box">
                            <div id="statusBody">Processing...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 🚀 VIEW: CREATE TOKEN -->
    <div id="view-launch" class="view-section">
        <div class="card" style="max-width: 550px; margin: 0 auto;">
            <div class="panel-header" style="font-size:24px;">🚀 Launch a Meme Token</div>
            <p style="color:var(--text-secondary); font-size:14px; margin-bottom:24px;">Create an upgraded ERC-20 meme coin on the Robinhood Chain virtual bonding curve. Deploy cost is set to just 0.0005 ETH.</p>
            
            <div class="form-group">
                <label for="tokName">Token Name</label>
                <input type="text" id="tokName" class="form-input" placeholder="e.g. Robinhood Doge">
            </div>
            <div class="form-group">
                <label for="tokSymbol">Token Symbol</label>
                <input type="text" id="tokSymbol" class="form-input" placeholder="e.g. RHDOGE">
            </div>
            <div class="form-group">
                <label for="tokSupply">Initial Supply</label>
                <input type="number" id="tokSupply" class="form-input" value="1000000000" readonly>
            </div>
            
            <button class="action-btn" id="launchBtn">Deploy Meme Token (0.0005 ETH)</button>
        </div>
    </div>

    <!-- 🔄 VIEW: DEX SWAP (STANDARD TOKENS) -->
    <div id="view-swap" class="view-section">
        <div class="card dex-container">
            <div class="panel-header" style="font-size:24px;">🔄 Swap Tokens</div>
            <p style="color:var(--text-secondary); font-size:14px; margin-bottom:24px;">Swap standard Robinhood Chain L2 assets using your Rabby Gas Account.</p>
            
            <!-- Pay Token -->
            <div class="form-group">
                <label>Pay</label>
                <div class="token-selector-row">
                    <select id="swapFromSelect" class="token-select-dropdown" style="flex-grow:1;">
                        <option value="ETH">ETH (Native)</option>
                        <option value="USDG">USDG (Stablecoin)</option>
                        <option value="AAPL">AAPL (Tokenized Stock)</option>
                        <option value="TSLA">TSLA (Tokenized Stock)</option>
                    </select>
                    <input type="number" id="swapFromAmount" class="form-input" style="width:150px; border:none; text-align:right; font-size:18px;" placeholder="0.0">
                </div>
            </div>

            <!-- Receive Token -->
            <div class="form-group">
                <label>Receive</label>
                <div class="token-selector-row">
                    <select id="swapToSelect" class="token-select-dropdown" style="flex-grow:1;">
                        <option value="USDG" selected>USDG (Stablecoin)</option>
                        <option value="ETH">ETH (Native)</option>
                        <option value="AAPL">AAPL (Tokenized Stock)</option>
                        <option value="TSLA">TSLA (Tokenized Stock)</option>
                    </select>
                    <input type="number" id="swapToAmount" class="form-input" style="width:150px; border:none; text-align:right; font-size:18px;" placeholder="0.0" readonly>
                </div>
            </div>

            <button class="action-btn" id="dexSwapBtn">Execute Swap (Mock Router)</button>
        </div>
    </div>

    <!-- 💼 VIEW: PORTFOLIO -->
    <div id="view-portfolio" class="view-section">
        <div class="card">
            <div class="portfolio-header">
                <div>
                    <h2 style="font-size:24px; font-weight:800;">💼 My Portfolio</h2>
                    <p id="portfolioWalletAddr" style="font-size:13px; font-family:var(--font-mono); color:var(--text-secondary); margin-top:4px;">Not Connected</p>
                </div>
            </div>

            <!-- Balances Stats Cards -->
            <div style="display:flex; gap:20px; margin-bottom:30px;">
                <div class="wallet-stat-card">
                    <div style="font-size:13px; color:var(--text-secondary);">Native ETH Balance</div>
                    <div class="balance-value" id="portEthBalance">0.00 ETH</div>
                </div>
                <div class="wallet-stat-card">
                    <div style="font-size:13px; color:var(--text-secondary);">Asset Count</div>
                    <div class="balance-value" id="portAssetCount">0</div>
                </div>
            </div>

            <h3 style="font-size:18px; font-weight:700; margin-bottom:15px;">Asset Allocations</h3>
            <table class="asset-table">
                <thead>
                    <tr>
                        <th>Asset Name</th>
                        <th>Ticker</th>
                        <th>Balance</th>
                        <th>Contract Address</th>
                    </tr>
                </thead>
                <tbody id="portfolioAssetBody">
                    <tr>
                        <td colspan="4" style="text-align:center; color:var(--text-secondary);">Connect your wallet to query active holdings on Robinhood Chain L2.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Live Activity Log Ticker -->
    <div class="console-box" id="consoleBox">
        <div class="console-line">
            <span class="console-time">[18:20:00]</span>
            <span class="console-tag">[AGENT_BOT]</span>
            <span class="console-text">Active connection to Robinhood Chain L2 nodes. Ready for swap routing...</span>
        </div>
    </div>

</div>

<script>
    const factoryAddress = "{factory_address}";
    const factoryAbi = {json.dumps(abi)};
    const tokenAbi = {json.dumps(token_abi)};

    // Standard Token Addresses on Robinhood L2
    const standardTokens = {{
        "USDG": "0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168",
        "AAPL": "0xaF3D76f1834A1d425780943C99Ea8A608f8a93f9",
        "TSLA": "0x322F0929c4625eD5bAd873c95208D54E1c003b2d"
    }};

    let provider;
    let signer;
    let factoryContract;
    let activeTokenAddress = null;
    let tradeMode = "buy";
    let loadedPoolsData = [];

    const connectBtn = document.getElementById("connectBtn");
    const launchBtn = document.getElementById("launchBtn");
    const tokenGrid = document.getElementById("tokenGrid");
    const searchInput = document.getElementById("searchInput");
    const tickerPools = document.getElementById("tickerPools");
    
    // Trade controls DOM
    const tradeCardContent = document.getElementById("tradeCardContent");
    const tradeControls = document.getElementById("tradeControls");
    const tradeTitle = document.getElementById("tradeTitle");
    const tradeAddressText = document.getElementById("tradeAddress");
    const tabBuy = document.getElementById("tabBuy");
    const tabSell = document.getElementById("tabSell");
    const inputLabel = document.getElementById("inputLabel");
    const tradeAmountInput = document.getElementById("tradeAmount");
    const tradeBtn = document.getElementById("tradeBtn");
    const statusBox = document.getElementById("statusBox");
    const statusBody = document.getElementById("statusBody");
    const consoleBox = document.getElementById("consoleBox");

    // Portfolio views DOM
    const portfolioWalletAddr = document.getElementById("portfolioWalletAddr");
    const portEthBalance = document.getElementById("portEthBalance");
    const portAssetCount = document.getElementById("portAssetCount");
    const portfolioAssetBody = document.getElementById("portfolioAssetBody");

    // DEX swap DOM
    const swapFromSelect = document.getElementById("swapFromSelect");
    const swapToSelect = document.getElementById("swapToSelect");
    const swapFromAmount = document.getElementById("swapFromAmount");
    const swapToAmount = document.getElementById("swapToAmount");
    const dexSwapBtn = document.getElementById("dexSwapBtn");

    // Multi-page switch routing
    function switchView(viewId) {{
        document.querySelectorAll(".view-section").forEach(s => s.classList.remove("active"));
        document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
        
        document.getElementById(`view-${{viewId}}`).classList.add("active");
        
        // Find corresponding tab button
        const tabs = document.querySelectorAll(".nav-tab");
        if (viewId === "launchpad") tabs[0].classList.add("active");
        if (viewId === "launch") tabs[1].classList.add("active");
        if (viewId === "swap") tabs[2].classList.add("active");
        if (viewId === "portfolio") tabs[3].classList.add("active");
    }}

    // Ticker log simulator
    const aiAgents = ["satoshis_bot", "poly_agent", "kronos_whale", "rh_trading_bot", "pepe_snip_agent"];
    setInterval(() => {{
        const agent = aiAgents[Math.floor(Math.random() * aiAgents.length)];
        const isBuy = Math.random() > 0.45;
        const ethVal = (Math.random() * 0.08 + 0.005).toFixed(4);
        const tokAmt = Math.floor(Math.random() * 90000 + 1000).toLocaleString();
        
        const timeStr = new Date().toTimeString().split(' ')[0];
        const line = document.createElement("div");
        line.className = "console-line";
        
        const actionSpan = isBuy 
            ? `<span class="console-action-buy">[BUY]</span>` 
            : `<span class="console-action-sell">[SELL]</span>`;
            
        const text = isBuy
            ? `Agent @${{agent}} sniped ${{ethVal}} ETH of custom bonding pool.`
            : `Agent @${{agent}} executed sell transaction of ${{tokAmt}} tokens on Robinhood L2.`;
            
        line.innerHTML = `<span class="console-time">[${{timeStr}}]</span> ${{actionSpan}} <span class="console-text">${{text}}</span>`;
        consoleBox.appendChild(line);
        if (consoleBox.children.length > 25) consoleBox.removeChild(consoleBox.firstChild);
        consoleBox.scrollTop = consoleBox.scrollHeight;
    }}, 4500);

    async function switchNetwork() {{
        const targetChainId = "0x1237";
        try {{
            await window.ethereum.request({{
                method: "wallet_switchEthereumChain",
                params: [{{ chainId: targetChainId }}],
            }});
            return true;
        }} catch (switchError) {{
            if (switchError.code === 4902 || switchError.message.includes("4902")) {{
                try {{
                    await window.ethereum.request({{
                        method: "wallet_addEthereumChain",
                        params: [{{
                            chainId: targetChainId,
                            chainName: "Robinhood Chain Mainnet",
                            nativeCurrency: {{
                                name: "Ethereum",
                                symbol: "ETH",
                                decimals: 18
                            }},
                            rpcUrls: ["https://rpc.mainnet.chain.robinhood.com"],
                            blockExplorerUrls: ["https://robinhoodchain.blockscout.com"]
                        }}],
                    }});
                    return true;
                }} catch (addError) {{
                    alert("Failed to add Robinhood Chain to wallet.");
                    return false;
                }}
            }}
            alert("Failed to switch network.");
            return false;
        }}
    }}

    async function connectWallet() {{
        if (typeof window.ethereum === "undefined") {{
            alert("Open this page inside Rabby mobile browser.");
            return;
        }}
        try {{
            provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            signer = provider.getSigner();
            const address = await signer.getAddress();
            
            // Switch network automatically
            let network = await provider.getNetwork();
            if (network.chainId !== 4663) {{
                const success = await switchNetwork();
                if (!success) return;
                await new Promise(r => setTimeout(r, 1000));
                provider = new ethers.providers.Web3Provider(window.ethereum);
                signer = provider.getSigner();
                network = await provider.getNetwork();
            }}

            factoryContract = new ethers.Contract(factoryAddress, factoryAbi, signer);
            
            connectBtn.innerText = `Connected: ${{address.substring(0, 6)}}...${{address.substring(38)}}`;
            connectBtn.style.background = "var(--success)";
            connectBtn.style.color = "#060b18";
            connectBtn.style.borderColor = "var(--success)";
            
            await loadPools();
            await updatePortfolio(address);
        }} catch (err) {{
            console.error(err);
        }}
    }}

    async function loadPools() {{
        if (!factoryContract) return;
        try {{
            const count = await factoryContract.getMemeCount();
            tickerPools.innerText = `${{count.toString()}} Meme Coins`;
            loadedPoolsData = [];

            for (let i = 0; i < count; i++) {{
                const tokenAddr = await factoryContract.allMemeTokens(i);
                const pool = await factoryContract.pools(tokenAddr);
                const tokenContract = new ethers.Contract(tokenAddr, tokenAbi, provider);
                
                const name = await tokenContract.name();
                const symbol = await tokenContract.symbol();
                
                const maxReserve = ethers.utils.parseEther("800000000");
                const currentReserve = pool.tokenReserves;
                const sold = maxReserve.sub(currentReserve);
                let progress = sold.mul(100).div(maxReserve).toNumber();
                if (progress < 0) progress = 0;
                if (progress > 100) progress = 100;

                loadedPoolsData.push({{
                    address: tokenAddr,
                    name: name,
                    symbol: symbol,
                    ethReserves: pool.ethReserves,
                    progress: progress
                }});
            }}
            
            renderPools();
        }} catch (err) {{
            console.error("Error loading pools:", err);
        }}
    }}

    function renderPools() {{
        const search = searchInput.value.toLowerCase().trim();
        let filtered = loadedPoolsData.filter(t => 
            t.name.toLowerCase().includes(search) || 
            t.symbol.toLowerCase().includes(search)
        );

        tokenGrid.innerHTML = "";
        filtered.forEach(token => {{
            const card = document.createElement("div");
            card.className = "token-card";
            const firstLetter = token.name.charAt(0).toUpperCase();

            card.innerHTML = `
                <div class="token-card-header">
                    <div style="display:flex; align-items:center;">
                        <div class="avatar-circle">${{firstLetter}}</div>
                        <div class="token-info">
                            <div class="token-name">${{token.name}}</div>
                            <div class="token-symbol">$${{token.symbol}}</div>
                        </div>
                    </div>
                    <span class="progress-badge">${{token.progress}}%</span>
                </div>
                <div class="token-metrics">
                    <div class="metric-item">
                        <span>Liquidity:</span>
                        <span class="metric-value">${{ethers.utils.formatEther(token.ethReserves)}} ETH</span>
                    </div>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${{token.progress}}%"></div>
                </div>
            `;
            
            card.addEventListener("click", () => selectToken(token.address, token.symbol));
            tokenGrid.appendChild(card);
        }});
    }}

    function selectToken(addr, symbol) {{
        activeTokenAddress = addr;
        tradeCardContent.style.display = "none";
        tradeControls.style.display = "block";
        tradeTitle.innerText = `Trade $${{symbol}}`;
        tradeAddressText.innerText = addr;
        statusBox.style.display = "none";
        tradeAmountInput.value = "";
    }}

    // Tab Swapping Logic
    tabBuy.addEventListener("click", () => {{
        tradeMode = "buy";
        tabBuy.className = "trade-tab-btn active buy";
        tabSell.className = "trade-tab-btn";
        inputLabel.innerText = "Amount of ETH to spend";
        tradeAmountInput.placeholder = "0.01";
        tradeBtn.style.background = "var(--success)";
        tradeBtn.style.color = "#060b18";
    }});

    tabSell.addEventListener("click", () => {{
        tradeMode = "sell";
        tabSell.className = "trade-tab-btn active sell";
        tabBuy.className = "trade-tab-btn";
        inputLabel.innerText = "Amount of tokens to sell";
        tradeAmountInput.placeholder = "10000";
        tradeBtn.style.background = "var(--error)";
        tradeBtn.style.color = "#fff";
    }});

    // Launch Token
    launchBtn.addEventListener("click", async () => {{
        if (!factoryContract) {{
            alert("Connect wallet first!");
            return;
        }}
        const name = document.getElementById("tokName").value.trim();
        const symbol = document.getElementById("tokSymbol").value.trim();
        if (!name || !symbol) {{
            alert("Fill in name and symbol.");
            return;
        }}

        try {{
            launchBtn.innerText = "Deploying...";
            launchBtn.disabled = true;
            
            const tx = await factoryContract.deployMemeToken(name, symbol, 1000000000, {{
                value: ethers.utils.parseEther("0.0005")
            }});
            
            await tx.wait();
            alert("Token deployed successfully on Robinhood Chain L2!");
            document.getElementById("tokName").value = "";
            document.getElementById("tokSymbol").value = "";
            
            await loadPools();
            switchView("launchpad");
        }} catch (err) {{
            alert("Deployment failed: " + err.message);
        }} finally {{
            launchBtn.innerText = "Deploy Meme Token (0.0005 ETH)";
            launchBtn.disabled = false;
        }}
    }});

    // Swap Meme Coin
    tradeBtn.addEventListener("click", async () => {{
        if (!factoryContract || !activeTokenAddress) return;
        const amount = tradeAmountInput.value.trim();
        if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {{
            alert("Please enter a valid amount.");
            return;
        }}

        statusBox.style.display = "block";
        statusBody.innerText = "Initiating transaction in wallet...";

        try {{
            tradeBtn.disabled = true;
            const defaultReferrer = "0x0000000000000000000000000000000000000000";

            if (tradeMode === "buy") {{
                const valueWei = ethers.utils.parseEther(amount);
                const tx = await factoryContract.buyMemeToken(activeTokenAddress, defaultReferrer, {{
                    value: valueWei
                }});
                statusBody.innerText = `Transaction broadcasted!\\nTx Hash: ${{tx.hash}}\\nWaiting for confirmation...`;
                await tx.wait();
                statusBody.innerText = `✅ Success! Swap complete.`;
            }} else {{
                const tokenAmount = ethers.utils.parseEther(amount);
                statusBody.innerText = "Approving factory to spend tokens...";
                const tokenContract = new ethers.Contract(activeTokenAddress, tokenAbi, signer);
                const approveTx = await tokenContract.approve(factoryAddress, tokenAmount);
                await approveTx.wait();
                
                statusBody.innerText = "Executing sell swap...";
                const tx = await factoryContract.sellMemeToken(activeTokenAddress, tokenAmount, defaultReferrer);
                statusBody.innerText = `Transaction broadcasted!\\nTx Hash: ${{tx.hash}}\\nWaiting for confirmation...`;
                await tx.wait();
                statusBody.innerText = `✅ Success! Swap complete.`;
            }}
            await loadPools();
            const address = await signer.getAddress();
            await updatePortfolio(address);
        }} catch (err) {{
            statusBody.innerText = `❌ Error: ${{err.message}}`;
        }} finally {{
            tradeBtn.disabled = false;
        }}
    }});

    // Update Portfolio asset balances
    async function updatePortfolio(walletAddress) {{
        portfolioWalletAddr.innerText = walletAddress;
        
        // Native Balance
        const balance = await provider.getBalance(walletAddress);
        portEthBalance.innerText = `${{parseFloat(ethers.utils.formatEther(balance)).toFixed(4)}} ETH`;

        let assetRows = "";
        let count = 0;

        // Query standard L2 assets
        for (const [ticker, address] of Object.entries(standardTokens)) {{
            try {{
                const erc20 = new ethers.Contract(address, tokenAbi, provider);
                const bal = await erc20.balanceOf(walletAddress);
                const name = ticker === "USDG" ? "USDG Stablecoin" : `${{ticker}} Tokenized Asset`;
                
                if (bal.gt(0)) {{
                    count++;
                    assetRows += `
                        <tr>
                            <td>${{name}}</td>
                            <td><span class="progress-badge">${{ticker}}</span></td>
                            <td>${{ethers.utils.formatUnits(bal, 18)}}</td>
                            <td style="font-family:var(--font-mono); font-size:12px;">${{address.substring(0, 6)}}...${{address.substring(38)}}</td>
                        </tr>
                    `;
                }}
            }} catch (e) {{}}
        }}

        // Query deployed meme tokens balances
        for (let i = 0; i < loadedPoolsData.length; i++) {{
            const token = loadedPoolsData[i];
            try {{
                const erc20 = new ethers.Contract(token.address, tokenAbi, provider);
                const bal = await erc20.balanceOf(walletAddress);
                if (bal.gt(0)) {{
                    count++;
                    assetRows += `
                        <tr>
                            <td>${{token.name}}</td>
                            <td><span class="progress-badge" style="background:rgba(245,158,11,0.1); color:var(--gold); border-color:var(--gold);">${{token.symbol}}</span></td>
                            <td>${{ethers.utils.formatUnits(bal, 18)}}</td>
                            <td style="font-family:var(--font-mono); font-size:12px;">${{token.address.substring(0, 6)}}...${{token.address.substring(38)}}</td>
                        </tr>
                    `;
                }}
            }} catch (e) {{}}
        }}

        portAssetCount.innerText = count.toString();
        if (count > 0) {{
            portfolioAssetBody.innerHTML = assetRows;
        }} else {{
            portfolioAssetBody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-secondary);">No active token balances detected on Robinhood Chain L2.</td></tr>`;
        }}
    }}

    // DEX Mock Swap (Interactive mock swapper UI to swap standard L2 tokens)
    swapFromAmount.addEventListener("input", () => {{
        const amt = parseFloat(swapFromAmount.value);
        if (amt && amt > 0) {{
            const rate = swapFromSelect.value === "ETH" ? 3400 : 0.0003;
            swapToAmount.value = (amt * rate).toFixed(4);
        }} else {{
            swapToAmount.value = "";
        }}
    }});

    dexSwapBtn.addEventListener("click", async () => {{
        if (!signer) {{
            alert("Connect wallet first!");
            return;
        }}
        const amt = swapFromAmount.value;
        if (!amt || parseFloat(amt) <= 0) {{
            alert("Enter amount to swap.");
            return;
        }}

        dexSwapBtn.innerText = "Interacting with Rabby...";
        try {{
            // Construct mock tx sending 0 value just to prompt Rabby Gas Account popup
            const tx = await signer.sendTransaction({{
                to: "0x0000000000000000000000000000000000000000",
                value: 0
            }});
            alert("Swap completed successfully!");
            swapFromAmount.value = "";
            swapToAmount.value = "";
            const address = await signer.getAddress();
            await updatePortfolio(address);
        }} catch (err) {{
            alert("Swap aborted: " + err.message);
        }} finally {{
            dexSwapBtn.innerText = "Execute Swap (Mock Router)";
        }}
    }});

    // Bind inputs & events
    searchInput.addEventListener("input", renderPools);
    connectBtn.addEventListener("click", connectWallet);
</script>

</body>
</html>
"""

    # 3. Write HTML file to workspace
    output_path = "index.html"
    with open(output_path, "w") as f:
        f.write(html_content)

    print(f"✅ Generated {output_path} successfully!")
    print(f"File path: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate()
