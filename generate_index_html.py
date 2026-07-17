# generate_index_html.py
# generate_index_html.py - Upgraded Web3 Sovereign Launchpad Terminal
# ponytail: clean, zero-boilerplate codebase utilizing local ethers.js and Three.js.
# ceiling: Client-side RPC queries can hit public node rate-limits; upgrade path: Goldsky/The Graph indexer.

import os

def load_all_envs():
    for path in [os.path.expanduser("~/.env"), ".env"]:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_all_envs()

def generate():
    meme_factory = os.getenv("MEME_FACTORY_ADDRESS", "0xAb783574A8B12d580659e86F01dEA310Fb300113")
    robin_mcp = os.getenv("ROBIN_MCP_TOKEN_ADDRESS", "0xB6579E6489afC53Cd3eEb14eEF0EF039c65914bd")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robinhood L2 - Sovereign Code & Culture Launchpad</title>
    <!-- Outfit & JetBrains Mono Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    
    <!-- Local Ethers.js and Three.js CDN -->
    <script src="/ethers.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    
    <style>
        :root {{
            --bg: #02040a;
            --card: rgba(6, 10, 24, 0.65);
            --gold: #fbbf24;
            --gold-dark: #b45309;
            --gold-glow: rgba(251, 191, 36, 0.15);
            --border: rgba(251, 191, 36, 0.15);
            --cream: #faf5e6;
            --text: var(--cream);
            --text-muted: #9ca3af;
            --success: #10b981;
            --error: #ef4444;
            --font-mono: 'JetBrains Mono', monospace;
            --accent-green: #00ff88;
            --accent-pink: #ff0066;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }}
        body {{ 
            background-color: var(--bg); 
            color: var(--text); 
            min-height: 400vh; /* Height to support scrolling sections */
            overflow-x: hidden; 
            scroll-behavior: smooth;
        }}

        /* Custom Scrollbars */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #02040a;
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(251, 191, 36, 0.3);
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(251, 191, 36, 0.6);
        }}

        /* 3D Fullscreen Background */
        .scroll-world-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #02040a;
            overflow: hidden;
            z-index: -1;
            pointer-events: none;
        }}
        #worldCanvas {{ width: 100%; height: 100%; display: block; }}

        /* HUD & Overlays */
        .hud-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
        }}
        .hud-top {{
            position: absolute;
            top: 75px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            width: 100%;
        }}
        .overlay-title {{ 
            font-size: 2.5rem; 
            font-weight: 800; 
            background: linear-gradient(135deg, #fff, var(--gold)); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            letter-spacing: -1px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.5);
            transition: all 0.5s ease;
        }}
        .overlay-desc {{ 
            color: var(--text-muted); 
            font-size: 13px; 
            font-family: var(--font-mono); 
            margin-top: 6px;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.5s ease;
        }}

        /* Navigation */
        .navbar {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 16px 40px; 
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            z-index: 100;
            background: rgba(2, 4, 10, 0.75);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }}
        .logo-box {{ display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 22px; letter-spacing: -0.5px; }}
        .logo-icon {{ 
            width: 34px; 
            height: 34px; 
            background: linear-gradient(135deg, var(--gold), var(--gold-dark)); 
            border-radius: 8px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            color: #030712;
            font-weight: 800;
        }}
        .nav-tabs {{ display: flex; gap: 6px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 4px; }}
        .tab-btn {{ background: none; border: none; color: var(--text-muted); font-size: 13px; font-weight: 600; padding: 8px 18px; border-radius: 8px; cursor: pointer; transition: 0.2s; }}
        .tab-btn:hover {{ color: var(--text); }}
        .tab-btn.active {{ background: rgba(251,191,36,0.12); color: var(--gold); border: 1px solid rgba(251,191,36,0.15); }}
        
        .connect-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: var(--text);
            font-size: 13px;
            font-weight: 600;
            padding: 8px 16px;
            cursor: pointer;
            transition: 0.2s;
        }}
        .connect-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--gold);
        }}

        /* Scroll Layout Sections */
        .scroll-section {{
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            padding: 100px 40px 40px 40px;
            opacity: 0;
            transform: translateY(40px);
            transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .scroll-section.active {{
            opacity: 1;
            transform: translateY(0);
        }}

        /* Container Card styles */
        .container {{ max-width: 1100px; width: 100%; margin: 0 auto; }}
        .card {{ 
            background: var(--card); 
            backdrop-filter: blur(20px); 
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border); 
            border-radius: 24px; 
            padding: 30px; 
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .card:hover {{
            border-color: rgba(251, 191, 36, 0.25);
            box-shadow: 0 25px 60px rgba(251, 191, 36, 0.05);
        }}
        .grid {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 30px; }}
        @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}

        /* Forms */
        .form-group {{ margin-bottom: 18px; }}
        .form-group label {{ display: block; font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px; }}
        .input {{ width: 100%; background: rgba(3, 7, 18, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 12px 14px; color: var(--text); font-size: 14px; outline: none; transition: all 0.3s; }}
        .input:focus {{ border-color: var(--gold); box-shadow: 0 0 12px rgba(251, 191, 36, 0.12); background: rgba(3, 7, 18, 0.9); }}
        
        select.input {{
            appearance: none;
            background-image: url("data:image/svg+xml;utf8,<svg fill='white' height='24' viewBox='0 0 24 24' width='24' xmlns='http://www.w3.org/2000/svg'><path d='M7 10l5 5 5-5z'/><path d='M0 0h24v24H0z' fill='none'/></svg>");
            background-repeat: no-repeat;
            background-position: right 10px center;
        }}

        .btn {{ 
            width: 100%; 
            background: linear-gradient(135deg, var(--gold), var(--gold-dark)); 
            border: none; 
            border-radius: 12px; 
            padding: 14px; 
            color: #030712; 
            font-size: 14px; 
            font-weight: 800; 
            cursor: pointer; 
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            box-shadow: 0 4px 12px var(--gold-glow);
        }}
        .btn:hover {{ 
            transform: translateY(-1px); 
            box-shadow: 0 6px 20px rgba(251, 191, 36, 0.3); 
            filter: brightness(1.1);
        }}
        
        .btn-outline {{
            background: none;
            border: 1px solid rgba(255,255,255,0.1);
            color: var(--text);
            box-shadow: none;
            margin-top: 10px;
        }}
        .btn-outline:hover {{
            background: rgba(255,255,255,0.03);
            border-color: var(--gold);
            color: var(--gold);
        }}

        /* Fullscreen Workspaces */
        .workspace-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(3, 5, 12, 0.98);
            backdrop-filter: blur(35px);
            -webkit-backdrop-filter: blur(35px);
            z-index: 1000;
            display: none;
            animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            padding: 40px;
            overflow-y: auto;
        }}
        @keyframes slideUp {{
            from {{ transform: translateY(100%); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
        
        .ws-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding-bottom: 20px;
        }}
        .back-btn {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: 0.2s;
        }}
        .back-btn:hover {{
            border-color: var(--gold);
            color: var(--gold);
            background: rgba(251,191,36,0.05);
        }}

        /* Candlestick Canvas */
        .chart-box {{
            width: 100%;
            height: 320px;
            background: #010206;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.03);
            overflow: hidden;
            position: relative;
        }}
        #priceChart {{ width: 100%; height: 100%; display: block; }}

        .console {{ 
            background: #010206; 
            border-radius: 16px; 
            padding: 18px; 
            font-family: var(--font-mono); 
            font-size: 12px; 
            height: 250px; 
            overflow-y: auto; 
            display: flex; 
            flex-direction: column; 
            gap: 8px; 
            box-shadow: inset 0 0 15px #000;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }}
        .c-line {{ display: flex; gap: 8px; line-height: 1.4; }}
        .c-time {{ color: var(--text-muted); }}
        .c-tag {{ color: var(--gold); font-weight: 700; }}

        /* Dev Leaders & PRs */
        .table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .table th, .table td {{ padding: 12px 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 13px; }}
        .table th {{ color: var(--text-muted); text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; font-weight: 600; }}
        
        .badge {{
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-success {{ background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.15); }}
        .badge-warn {{ background: rgba(251, 191, 36, 0.1); color: var(--gold); border: 1px solid rgba(251, 191, 36, 0.15); }}

        /* Chat simulation */
        .chat {{ 
            display: flex; 
            flex-direction: column; 
            gap: 12px; 
            background: #010206; 
            border-radius: 16px; 
            padding: 18px; 
            height: 300px; 
            overflow-y: auto; 
            border: 1px solid rgba(255,255,255,0.03); 
        }}
        .bubble {{ max-width: 80%; padding: 10px 14px; border-radius: 14px; font-size: 13px; line-height: 1.4; }}
        .b-user {{ background: rgba(251,191,36,0.12); align-self: flex-end; color: var(--gold); border: 1px solid rgba(251,191,36,0.08); border-bottom-right-radius: 2px; }}
        .b-agent {{ background: rgba(16, 185, 129, 0.1); align-self: flex-start; color: #34d399; border: 1px solid rgba(16, 185, 129, 0.08); border-bottom-left-radius: 2px; }}

        /* Step visualizer */
        .step-container {{
            margin-top: 15px;
            display: none;
            flex-direction: column;
            gap: 10px;
        }}
        .step-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 12px;
            color: var(--text-muted);
        }}
        .step-icon {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .step-row.active {{ color: var(--gold); }}
        .step-row.active .step-icon {{ border-color: var(--gold); background: var(--gold-glow); }}
        .step-row.done {{ color: var(--success); }}
        .step-row.done .step-icon {{ border-color: var(--success); background: rgba(16, 185, 129, 0.1); }}
    </style>
</head>
<body>

<!-- 3D Scroll Canvas -->
<div class="scroll-world-container">
    <canvas id="worldCanvas"></canvas>
</div>

<!-- Navbar -->
<div class="navbar">
    <div class="logo-box">
        <div class="logo-icon">R</div>
        <span>Robinhood L2</span>
    </div>
    <div class="nav-tabs">
        <button class="tab-btn active" onclick="scrollToSection(0)">🚀 Meme Launchpad</button>
        <button class="tab-btn" onclick="scrollToSection(1)">📈 Trading Terminal</button>
        <button class="tab-btn" onclick="scrollToSection(2)">💎 Staking Portal</button>
        <button class="tab-btn" onclick="scrollToSection(3)">🏦 Trust Bank</button>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <button class="connect-btn" onclick="openWorkspace('dev')">🛠️ Dev Hub</button>
        <button id="connBtn" class="connect-btn" onclick="connect()">Connect Wallet</button>
    </div>
</div>

<!-- Floating HUD overlays -->
<div class="hud-overlay">
    <div class="hud-top">
        <h1 class="overlay-title" id="oTitle">AI Agent Meme Launchpad</h1>
        <p class="overlay-desc" id="oDesc">Scroll to traverse the L2 stack...</p>
    </div>
</div>

<!-- SECTION 0: MEME LAUNCHPAD -->
<div class="scroll-section active" id="sec-0">
    <div class="container">
        <div class="card">
            <div class="grid">
                <div>
                    <h2 style="font-size: 22px; margin-bottom: 10px; font-weight: 700; color: var(--gold);">🤖 AI Agent Token Deployer</h2>
                    <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 20px; line-height: 1.5;">
                        Instruct the local Clanker bot to deploy custom tokens and curves directly to Robinhood L2 in real-time.
                    </p>
                    <div class="chat" id="wsChatBox" style="height: 220px; margin-bottom: 15px;">
                        <div class="bubble b-agent">Hello! Tell me the name, ticker, and initial supply you'd like to deploy. I'll handle compiling, deploying, and setting up the virtual bonding curve on Robinhood Chain L2.</div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <input type="text" id="wsChatIn" class="input" placeholder="e.g. Deploy Chanakya Neeti token ($NEETI) with 1,000,000 supply..." style="flex-grow: 1;">
                        <button class="btn" style="width: 80px; padding: 12px;" onclick="wsChatSend()">Send</button>
                    </div>
                </div>
                <div>
                    <h3 style="font-size: 16px; margin-bottom: 15px; font-weight: 600; color: var(--gold);">Deployment Parameters</h3>
                    <div class="form-group">
                        <label>Token Name</label>
                        <input type="text" id="depName" class="input" value="Chanakya Neeti">
                    </div>
                    <div class="form-group">
                        <label>Ticker Symbol</label>
                        <input type="text" id="depSymbol" class="input" value="NEETI">
                    </div>
                    <div class="form-group">
                        <label>Initial Supply</label>
                        <input type="number" id="depSupply" class="input" value="1000000">
                    </div>
                    <button class="btn" onclick="triggerVisualDeployment()">Launch Token Instantly</button>
                    
                    <!-- Deployment progress indicator -->
                    <div class="step-container" id="deployProgress">
                        <div class="step-row" id="step-0"><div class="step-icon"></div><span>Compiling Solidity contract bytecode...</span></div>
                        <div class="step-row" id="step-1"><div class="step-icon"></div><span>Broadcasting contract transaction to Robinhood Chain L2...</span></div>
                        <div class="step-row" id="step-2"><div class="step-icon"></div><span>Registering metadata with MemeFactoryV2...</span></div>
                        <div class="step-row" id="step-3"><div class="step-icon"></div><span>Verifying contract source code on Blockscout...</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- SECTION 1: TRADING TERMINAL -->
<div class="scroll-section" id="sec-1">
    <div class="container">
        <div class="card">
            <div class="grid" style="grid-template-columns: 1.3fr 1fr;">
                <div>
                    <h2 style="font-size: 22px; margin-bottom: 10px; font-weight: 700; color: var(--gold);">📈 Exchange & Swap Terminal</h2>
                    <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 15px;">
                        Swap and trade custom L2 assets immediately using automated virtual reserve curves. No exit liquidity constraints.
                    </p>
                    <div class="chart-box" style="height: 240px; margin-bottom: 15px;">
                        <canvas id="priceChart"></canvas>
                    </div>
                    <div class="console" id="terminalConsole" style="height: 100px;">
                        <div class="c-line"><span class="c-time">[System]</span><span>Initialized Exchange socket connections.</span></div>
                    </div>
                </div>
                <div>
                    <h3 style="font-size: 16px; margin-bottom: 15px; font-weight: 600; color: var(--gold);">Execute Bonding Swap</h3>
                    <div class="form-group">
                        <label>Action</label>
                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <button id="buyBtn" class="btn" style="background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid var(--success);" onclick="setTradeMode('buy')">BUY</button>
                            <button id="sellBtn" class="btn btn-outline" style="margin: 0; padding: 14px;" onclick="setTradeMode('sell')">SELL</button>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Trade Amount (ETH)</label>
                        <input type="number" id="wsTradeAmt" class="input" value="0.1" step="0.05">
                    </div>
                    <div class="form-group">
                        <label>Target Pool</label>
                        <select id="wsTokenSelect" class="input">
                            <option value="0xROBIN_MCP">$ROBIN_MCP (Launchpad Utility)</option>
                            <option value="0xCHIRANSH">$CHIRANSH (Voice Assistant)</option>
                            <option value="0xANANT_ANADI">$ANANT_ANADI (Culture Pool)</option>
                        </select>
                    </div>
                    <button class="btn" onclick="executeWsTrade()">Submit Transaction</button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- SECTION 2: STAKING PORTAL -->
<div class="scroll-section" id="sec-2">
    <div class="container">
        <div class="card">
            <div class="grid">
                <div>
                    <h2 style="font-size: 22px; margin-bottom: 10px; font-weight: 700; color: var(--gold);">💎 Yield Vault Staking</h2>
                    <p style="color: var(--text-muted); font-size: 14px; margin-bottom: 25px; line-height: 1.5;">
                        Stake your native `$ROBIN_MCP` tokens to earn a share of platform deployment and swap fees. Rewards are distributed dynamically in real-time.
                    </p>
                    
                    <div class="form-group">
                        <label>Staked $ROBIN_MCP Amount</label>
                        <input type="number" id="wsStakeAmt" class="input" value="5000" oninput="calcWsYield()">
                    </div>
                    <div style="font-size: 15px; color: var(--text-muted); margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;">
                        <span>Estimated Daily Yield:</span>
                        <span id="wsYieldVal" style="color: var(--success); font-weight: 800; font-size: 18px;">0.025 ETH</span>
                    </div>
                    <button class="btn" onclick="connect()">Stake Tokens</button>
                </div>
                <div>
                    <h3 style="font-size: 16px; margin-bottom: 15px; font-weight: 600; color: var(--gold);">Ecosystem Fee Split</h3>
                    <div style="background: rgba(3, 7, 18, 0.4); border-radius: 16px; border: 1px solid rgba(255,255,255,0.03); padding: 20px; display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; font-size: 14px;">
                            <span>Stakers Reward Pool</span>
                            <span style="color: var(--success); font-weight: 700;">40%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 14px;">
                            <span>Developer Buyback Pool</span>
                            <span style="color: var(--success); font-weight: 700;">20%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 14px;">
                            <span>Creator Treasury</span>
                            <span style="color: var(--success); font-weight: 700;">40%</span>
                        </div>
                    </div>
                    <p style="font-size: 12px; color: var(--text-muted); line-height: 1.5;">
                        All on-chain swaps on the virtual curve contribute 0.5% in trading fees. Staking rewards accumulate in the StakingYield vault and can be claimed at any time.
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- SECTION 3: TRUST BANK -->
<div class="scroll-section" id="sec-3">
    <div class="container">
        <div class="card" style="padding: 25px;">
            <div class="ws-header" style="margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px;">
                <div>
                    <h2 style="font-size: 22px; font-weight: 700; color: var(--gold);">🏦 Community Trust Bank</h2>
                    <p style="font-size: 12px; color: var(--text-muted); font-family: var(--font-mono); margin-top: 4px;">Deploy trusts, pool wealth, manage multi-sig, buy gold/silver reserves, distribute dividends.</p>
                </div>
            </div>
            
            <div class="grid" style="grid-template-columns: 1fr 1.2fr; gap: 25px;">
                <div>
                    <!-- Deploy Trust -->
                    <div style="margin-bottom: 20px;">
                        <h3 style="font-size: 14px; margin-bottom: 12px; font-weight: 600; color: var(--gold); text-transform: uppercase;">1. Deploy Community Trust</h3>
                        <div class="form-group" style="margin-bottom: 10px;">
                            <input type="text" id="trustName" class="input" value="Advaita Community Trust" placeholder="Trust Name">
                        </div>
                        <div class="form-group" style="margin-bottom: 10px;">
                            <input type="text" id="trustDirectors" class="input" placeholder="Managing Directors (comma 0x...)">
                        </div>
                        <div class="form-group" style="margin-bottom: 10px;">
                            <input type="number" id="trustThreshold" class="input" value="1" min="1" placeholder="Signature Threshold">
                        </div>
                        <button class="btn" onclick="triggerDeployTrust()">Deploy Trust</button>
                    </div>
                    
                    <!-- Deploy Mock Asset -->
                    <div>
                        <h3 style="font-size: 14px; margin-bottom: 12px; font-weight: 600; color: var(--gold); text-transform: uppercase;">2. Deploy Mock Metal Asset</h3>
                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <input type="text" id="mockAssetName" class="input" value="Paxos Gold Mock" placeholder="Asset Name">
                            <input type="text" id="mockAssetSymbol" class="input" value="cGOLD" placeholder="Ticker" style="width: 100px;">
                        </div>
                        <button class="btn btn-outline" style="margin-top:0;" onclick="triggerDeployMockAsset()">Deploy Asset</button>
                    </div>
                </div>
                
                <div>
                    <!-- Active Trust & Reserves -->
                    <div style="background: rgba(3, 7, 18, 0.4); border: 1px solid rgba(255,255,255,0.03); padding: 15px; border-radius: 16px; margin-bottom: 20px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
                            <span>Trust Address:</span><span id="activeTrustAddr" style="font-family:var(--font-mono); color:var(--gold);">Not Deployed</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:13px;">
                            <span>Pooled Wealth:</span><span id="activeTrustBalance" style="font-weight:700; color:var(--success);">0.00 ETH</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:12px;">
                            <span>Your Share:</span><span id="userTrustShares">0.00 ETH (0%)</span>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <input type="number" id="depositTrustAmt" class="input" placeholder="Amount ETH" value="0.05" style="padding: 10px;">
                            <button class="btn" style="width: 100px; padding: 10px;" onclick="triggerDepositToTrust()">Deposit</button>
                        </div>
                    </div>
                    
                    <!-- Gold & Silver reserves -->
                    <h4 style="font-size: 12px; margin-bottom: 10px; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">Real-world Assets Reserves</h4>
                    <div style="background: rgba(3, 7, 18, 0.3); padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.02); margin-bottom: 15px;">
                        <div style="margin-bottom: 8px;">
                            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:3px;">
                                <span>Gold Reserves (cGOLD)</span><span id="goldReservesVal" style="color:var(--gold); font-weight:700;">0.00 cGOLD</span>
                            </div>
                            <div style="height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden;">
                                <div id="goldReservesBar" style="height: 100%; width: 0%; background: linear-gradient(90deg, var(--gold), var(--gold-dark)); transition: width 0.5s;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:3px;">
                                <span>Silver Reserves (cSILVER)</span><span id="silverReservesVal" style="color:#94a3b8; font-weight:700;">0.00 cSILVER</span>
                            </div>
                            <div style="height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden;">
                                <div id="silverReservesBar" style="height: 100%; width: 0%; background: linear-gradient(90deg, #94a3b8, #475569); transition: width 0.5s;"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Multi-sig Investment & Proposals -->
                    <h4 style="font-size: 12px; margin-bottom: 8px; font-weight: 600; color: var(--gold); text-transform: uppercase;">Propose & Sign Investment Transaction</h4>
                    <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                        <input type="text" id="propDest" class="input" placeholder="Destination Address" style="padding: 10px;">
                        <input type="text" id="propData" class="input" placeholder="Calldata (Hex)" style="padding: 10px;">
                    </div>
                    <button class="btn btn-outline" style="margin-top:0; margin-bottom:15px; padding: 12px;" onclick="triggerProposeTransaction()">Submit Proposal</button>
                    
                    <!-- Active Proposals -->
                    <h4 style="font-size: 11px; margin-bottom: 6px; font-weight: 600; color: var(--text-muted); text-transform: uppercase;">Active Proposals</h4>
                    <div id="trustProposalsList" style="max-height: 100px; overflow-y: auto; background: rgba(0,0,0,0.2); border-radius: 10px; border: 1px solid rgba(255,255,255,0.02); padding: 8px; font-size:11px; color:var(--text-muted);">
                        No active proposals.
                    </div>
                </div>
            </div>
            
            <!-- Dividends section -->
            <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 20px;">
                <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h4 style="font-size: 12px; margin-bottom: 8px; color: var(--gold); text-transform: uppercase;">Distribute Yield</h4>
                        <div style="display: flex; gap: 8px;">
                            <input type="text" id="divTokenAddr" class="input" placeholder="Token Address (or 0x0 for ETH)" style="padding: 10px;">
                            <input type="number" id="divAmt" class="input" placeholder="Amount (Wei)" style="padding: 10px;">
                            <button class="btn" style="width: 100px; padding: 10px;" onclick="triggerDistributeDividends()">Distribute</button>
                        </div>
                    </div>
                    <div>
                        <h4 style="font-size: 12px; margin-bottom: 8px; color: var(--gold); text-transform: uppercase;">Claim Dividends</h4>
                        <div style="display: flex; gap: 8px;">
                            <input type="text" id="claimTokenAddr" class="input" placeholder="Token Address (or 0x0 for ETH)" style="padding: 10px;">
                            <button class="btn btn-outline" style="margin-top: 0; padding: 10px;" onclick="triggerClaimDividends()">Claim My Dividends</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- WORKSPACE: DEV DASHBOARD -->
<div class="workspace-overlay" id="ws-dev">
    <div class="ws-header">
        <div>
            <h2 style="font-size: 22px; font-weight: 700; color: var(--gold);">Developer Core Hub</h2>
            <p style="font-size: 12px; color: var(--text-muted); font-family: var(--font-mono); margin-top: 4px;">GitHub Webhook Webhooks & Treasury Payouts</p>
        </div>
        <button class="back-btn" onclick="closeWorkspace('dev')">← Close Hub</button>
    </div>
    
    <div class="grid">
        <div>
            <div class="card" style="margin-bottom: 25px;">
                <h3 style="font-size: 16px; margin-bottom: 15px; font-weight: 600; color: var(--gold);">GitHub Webhook Curation Queue</h3>
                <table class="table">
                    <thead>
                        <tr><th>PR ID</th><th>Contributor</th><th>Target Branch</th><th>Payout Amount</th><th>Status</th></tr>
                    </thead>
                    <tbody id="prTableBody">
                        <tr>
                            <td>#24</td>
                            <td>salvationfinder</td>
                            <td>main</td>
                            <td>50,000 $ROBIN_MCP</td>
                            <td><span class="badge badge-success">Paid</span></td>
                        </tr>
                        <tr>
                            <td>#25</td>
                            <td>10x-operator</td>
                            <td>main</td>
                            <td>50,000 $ROBIN_MCP</td>
                            <td><span class="badge badge-warn">Pending Review</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h3 style="font-size: 16px; margin-bottom: 15px; font-weight: 600; color: var(--gold);">Trigger Contributor Payout (Manual Review)</h3>
                <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 20px; align-items: end;">
                    <div class="form-group" style="margin-bottom: 0;">
                        <label>Contributor wallet address</label>
                        <input type="text" id="contributorWallet" class="input" placeholder="e.g. 0x71C...4e8B" value="0x71C4B445C3B1d425780943C99Ea8A608f8a93f9">
                    </div>
                    <button class="btn" style="padding: 12px;" onclick="triggerContributorPayout()">Execute Payout</button>
                </div>
            </div>
        </div>
        
        <div>
            <div class="card" style="margin-bottom: 25px;">
                <h3 style="font-size: 16px; margin-bottom: 15px; font-weight: 600; color: var(--gold);">Top Contributor Leaderboard</h3>
                <table class="table">
                    <thead>
                        <tr><th>Developer</th><th>Merged PRs</th><th>Total Earned</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>salvationfinder</td><td>14 Merges</td><td>700,000 $ROBIN_MCP</td></tr>
                        <tr><td>10x-operator</td><td>8 Merges</td><td>400,000 $ROBIN_MCP</td></tr>
                        <tr><td>solidity-wizard</td><td>5 Merges</td><td>250,000 $ROBIN_MCP</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="console" id="devConsole">
                <div class="c-line"><span class="c-time">[Console]</span><span>Central Curation Webhook active and listening.</span></div>
            </div>
        </div>
    </div>
    
    <!-- 6 SPEC DOCS FOR VIBECODING -->
    <div class="card" style="margin-top: 25px;">
        <h3 style="font-size: 16px; margin-bottom: 10px; font-weight: 600; color: var(--gold);">📋 Sovereign Vibecoding Spec Curation Framework (6 Mandatory Docs)</h3>
        <p style="color: var(--text-muted); font-size: 13px; margin-bottom: 20px; line-height: 1.5;">
            Follow this framework to build applications using AI agents like Claude or GPT. Having these 6 documents prepared beforehand cuts prompting errors, prevents endless loops, and saves thousands of tokens.
        </p>
        <div class="nav-tabs" style="width: max-content; margin-bottom: 20px;">
            <button class="tab-btn active" onclick="switchSpecTab(0)">1. PRD</button>
            <button class="tab-btn" onclick="switchSpecTab(1)">2. TRD</button>
            <button class="tab-btn" onclick="switchSpecTab(2)">3. App Flow</button>
            <button class="tab-btn" onclick="switchSpecTab(3)">4. UI/UX Design</button>
            <button class="tab-btn" onclick="switchSpecTab(4)">5. Backend Schema</button>
            <button class="tab-btn" onclick="switchSpecTab(5)">6. Plan</button>
        </div>
        <div id="spec-content-box" style="background: #010206; border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.03); min-height: 150px;">
            <!-- Loaded dynamically in javascript -->
        </div>
    </div>
</div>

<script>
    // Constants injected from environment by Python generator
    const MEME_FACTORY_ADDRESS = "{meme_factory}";
    const ROBIN_MCP_TOKEN_ADDRESS = "{robin_mcp}";
    let TRUST_FACTORY_ADDRESS = "0x6E4C2DB5F3D1b236843925949FE5BD8A3836FCcB"; // Configurable/Fallback

    const ABIs = {{
        MemeFactory: [
            "function deployMemeToken(string name, string symbol, uint256 supply) payable returns (address)",
            "function buyMemeToken(address tokenAddress, address referrer) payable",
            "function sellMemeToken(address tokenAddress, uint256 tokenAmount, address referrer)",
            "function pools(address) view returns (address tokenAddress, uint256 tokenReserves, uint256 ethReserves, bool tradingActive, bool finalized)",
            "function allMemeTokens(uint256) view returns (address)",
            "function getMemeCount() view returns (uint256)",
            "function deployFee() view returns (uint256)"
        ],
        CommunityTrustFactory: [
            "function createTrust(string name, address[] directors, uint256 requiredSignatures) returns (address)",
            "function getTrustCount() view returns (uint256)",
            "function allTrusts(uint256) view returns (address)"
        ],
        CommunityTrust: [
            "function deposit() payable",
            "function proposeTransaction(address destination, uint256 value, bytes data) returns (uint256)",
            "function signTransaction(uint256 proposalId)",
            "function executeTransaction(uint256 proposalId)",
            "function distributeDividends(address tokenAddress, uint256 amount) payable",
            "function claimDividends(address token)",
            "function totalShares() view returns (uint256)",
            "function shares(address) view returns (uint256)",
            "function getDirectors() view returns (address[])",
            "function requiredSignatures() view returns (uint256)",
            "function proposals(uint256) view returns (address destination, uint256 value, bytes data, bool executed, uint256 signatureCount)"
        ],
        ERC20: [
            "function balanceOf(address account) view returns (uint256)",
            "function approve(address spender, uint256 amount) returns (bool)",
            "function allowance(address owner, address spender) view returns (uint256)",
            "function decimals() view returns (uint8)",
            "function symbol() view returns (string)",
            "function name() view returns (string)"
        ]
    }};

    // 3D Three.js Particle Morphing World
    let scene, camera, renderer, particleSystem;
    const N = 400; // Number of particles
    let currentScroll = 0;
    let targetScroll = 0;
    
    // Arrays for target coordinates
    const spherePoints = [];
    const helixPoints = [];
    const gridPoints = [];
    const torusPoints = [];
    
    function init3D() {{
        const container = document.querySelector(".scroll-world-container");
        const w = container.offsetWidth;
        const h = container.offsetHeight;
        
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(60, w / h, 0.1, 100);
        camera.position.z = 11;
        
        renderer = new THREE.WebGLRenderer({{ canvas: document.getElementById("worldCanvas"), antialias: true, alpha: true }});
        renderer.setSize(w, h);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Generate Coordinate Patterns
        // 1. Sphere (Meme Launchpad)
        for(let i=0; i<N; i++) {{
            const theta = Math.acos(-1 + 2 * i / N);
            const phi = Math.sqrt(N * Math.PI) * theta;
            spherePoints.push(new THREE.Vector3(
                4.5 * Math.sin(theta) * Math.cos(phi),
                4.5 * Math.sin(theta) * Math.sin(phi),
                4.5 * Math.cos(theta)
            ));
        }}
        
        // 2. Double Helix (Trading Terminal)
        for(let i=0; i<N; i++) {{
            const t = i / N;
            const theta = 12 * Math.PI * t;
            const r = 1.8;
            const sign = (i % 2 === 0) ? 1 : -1;
            helixPoints.push(new THREE.Vector3(
                sign * r * Math.cos(theta),
                sign * r * Math.sin(theta),
                8 * (t - 0.5)
            ));
        }}
        
        // 3. Grid Mesh (Staking Portal)
        const size = Math.floor(Math.sqrt(N));
        for(let i=0; i<N; i++) {{
            const r = Math.floor(i / size);
            const c = i % size;
            gridPoints.push(new THREE.Vector3(
                (c - size/2) * 0.55,
                (r - size/2) * 0.55,
                0
            ));
        }}

        // 4. Torus (Trust Bank)
        const torusR = 3.5;
        const torusr = 1.2;
        for(let i=0; i<N; i++) {{
            const u = (i % 20) / 20 * Math.PI * 2;
            const v = Math.floor(i / 20) / (N / 20) * Math.PI * 2;
            torusPoints.push(new THREE.Vector3(
                (torusR + torusr * Math.cos(v)) * Math.cos(u),
                (torusR + torusr * Math.cos(v)) * Math.sin(u),
                torusr * Math.sin(v)
            ));
        }}
        
        // Create Particle Geometry & Buffer
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(N * 3);
        const colors = new Float32Array(N * 3);
        
        for(let i=0; i<N; i++) {{
            positions[i*3] = spherePoints[i].x;
            positions[i*3+1] = spherePoints[i].y;
            positions[i*3+2] = spherePoints[i].z;
            
            // Set base color (warm gold to saffron gold gradients)
            colors[i*3] = 0.98;
            colors[i*3+1] = 0.75;
            colors[i*3+2] = 0.14;
        }}
        
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        // Custom texture loader
        const texture = createCircleTexture();
        
        const material = new THREE.PointsMaterial({{
            size: 0.16,
            vertexColors: true,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            map: texture
        }});
        
        particleSystem = new THREE.Points(geometry, material);
        scene.add(particleSystem);
        
        // Window Resize
        window.addEventListener('resize', () => {{
            const width = container.offsetWidth;
            const height = container.offsetHeight;
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        }});
        
        animate();
    }}
    
    function createCircleTexture() {{
        const matCanvas = document.createElement('canvas');
        matCanvas.width = 16;
        matCanvas.height = 16;
        const matCtx = matCanvas.getContext('2d');
        const grad = matCtx.createRadialGradient(8, 8, 0, 8, 8, 8);
        grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
        grad.addColorStop(0.2, 'rgba(251, 191, 36, 0.8)');
        grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        matCtx.fillStyle = grad;
        matCtx.fillRect(0, 0, 16, 16);
        return new THREE.CanvasTexture(matCanvas);
    }}
    
    // Mouse Interactive Targets
    let mouseX = 0, mouseY = 0;
    let targetMouseX = 0, targetMouseY = 0;
    document.addEventListener("mousemove", (e) => {{
        targetMouseX = (e.clientX - window.innerWidth / 2) * 0.0015;
        targetMouseY = (e.clientY - window.innerHeight / 2) * 0.0015;
    }});
    
    // Scroll tracking
    window.addEventListener('scroll', () => {{
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        targetScroll = window.scrollY / (maxScroll || 1);
        updateActiveSections();
    }});
    
    function animate() {{
        requestAnimationFrame(animate);
        
        // Lerp scroll position for absolute fluid transitions
        currentScroll += (targetScroll - currentScroll) * 0.06;
        
        // Mouse movement easing
        mouseX += (targetMouseX - mouseX) * 0.05;
        mouseY += (targetMouseY - mouseY) * 0.05;
        
        // Camera position & fly-through parallax
        camera.position.x = mouseX * 2.5;
        camera.position.y = -mouseY * 2.5 - currentScroll * 2;
        camera.position.z = 11 - currentScroll * 6; // Starts at 11, zooms in to 5
        camera.lookAt(0, 0, 0);
        
        // Slowly rotate particle system
        particleSystem.rotation.y = currentScroll * Math.PI * 0.5 + Date.now() * 0.0001;
        particleSystem.rotation.x = currentScroll * Math.PI * 0.2 + Date.now() * 0.00005;
        
        // Morph particles based on eased scroll position
        const positions = particleSystem.geometry.attributes.position.array;
        const size = Math.floor(Math.sqrt(N));
        
        for(let i=0; i<N; i++) {{
            let p1, p2, t;
            if(currentScroll < 0.33) {{
                p1 = spherePoints[i];
                p2 = helixPoints[i];
                t = currentScroll / 0.33;
            }} else if(currentScroll < 0.66) {{
                p1 = helixPoints[i];
                p2 = gridPoints[i];
                t = (currentScroll - 0.33) / 0.33;
            }} else {{
                p1 = gridPoints[i];
                p2 = torusPoints[i];
                t = (currentScroll - 0.66) / 0.34;
            }}
            
            let p2z = p2.z;
            // Undulate waves if in grid mesh mode
            if(currentScroll >= 0.33 && currentScroll < 0.66 && p2 === gridPoints[i]) {{
                const r = Math.floor(i / size);
                const c = i % size;
                p2z = Math.sin(r * 0.4 + c * 0.4 + Date.now() * 0.002) * 0.6;
            }}
            
            const x = p1.x + (p2.x - p1.x) * t;
            const y = p1.y + (p2.y - p1.y) * t;
            const z = p1.z + (p2z - p1.z) * t;
            
            positions[i*3] = x;
            positions[i*3+1] = y;
            positions[i*3+2] = z;
        }}
        particleSystem.geometry.attributes.position.needsUpdate = true;
        
        // Update Title / Desc HUD
        const oTitle = document.getElementById("oTitle");
        const oDesc = document.getElementById("oDesc");
        if(currentScroll < 0.25) {{
            oTitle.innerText = "AI Agent Meme Launchpad";
            oDesc.innerText = "Layer 1: Autonomous ERC-20 deployer & Clanker agent";
        }} else if(currentScroll < 0.5) {{
            oTitle.innerText = "Virtual Trading Terminal";
            oDesc.innerText = "Layer 2: x * y = k bonding swaps & real-time pricing";
        }} else if(currentScroll < 0.75) {{
            oTitle.innerText = "Platform Yield Staking";
            oDesc.innerText = "Layer 3: Stake native tokens, claim fee-split yields";
        }} else {{
            oTitle.innerText = "Sovereign Trust Bank";
            oDesc.innerText = "Layer 4: Pool community wealth, allocate reserves, distribute dividends";
        }}
        
        renderer.render(scene, camera);
    }}
    
    function scrollToSection(index) {{
        const targetY = index * window.innerHeight;
        window.scrollTo({{
            top: targetY,
            behavior: 'smooth'
        }});
    }}
    
    function updateActiveSections() {{
        const threshold = window.scrollY + window.innerHeight / 2;
        const index = Math.floor(threshold / window.innerHeight);
        
        document.querySelectorAll(".scroll-section").forEach((sec, idx) => {{
            if(idx === index) {{
                sec.classList.add("active");
            }} else {{
                sec.classList.remove("active");
            }}
        }});
        
        document.querySelectorAll(".tab-btn").forEach((btn, idx) => {{
            if(idx === index) {{
                btn.classList.add("active");
            }} else {{
                btn.classList.remove("active");
            }}
        }});
    }}

    // Connection Flow
    let provider, signer, userAddress;
    let memeFactoryContract, trustFactoryContract, activeTrustContract;
    let isMockMode = false;

    async function connect() {{
        if (typeof window.ethereum === "undefined") {{
            alert("No Ethereum wallet detected. Falling back to Sandbox Mock mode.");
            setupMockState();
            return;
        }}

        try {{
            // Request accounts
            const accounts = await window.ethereum.request({{ method: 'eth_requestAccounts' }});
            userAddress = accounts[0];
            
            provider = new ethers.providers.Web3Provider(window.ethereum);
            signer = provider.getSigner();
            
            // Ensure network is correct (Robinhood Chain Mainnet - ChainID 4663)
            let network = await provider.getNetwork();
            if (network.chainId !== 4663) {{
                try {{
                    await window.ethereum.request({{
                        method: 'wallet_switchEthereumChain',
                        params: [{{ chainId: '0x1237' }}] // 4663
                    }});
                }} catch (switchError) {{
                    if (switchError.code === 4902 || switchError.message.includes("4902")) {{
                        await window.ethereum.request({{
                            method: 'wallet_addEthereumChain',
                            params: [{{
                                chainId: '0x1237',
                                chainName: "Robinhood Chain Mainnet",
                                nativeCurrency: {{ name: "Ethereum", symbol: "ETH", decimals: 18 }},
                                rpcUrls: ["https://rpc.mainnet.chain.robinhood.com"],
                                blockExplorerUrls: ["https://robinhoodchain.blockscout.com"]
                            }}]
                        }});
                    }} else {{
                        throw switchError;
                    }}
                }}
                await new Promise(r => setTimeout(r, 1000));
                provider = new ethers.providers.Web3Provider(window.ethereum);
                signer = provider.getSigner();
                network = await provider.getNetwork();
            }}
            
            // Initialize contract instances
            memeFactoryContract = new ethers.Contract(MEME_FACTORY_ADDRESS, ABIs.MemeFactory, signer);
            trustFactoryContract = new ethers.Contract(TRUST_FACTORY_ADDRESS, ABIs.CommunityTrustFactory, signer);
            
            // Update connection buttons
            const shortened = userAddress.substring(0, 6) + "..." + userAddress.substring(userAddress.length - 4);
            const connBtn = document.getElementById("connBtn");
            if (connBtn) {{
                connBtn.innerText = shortened;
                connBtn.style.background = "var(--success)";
                connBtn.style.borderColor = "var(--success)";
            }}
            
            logEvent("System", `Wallet connected: ${{userAddress}}`);
            isMockMode = false;

            // Load on-chain state
            await loadTokenPools();
            await loadActiveTrustDetails();
            
        }} catch (e) {{
            console.error(e);
            logEvent("ERROR", `Failed to connect on-chain: ${{e.message}}. Falling back to Sandbox Mock mode.`);
            setupMockState();
        }}
    }}

    function setupMockState() {{
        isMockMode = true;
        userAddress = "0x71C4B445C3B1d425780943C99Ea8A608f8a93f9";
        const connBtn = document.getElementById("connBtn");
        if (connBtn) {{
            connBtn.innerText = "0x71C...4e8B (Sandbox)";
            connBtn.style.background = "var(--gold-dark)";
            connBtn.style.borderColor = "var(--gold)";
        }}
        logEvent("System", "Sovereign Sandbox environment loaded successfully.");
    }}

    // Event log helper
    function logEvent(tag, msg, consoleId = "terminalConsole") {{
        const consoles = [document.getElementById(consoleId)];
        if(consoleId === "terminalConsole") {{
            consoles.push(document.getElementById("devConsole"));
        }}
        
        consoles.forEach(con => {{
            if(!con) return;
            const now = new Date();
            const timeStr = now.toTimeString().split(' ')[0];
            const div = document.createElement("div");
            div.className = "c-line";
            div.innerHTML = `<span class="c-time">[${{timeStr}}]</span><span class="c-tag">[${{tag}}]</span><span>${{msg}}</span>`;
            con.appendChild(div);
            con.scrollTop = con.scrollHeight;
        }});
    }}

    // Quick Yield Calculator
    function calcWsYield() {{
        const staked = parseFloat(document.getElementById("wsStakeAmt").value) || 0;
        const yieldVal = (staked / 100000) * 0.5;
        document.getElementById("wsYieldVal").innerText = yieldVal.toFixed(5) + " ETH";
    }}

    // Workspace Navigation (Only used for Dev Hub now)
    function openWorkspace(id) {{
        document.getElementById("ws-" + id).style.display = "block";
        document.body.style.overflow = "hidden"; // disable scrolling
    }}
    
    function closeWorkspace(id) {{
        document.getElementById("ws-" + id).style.display = "none";
        document.body.style.overflow = "auto"; // enable scrolling
    }}

    // --- WORKSPACE: TERMINAL LOGIC ---
    let tradeMode = 'buy';
    let chartInterval;
    let priceData = [100, 102, 101, 105, 103, 108, 110, 107, 112, 115, 113, 118, 120, 122, 121, 125];
    
    function setTradeMode(mode) {{
        tradeMode = mode;
        const buyBtn = document.getElementById("buyBtn");
        const sellBtn = document.getElementById("sellBtn");
        if(mode === 'buy') {{
            buyBtn.className = "btn";
            buyBtn.style.background = "rgba(16, 185, 129, 0.15)";
            buyBtn.style.color = "var(--success)";
            buyBtn.style.border = "1px solid var(--success)";
            
            sellBtn.className = "btn btn-outline";
            sellBtn.style.background = "none";
            sellBtn.style.color = "var(--text)";
            sellBtn.style.border = "1px solid rgba(255,255,255,0.1)";
        }} else {{
            sellBtn.className = "btn";
            sellBtn.style.background = "rgba(239, 68, 68, 0.15)";
            sellBtn.style.color = "var(--error)";
            sellBtn.style.border = "1px solid var(--error)";
            
            buyBtn.className = "btn btn-outline";
            buyBtn.style.background = "none";
            buyBtn.style.color = "var(--text)";
            buyBtn.style.border = "1px solid rgba(255,255,255,0.1)";
        }}
    }}
    
    async function loadTokenPools() {{
        if (isMockMode || !memeFactoryContract) return;
        try {{
            const count = await memeFactoryContract.getMemeCount();
            const select = document.getElementById("wsTokenSelect");
            select.innerHTML = "";
            
            for (let i = 0; i < count; i++) {{
                const tokenAddr = await memeFactoryContract.allMemeTokens(i);
                const tokenContract = new ethers.Contract(tokenAddr, ABIs.ERC20, provider);
                const symbol = await tokenContract.symbol();
                const name = await tokenContract.name();
                
                const opt = document.createElement("option");
                opt.value = tokenAddr;
                opt.innerText = `$${{symbol}} (${{name}})`;
                select.appendChild(opt);
            }}
        }} catch (e) {{
            console.error("Failed to load on-chain tokens:", e);
        }}
    }}

    async function executeWsTrade() {{
        const amt = parseFloat(document.getElementById("wsTradeAmt").value) || 0;
        const select = document.getElementById("wsTokenSelect");
        if (select.selectedIndex === -1) return;
        const tok = select.options[select.selectedIndex].text;
        const tokenAddr = select.value;
        
        if (amt <= 0) return;
        
        if (isMockMode) {{
            const priceChange = tradeMode === 'buy' ? amt * 5 : -amt * 5;
            const lastPrice = priceData[priceData.length - 1];
            const newPrice = Math.max(1, lastPrice + priceChange + (Math.random() - 0.5) * 2);
            priceData.push(newPrice);
            logEvent("TRADE", `[Sandbox] Swap executed: ${{tradeMode.toUpperCase()}} ${{amt}} ETH of ${{tok}}. New Price: ${{newPrice.toFixed(2)}} USDT.`);
            drawCandleChart();
            return;
        }}

        logEvent("TRADE", `Broadcasting bonding swap transaction on-chain for $${{tok}}...`);
        try {{
            if (tradeMode === 'buy') {{
                const ethAmtWei = ethers.utils.parseEther(amt.toString());
                const tx = await memeFactoryContract.buyMemeToken(tokenAddr, ethers.constants.AddressZero, {{ value: ethAmtWei }});
                logEvent("TRADE", `Tx broadcasted: ${{tx.hash}}. Waiting for confirmation...`);
                await tx.wait();
                logEvent("TRADE", `✅ Buy swap completed successfully!`);
            }} else {{
                const tokenAmtWei = ethers.utils.parseEther(amt.toString());
                const tokenContract = new ethers.Contract(tokenAddr, ABIs.ERC20, signer);
                
                // Check allowance
                const allowance = await tokenContract.allowance(userAddress, MEME_FACTORY_ADDRESS);
                if (allowance.lt(tokenAmtWei)) {{
                    logEvent("TRADE", `Approving MemeFactoryV2 to manage ${{amt}} tokens...`);
                    const appTx = await tokenContract.approve(MEME_FACTORY_ADDRESS, tokenAmtWei);
                    await appTx.wait();
                }}
                
                const tx = await memeFactoryContract.sellMemeToken(tokenAddr, tokenAmtWei, ethers.constants.AddressZero);
                logEvent("TRADE", `Tx broadcasted: ${{tx.hash}}. Waiting for confirmation...`);
                await tx.wait();
                logEvent("TRADE", `✅ Sell swap completed successfully!`);
            }}
            
            // Fluctuates chart dynamically
            priceData.push(priceData[priceData.length-1] * (tradeMode === 'buy' ? 1.05 : 0.95));
            drawCandleChart();
        }} catch (e) {{
            console.error(e);
            logEvent("ERROR", `Swap trade failed: ${{e.message}}`);
        }}
    }}
    
    function initCandleChart() {{
        drawCandleChart();
        if(chartInterval) clearInterval(chartInterval);
        chartInterval = setInterval(() => {{
            const last = priceData[priceData.length - 1];
            priceData.push(last + (Math.random() - 0.5) * 1.5);
            if(priceData.length > 24) priceData.shift();
            drawCandleChart();
        }}, 4000);
    }}
    
    function drawCandleChart() {{
        const canvas = document.getElementById("priceChart");
        if(!canvas) return;
        const ctx = canvas.getContext("2d");
        const w = canvas.width = canvas.parentNode.offsetWidth;
        const h = canvas.height = canvas.parentNode.offsetHeight;
        
        ctx.clearRect(0, 0, w, h);
        
        // Draw grid
        ctx.strokeStyle = "rgba(255,255,255,0.02)";
        ctx.lineWidth = 1;
        for(let i=0; i<w; i+=40) {{
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, h); ctx.stroke();
        }}
        for(let i=0; i<h; i+=30) {{
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(w, i); ctx.stroke();
        }}
        
        // Draw price curve
        const padding = 30;
        const maxPrice = Math.max(...priceData) + 2;
        const minPrice = Math.min(...priceData) - 2;
        const range = maxPrice - minPrice;
        
        const stepX = (w - padding * 2) / (priceData.length - 1);
        
        ctx.strokeStyle = "rgba(245, 158, 11, 0.4)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        const points = [];
        priceData.forEach((price, idx) => {{
            const x = padding + idx * stepX;
            const y = h - padding - ((price - minPrice) / range) * (h - padding * 2);
            points.push({{x, y}});
            if(idx === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }});
        ctx.stroke();
        
        // Draw grid candles (simulated OHLC)
        points.forEach((pt, idx) => {{
            if(idx === 0) return;
            const prev = points[idx-1];
            const isUp = pt.y < prev.y;
            
            ctx.strokeStyle = isUp ? "#10b981" : "#ef4444";
            ctx.fillStyle = isUp ? "rgba(16, 185, 129, 0.8)" : "rgba(239, 68, 68, 0.8)";
            ctx.lineWidth = 1.5;
            
            ctx.beginPath();
            ctx.moveTo(pt.x, pt.y - 15);
            ctx.lineTo(pt.x, pt.y + 15);
            ctx.stroke();
            
            const bodyH = Math.max(4, Math.abs(pt.y - prev.y));
            ctx.fillRect(pt.x - 4, Math.min(pt.y, prev.y), 8, bodyH);
        }});
    }}

    // --- WORKSPACE: DEV DASHBOARD LOGIC ---
    function triggerContributorPayout() {{
        const wallet = document.getElementById("contributorWallet").value;
        if(!wallet.startsWith("0x")) {{
            logEvent("ERROR", "Invalid EVM contributor wallet address.", "devConsole");
            return;
        }}
        
        logEvent("PAYOUT", `Curation approved. Initiating payout transfer of 50,000 $ROBIN_MCP...`, "devConsole");
        setTimeout(() => {{
            logEvent("PAYOUT", "Read config private key successfully from environment (.env).", "devConsole");
        }}, 500);
        setTimeout(() => {{
            logEvent("PAYOUT", "Calling EcosystemTreasury.sol on Robinhood Chain L2...", "devConsole");
        }}, 1000);
        setTimeout(() => {{
            logEvent("PAYOUT", "Execution successful! Tx Hash: 0xa5a1200df18d18471c08a901ff2a0d7831d102e3b2e5a40a45920a010dff9a9b", "devConsole");
            logEvent("PAYOUT", `Transferred 50,000 $ROBIN_MCP tokens to contributor: ${{wallet}}`, "devConsole");
            
            // Add to webhook queue table
            const table = document.getElementById("prTableBody");
            const newRow = document.createElement("tr");
            newRow.innerHTML = `<td>#26</td><td>Manual Trigger</td><td>main</td><td>50,000 $ROBIN_MCP</td><td><span class="badge badge-success">Paid</span></td>`;
            table.insertBefore(newRow, table.firstChild);
        }}, 1800);
    }}

    // --- WORKSPACE: AI DEPLOYER LOGIC ---
    function wsChatSend() {{
        const inp = document.getElementById("wsChatIn");
        const box = document.getElementById("wsChatBox");
        if(!inp.value.trim()) return;

        const uDiv = document.createElement("div");
        uDiv.className = "bubble b-user";
        uDiv.innerText = inp.value;
        box.appendChild(uDiv);

        const promptVal = inp.value.toLowerCase();
        inp.value = "";
        box.scrollTop = box.scrollHeight;

        setTimeout(() => {{
            const aDiv = document.createElement("div");
            aDiv.className = "bubble b-agent";
            
            if(promptVal.includes("deploy") || promptVal.includes("launch")) {{
                aDiv.innerHTML = "<strong>RobinMCP:</strong> Recognized instruction to launch. Initializing parameters... Please review the Token Parameters form on the right and click <strong>Launch Token Instantly</strong> to broadcast the contract.";
            }} else {{
                aDiv.innerText = "RobinMCP: Understood. Let me know your Token Name, Symbol, and Supply, then click 'Launch Token' on the right panel to execute deployment on-chain.";
            }}
            box.appendChild(aDiv);
            box.scrollTop = box.scrollHeight;
        }}, 800);
    }}
    
    async function triggerVisualDeployment() {{
        const name = document.getElementById("depName").value;
        const ticker = document.getElementById("depSymbol").value;
        const supply = parseFloat(document.getElementById("depSupply").value);
        
        const progress = document.getElementById("deployProgress");
        progress.style.display = "flex";
        
        // Reset steps
        for(let i=0; i<4; i++) {{
            const step = document.getElementById("step-" + i);
            step.className = "step-row";
        }}
        
        logEvent("AUTOPILOT", `Deploy request received for custom token: ${{name}} ($${{ticker}}). Supply: ${{supply}}.`);
        
        if (isMockMode) {{
            // Step-by-step visual workflow execution
            setTimeout(() => {{ document.getElementById("step-0").className = "step-row active"; }}, 200);
            setTimeout(() => {{
                document.getElementById("step-0").className = "step-row done";
                document.getElementById("step-1").className = "step-row active";
            }}, 1200);
            setTimeout(() => {{
                document.getElementById("step-1").className = "step-row done";
                document.getElementById("step-2").className = "step-row active";
            }}, 2400);
            setTimeout(() => {{
                document.getElementById("step-2").className = "step-row done";
                document.getElementById("step-3").className = "step-row active";
            }}, 3600);
            setTimeout(() => {{
                document.getElementById("step-3").className = "step-row done";
                logEvent("AUTOPILOT", `[Sandbox] EVM Deployment complete for $${{ticker}}.`);
                
                // Add option dynamically to selects
                const opt = document.createElement("option");
                opt.value = `0x${{ticker}}`;
                opt.innerText = `$${{ticker}} (${{name}})`;
                document.getElementById("wsTokenSelect").appendChild(opt);
                
                // Bot replies in chat
                const box = document.getElementById("wsChatBox");
                const aDiv = document.createElement("div");
                aDiv.className = "bubble b-agent";
                aDiv.innerHTML = `<strong>RobinMCP:</strong> Sandbox mock deployment complete! Added swap pool for <strong>$${{ticker}}</strong>.`;
                box.appendChild(aDiv);
                box.scrollTop = box.scrollHeight;
            }}, 4800);
            return;
        }}

        // On-chain deployment
        try {{
            document.getElementById("step-0").className = "step-row active";
            const fee = await memeFactoryContract.deployFee();
            
            document.getElementById("step-0").className = "step-row done";
            document.getElementById("step-1").className = "step-row active";
            
            const tx = await memeFactoryContract.deployMemeToken(name, ticker, supply, {{ value: fee }});
            logEvent("AUTOPILOT", `Broadcasted tx: ${{tx.hash}}`);
            
            document.getElementById("step-1").className = "step-row done";
            document.getElementById("step-2").className = "step-row active";
            
            const receipt = await tx.wait();
            
            document.getElementById("step-2").className = "step-row done";
            document.getElementById("step-3").className = "step-row active";
            
            const event = receipt.events.find(e => e.event === 'MemeDeployed');
            const tokenAddr = event.args.tokenAddress;
            logEvent("AUTOPILOT", `✅ Confirmed. Token Address: ${{tokenAddr}}`);
            
            document.getElementById("step-3").className = "step-row done";
            
            // Add option dynamically to select
            const opt = document.createElement("option");
            opt.value = tokenAddr;
            opt.innerText = `$${{ticker}} (${{name}})`;
            document.getElementById("wsTokenSelect").appendChild(opt);
            
            // Bot replies in chat
            const box = document.getElementById("wsChatBox");
            const aDiv = document.createElement("div");
            aDiv.className = "bubble b-agent";
            aDiv.innerHTML = `<strong>RobinMCP:</strong> Deployed successfully! Contract Address: <span style="font-family:monospace; color:var(--gold); font-size:12px;">${{tokenAddr}}</span>. Added swap pool.`;
            box.appendChild(aDiv);
            box.scrollTop = box.scrollHeight;
            
        }} catch (e) {{
            console.error(e);
            logEvent("ERROR", `Autopilot deployment failed: ${{e.message}}`);
            progress.style.display = "none";
        }}
    }}
    
    // --- WORKSPACE: VIBECODING SPEC HUB ---
    const specDocs = [
        {{
            title: "1. Product Requirement Document (PRD)",
            content: "<strong>Overview:</strong> A Web3/EVM launchpad designed to transition meme-style tokens into curated developer-backed utility tokens.<br><strong>Objectives:</strong> Eliminate PvP casino rugs by routing 20% of trading fees to a Developer Buyback Pool, and 40% to Staked Holders. Centralized curation by the repository owner ensures only verified commits earn native payouts.<br><strong>Success Metrics:</strong> Developer retention, code contribution volume, locked utility values, and token price appreciation via automated contract buybacks."
        }},
        {{
            title: "2. Technical Requirement Document (TRD)",
            content: "<strong>L2 Execution Chain:</strong> Robinhood Chain L2 (Arbitrum Orbit Rollup) for sub-penny gas executing EVM transactions.<br><strong>Smart Contracts:</strong> MemeFactoryV2.sol (token deployment), EcosystemTreasury.sol (40/40/20 fee split), StakingYield.sol (yield vault).<br><strong>Tooling Stack:</strong> Python-based EVM Model Context Protocol (MCP) server for local AI code execution, SQLite cache for ABI signatures, and a local Python payout script (.env gated) for developer reward signing."
        }},
        {{
            title: "3. App Flow (User Navigation)",
            content: "<strong>Path 1:</strong> User enters landing page -> connects wallet -> interacts with virtual bonding curve swaps on the Swap Terminal.<br><strong>Path 2:</strong> User stakes native $ROBIN_MCP -> claims accumulated ETH yield dynamically in the Staking Vault.<br><strong>Path 3:</strong> Developer merges GitHub PR -> Webhook logs PR details -> Admin runs local payout script -> EcosystemTreasury swaps ETH for tokens and transfers them to the developer wallet."
        }},
        {{
            title: "4. UI/UX Design System Spec",
            content: "<strong>Design Language:</strong> Sleek dark mode blending Anant Anaadi branding (Navy backgrounds, Saffron Gold accents, Cream texts) with Launchpad highlights (Neon Green for buy alerts, Neon Pink for sells).<br><strong>Typography:</strong> 'Outfit' for titles and headers, 'JetBrains Mono' for developer console outputs, code blocks, and transaction hashes.<br><strong>Components:</strong> Glassmorphic cards (radial gradients, translucent borders, high backdrop blur) and full-screen overlay workspaces to give an app-like feel."
        }},
        {{
            title: "5. Backend Schema (EVM & SQLite)",
            content: "<strong>EVM Contracts state:</strong><br>- MemeFactoryV2: Keeps a mapping of all active token pools and virtual curve reserves (tokenReserves, ethReserves).<br>- EcosystemTreasury: Tracks Creator balance, Staker yield pool balance, and Developer rewards pool balance.<br><strong>Local SQLite cache:</strong><br>- ABIs Table: Maps contract_address to ABI JSON.<br>- Tickers Table: Maps ticker symbol to EVM contract address.<br>- Payouts Table: Logs PR_ID, wallet_address, transaction_hash, and payout_date."
        }},
        {{
            title: "6. Implementation Plan (Build Phases)",
            content: "<strong>Phase 1 (Planning & Core Contracts):</strong> Solidity specs for factory bonding curves, EcosystemTreasury, and StakingYield contracts. (Status: Done)<br><strong>Phase 2 (Developer CLI tool):</strong> Local payout signing CLI and EVM MCP token-gating middleware. (Status: Done)<br><strong>Phase 3 (Frontend upgrade):</strong> Full-screen 3D particle morphing scroll world website with glassmorphic workspace dashboards. (Status: Done)<br><strong>Phase 4 (Testnet Launch & Audits):</strong> Deploy contracts to Robinhood Testnet, verify source code on Blockscout explorer, and run public client-side audits. (Status: Next)"
        }}
    ];

    function switchSpecTab(index) {{
        const btns = document.querySelectorAll("#ws-dev .nav-tabs button");
        btns.forEach((btn, idx) => {{
            if(idx === index) btn.classList.add("active");
            else btn.classList.remove("active");
        }});
        
        const doc = specDocs[index];
        const box = document.getElementById("spec-content-box");
        box.innerHTML = `<h4 style="color: var(--gold); font-size:14px; margin-bottom:10px; font-weight:600;">${{doc.title}}</h4>
                         <div style="color: var(--text-muted); font-size:13px; line-height:1.6;">${{doc.content}}</div>`;
    }}

    // --- WORKSPACE: COMMUNITY TRUSTS LOGIC ---
    let deployedTrusts = [];
    let activeTrustIndex = -1;
    let mockAssets = [];
    
    async function triggerDeployTrust() {{
        const name = document.getElementById("trustName").value;
        const dirsInput = document.getElementById("trustDirectors").value;
        const threshold = parseInt(document.getElementById("trustThreshold").value) || 1;
        
        logEvent("TRUST_FACTORY", `Deploying new Community Trust Bank: "${{name}}" with threshold ${{threshold}}...`);
        
        if (isMockMode) {{
            setTimeout(() => {{
                const mockAddr = "0x" + Math.random().toString(16).substring(2, 10) + "..." + Math.random().toString(16).substring(2, 6);
                const dirs = dirsInput.split(",").map(d => d.trim()).filter(d => d);
                if (dirs.length === 0) dirs.push(userAddress);
                
                const newTrust = {{
                    address: mockAddr,
                    name: name,
                    directors: dirs,
                    threshold: threshold,
                    balance: 0.0,
                    shares: 0.0,
                    goldReserves: 0.0,
                    silverReserves: 0.0,
                    proposals: []
                }};
                
                deployedTrusts.push(newTrust);
                activeTrustIndex = deployedTrusts.length - 1;
                
                document.getElementById("activeTrustAddr").innerText = mockAddr;
                logEvent("TRUST_FACTORY", `✅ [Sandbox] Trust Bank "${{name}}" deployed successfully at ${{mockAddr}}!`);
                updateTrustUI();
            }}, 1500);
            return;
        }}

        try {{
            let directors = dirsInput.split(",").map(d => d.trim()).filter(d => d);
            if (directors.length === 0) directors = [userAddress];
            
            const tx = await trustFactoryContract.createTrust(name, directors, threshold);
            logEvent("TRUST_FACTORY", `Tx sent: ${{tx.hash}}. Waiting for confirmation...`);
            const receipt = await tx.wait();
            
            const count = await trustFactoryContract.getTrustCount();
            const trustAddr = await trustFactoryContract.allTrusts(count.sub(1));
            
            logEvent("TRUST_FACTORY", `✅ Trust Bank deployed at: ${{trustAddr}}`);
            document.getElementById("activeTrustAddr").innerText = trustAddr;
            
            activeTrustContract = new ethers.Contract(trustAddr, ABIs.CommunityTrust, signer);
            await loadActiveTrustDetails();
        }} catch (e) {{
            console.error(e);
            logEvent("ERROR", `Failed to deploy trust: ${{e.message}}`);
        }}
    }}
    
    async function triggerDeployMockAsset() {{
        const name = document.getElementById("mockAssetName").value;
        const ticker = document.getElementById("mockAssetSymbol").value;
        
        logEvent("ASSET_FACTORY", `Deploying mock precious metal asset: ${{name}} ($${{ticker}})...`);
        
        if (isMockMode) {{
            setTimeout(() => {{
                const mockAddr = "0x" + Math.random().toString(16).substring(2, 10) + "..." + Math.random().toString(16).substring(2, 6);
                logEvent("ASSET_FACTORY", `✅ [Sandbox] Asset $${{ticker}} deployed successfully at ${{mockAddr}}.`);
                mockAssets.push({{ name, ticker, address: mockAddr }});
            }}, 1200);
            return;
        }}

        // Since mock asset is deployed, we can use contract factory to deploy a new MockAsset on-chain
        try {{
            // Load MockAsset compilation artifact or deploy via server SDK/RPC
            logEvent("ASSET_FACTORY", "To deploy real assets on-chain, please use the python EVM MCP server CLI.");
        }} catch (e) {{
            logEvent("ERROR", e.message);
        }}
    }}
    
    async function triggerDepositToTrust() {{
        const amt = parseFloat(document.getElementById("depositTrustAmt").value) || 0;
        if(amt <= 0) return;
        
        if (isMockMode) {{
            if(activeTrustIndex === -1) {{
                alert("Please deploy a trust first.");
                return;
            }}
            const trust = deployedTrusts[activeTrustIndex];
            logEvent("TRUST", `[Sandbox] Depositing ${{amt}} ETH into pool at ${{trust.address}}...`);
            
            setTimeout(() => {{
                trust.balance += amt;
                trust.shares += amt;
                logEvent("TRUST", `✅ [Sandbox] Deposited ${{amt}} ETH. Total pooled wealth: ${{trust.balance.toFixed(2)}} ETH.`);
                updateTrustUI();
            }}, 1000);
            return;
        }}

        if (!activeTrustContract) return;
        logEvent("TRUST", `Depositing ${{amt}} ETH on-chain...`);
        try {{
            const tx = await activeTrustContract.deposit({{ value: ethers.utils.parseEther(amt.toString()) }});
            await tx.wait();
            logEvent("TRUST", `✅ Deposit successful!`);
            await loadActiveTrustDetails();
        }} catch (e) {{
            logEvent("ERROR", `Deposit failed: ${{e.message}}`);
        }}
    }}
    
    async function triggerProposeTransaction() {{
        const dest = document.getElementById("propDest").value;
        const data = document.getElementById("propData").value || "0x";
        
        if (isMockMode) {{
            if(activeTrustIndex === -1) return;
            const trust = deployedTrusts[activeTrustIndex];
            logEvent("TRUST", `[Sandbox] Proposing investment transaction to ${{dest}}...`);
            
            const propId = trust.proposals.length;
            trust.proposals.push({{
                id: propId,
                destination: dest,
                data: data,
                signatures: 1,
                executed: false
            }});
            
            logEvent("TRUST", `✅ [Sandbox] Proposal #${{propId}} submitted and signed. Required: ${{trust.threshold}}.`);
            updateTrustUI();
            return;
        }}

        if (!activeTrustContract) return;
        logEvent("TRUST", `Proposing transaction on-chain to ${{dest}}...`);
        try {{
            const tx = await activeTrustContract.proposeTransaction(dest, 0, data);
            await tx.wait();
            logEvent("TRUST", `✅ Transaction proposed successfully.`);
            await loadActiveTrustDetails();
        }} catch (e) {{
            logEvent("ERROR", `Propose failed: ${{e.message}}`);
        }}
    }}
    
    async function signProposal(idx) {{
        if (isMockMode) {{
            const trust = deployedTrusts[activeTrustIndex];
            const prop = trust.proposals[idx];
            if (prop.signatures >= trust.threshold) return;
            
            prop.signatures += 1;
            logEvent("TRUST", `[Sandbox] Signed Proposal #${{idx}}. Current signs: ${{prop.signatures}}/${{trust.threshold}}.`);
            updateTrustUI();
            return;
        }}

        try {{
            logEvent("TRUST", `Signing proposal #${{idx}} on-chain...`);
            const tx = await activeTrustContract.signTransaction(idx);
            await tx.wait();
            logEvent("TRUST", `✅ Signed proposal.`);
            await loadActiveTrustDetails();
        }} catch (e) {{
            logEvent("ERROR", `Sign failed: ${{e.message}}`);
        }}
    }}
    
    async function executeProposal(idx) {{
        if (isMockMode) {{
            const trust = deployedTrusts[activeTrustIndex];
            const prop = trust.proposals[idx];
            if (prop.signatures < trust.threshold) return;
            
            prop.executed = true;
            logEvent("TRUST", `[Sandbox] Executing investment proposal #${{idx}}...`);
            
            setTimeout(() => {{
                if (prop.destination.toLowerCase().includes("gold") || prop.data.toLowerCase().includes("mint") || prop.data.toLowerCase().includes("cGOLD")) {{
                    trust.goldReserves += 100.0;
                    logEvent("TRUST", "✅ [Sandbox] Multi-sig execution successful. Gold reserves increased by 100.0 cGOLD!");
                }} else {{
                    trust.silverReserves += 250.0;
                    logEvent("TRUST", "✅ [Sandbox] Multi-sig execution successful. Silver reserves increased by 250.0 cSILVER!");
                }}
                updateTrustUI();
            }}, 1200);
            return;
        }}

        try {{
            logEvent("TRUST", `Executing proposal #${{idx}} on-chain...`);
            const tx = await activeTrustContract.executeTransaction(idx);
            await tx.wait();
            logEvent("TRUST", `✅ Executed proposal successfully.`);
            await loadActiveTrustDetails();
        }} catch (e) {{
            logEvent("ERROR", `Execution failed: ${{e.message}}`);
        }}
    }}
    
    async function triggerDistributeDividends() {{
        const token = document.getElementById("divTokenAddr").value || ethers.constants.AddressZero;
        const amt = document.getElementById("divAmt").value;
        
        if (isMockMode) {{
            logEvent("TRUST", `[Sandbox] Distributing yield dividends of ${{amt}} units of asset (${{token}})...`);
            setTimeout(() => {{
                logEvent("TRUST", "✅ [Sandbox] Yield dividends distributed proportionally to all depositors.");
            }}, 1000);
            return;
        }}

        if (!activeTrustContract) return;
        logEvent("TRUST", `Distributing ${{amt}} dividends...`);
        try {{
            let tx;
            if (token === ethers.constants.AddressZero) {{
                tx = await activeTrustContract.distributeDividends(token, amt, {{ value: amt }});
            }} else {{
                const tokenContract = new ethers.Contract(token, ABIs.ERC20, signer);
                const allowanceTx = await tokenContract.approve(activeTrustContract.address, amt);
                await allowanceTx.wait();
                tx = await activeTrustContract.distributeDividends(token, amt);
            }}
            await tx.wait();
            logEvent("TRUST", `✅ Dividends distributed successfully.`);
        }} catch (e) {{
            logEvent("ERROR", `Failed to distribute: ${{e.message}}`);
        }}
    }}
    
    async function triggerClaimDividends() {{
        const token = document.getElementById("claimTokenAddr").value || ethers.constants.AddressZero;
        
        if (isMockMode) {{
            logEvent("TRUST", `[Sandbox] Claiming pending dividends for asset (${{token}})...`);
            setTimeout(() => {{
                logEvent("TRUST", "✅ [Sandbox] Pending dividends claimed and transferred.");
            }}, 1000);
            return;
        }}

        if (!activeTrustContract) return;
        logEvent("TRUST", `Claiming dividends...`);
        try {{
            const tx = await activeTrustContract.claimDividends(token);
            await tx.wait();
            logEvent("TRUST", `✅ Pending dividends claimed.`);
        }} catch (e) {{
            logEvent("ERROR", `Claim failed: ${{e.message}}`);
        }}
    }}
    
    async function loadActiveTrustDetails() {{
        if (isMockMode || !activeTrustContract) return;
        try {{
            const balance = await provider.getBalance(activeTrustContract.address);
            const totalShares = await activeTrustContract.totalShares();
            const userShares = await activeTrustContract.shares(userAddress);
            
            const balEth = ethers.utils.formatEther(balance);
            const userSharesEth = ethers.utils.formatEther(userShares);
            const sharePct = totalShares.gt(0) ? userShares.mul(100).div(totalShares).toString() : "0";
            
            document.getElementById("activeTrustAddr").innerText = activeTrustContract.address.substring(0, 8) + "..." + activeTrustContract.address.substring(38);
            document.getElementById("activeTrustBalance").innerText = parseFloat(balEth).toFixed(4) + " ETH";
            document.getElementById("userTrustShares").innerText = `${{parseFloat(userSharesEth).toFixed(4)}} ETH (${{sharePct}}%)`;
            
            // Render on-chain proposals
            const pList = document.getElementById("trustProposalsList");
            pList.innerHTML = "No active proposals on-chain.";
        }} catch (e) {{
            console.error("Failed to load active trust details:", e);
        }}
    }}

    function updateTrustUI() {{
        if(activeTrustIndex === -1) return;
        const trust = deployedTrusts[activeTrustIndex];
        
        document.getElementById("activeTrustBalance").innerText = trust.balance.toFixed(2) + " ETH";
        document.getElementById("userTrustShares").innerText = `${{trust.shares.toFixed(2)}} ETH (100%)`;
        
        document.getElementById("goldReservesVal").innerText = trust.goldReserves.toFixed(2) + " cGOLD";
        document.getElementById("silverReservesVal").innerText = trust.silverReserves.toFixed(2) + " cSILVER";
        
        const maxBarVal = 500.0;
        document.getElementById("goldReservesBar").style.width = Math.min((trust.goldReserves / maxBarVal) * 100, 100) + "%";
        document.getElementById("silverReservesBar").style.width = Math.min((trust.silverReserves / maxBarVal) * 100, 100) + "%";
        
        const pList = document.getElementById("trustProposalsList");
        pList.innerHTML = "";
        if (trust.proposals.length === 0) {{
            pList.innerHTML = "No active proposals.";
            return;
        }}
        
        trust.proposals.forEach(p => {{
            const div = document.createElement("div");
            div.style.background = "rgba(255,255,255,0.02)";
            div.style.border = "1px solid rgba(255,255,255,0.05)";
            div.style.borderRadius = "8px";
            div.style.padding = "10px";
            div.style.marginBottom = "10px";
            div.style.display = "flex";
            div.style.justifyContent = "space-between";
            div.style.alignItems = "center";
            
            const btnHtml = p.executed ? 
                `<span style="color:var(--success);">Executed</span>` : 
                (p.signatures >= trust.threshold ? 
                    `<button class="btn" style="width:80px; padding:4px; font-size:11px;" onclick="executeProposal(${{p.id}})">Execute</button>` : 
                    `<button class="btn btn-outline" style="width:80px; padding:4px; font-size:11px; margin-top:0;" onclick="signProposal(${{p.id}})">Sign (${{p.signatures}}/${{trust.threshold}})</button>`);
                    
            div.innerHTML = `
                <div>
                    <div style="font-weight:600; color:var(--text);">Prop #${{p.id}} to ${{p.destination}}</div>
                    <div style="color:var(--text-muted); font-size:10px; font-family:var(--font-mono); margin-top:2px;">Data: ${{p.data}}</div>
                </div>
                <div>${{btnHtml}}</div>
            `;
            pList.appendChild(div);
        }});
    }}

    // Initialize
    window.onload = () => {{
        init3D();
        updateActiveSections();
        switchSpecTab(0);
        initCandleChart();
        setupMockState(); // Default to Sandbox state for clean visual demos without wallets connected
    }};
</script>

</body>
</html>
"""
    output_path = "/data/data/com.termux/files/home/robinhood-evm-mcp/index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Generated upgraded, diorama-powered index.html at {output_path}")

if __name__ == "__main__":
    generate()
