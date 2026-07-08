# generate_index_html.py
# Generates a premium, single-page trading dApp dashboard for the Meme Launchpad

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
    <title>Robinhood Chain - Meme Launchpad</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Ethers.js v5 CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/5.7.2/ethers.umd.min.js" type="text/javascript"></script>
    <style>
        :root {{
            --bg-color: #0b111e;
            --card-bg: rgba(22, 33, 54, 0.4);
            --border-color: rgba(245, 158, 11, 0.15);
            --gold: #f59e0b;
            --gold-hover: #d97706;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --success: #10b981;
            --error: #ef4444;
            --font-main: 'Outfit', sans-serif;
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
                radial-gradient(at 0% 0%, rgba(245, 158, 11, 0.05) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(22, 33, 54, 0.3) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }}

        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto 40px auto;
            padding: 15px 0;
            border-bottom: 1px solid rgba(245, 158, 11, 0.1);
        }}

        .logo-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .logo {{
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, var(--gold), #b45309);
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 22px;
            font-weight: 800;
            color: #0b111e;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
        }}

        .brand-name {{
            font-size: 20px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}

        .nav-btn {{
            background: linear-gradient(135deg, var(--gold), #d97706);
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            color: #0b111e;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .nav-btn:hover {{
            background: linear-gradient(135deg, #d97706, #b45309);
            transform: translateY(-1px);
        }}

        .main-layout {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }}

        @media (max-width: 768px) {{
            .main-layout {{
                grid-template-columns: 1fr;
            }}
        }}

        .section-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        }}

        /* Token List Grid */
        .token-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        @media (max-width: 600px) {{
            .token-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .token-card {{
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(245, 158, 11, 0.1);
            border-radius: 16px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .token-card:hover {{
            border-color: var(--gold);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
        }}

        .token-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .token-name {{
            font-size: 16px;
            font-weight: 700;
        }}

        .token-symbol {{
            font-size: 12px;
            background: rgba(245, 158, 11, 0.15);
            color: var(--gold);
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: 600;
        }}

        .token-stat {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }}

        .progress-bar-container {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
            margin-top: 15px;
        }}

        .progress-bar {{
            background: linear-gradient(90deg, var(--gold), #10b981);
            height: 100%;
            width: 0%;
            transition: width 0.5s ease;
        }}

        /* Create Token Form */
        .form-group {{
            margin-bottom: 16px;
        }}

        label {{
            display: block;
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 6px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        input {{
            width: 100%;
            background: rgba(11, 17, 30, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 10px;
            padding: 12px;
            font-size: 14px;
            color: var(--text-primary);
            outline: none;
            transition: all 0.3s ease;
        }}

        input:focus {{
            border-color: var(--gold);
        }}

        .submit-btn {{
            width: 100%;
            background: linear-gradient(135deg, var(--gold), #d97706);
            border: none;
            border-radius: 12px;
            padding: 14px;
            color: #0b111e;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .submit-btn:hover {{
            background: linear-gradient(135deg, #d97706, #b45309);
        }}

        /* Trade Widget */
        .trade-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .tab-btn {{
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 10px;
            color: var(--text-secondary);
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .tab-btn.active.buy {{
            background: rgba(16, 185, 129, 0.2);
            border-color: var(--success);
            color: var(--success);
        }}

        .tab-btn.active.sell {{
            background: rgba(239, 68, 68, 0.2);
            border-color: var(--error);
            color: var(--error);
        }}

        .status-box {{
            background: rgba(11, 17, 30, 0.6);
            border-radius: 10px;
            padding: 12px;
            font-size: 12px;
            margin-top: 15px;
            border-left: 3px solid var(--gold);
            display: none;
            word-break: break-all;
        }}
    </style>
</head>
<body>

<div class="navbar">
    <div class="logo-container">
        <div class="logo">R</div>
        <div class="brand-name">Meme Launchpad</div>
    </div>
    <button id="connectBtn" class="nav-btn">Connect Wallet</button>
</div>

<div class="main-layout">
    <!-- Left Column: Token Directory -->
    <div>
        <div class="section-title">
            <span>🔥 Active Pools</span>
            <span style="font-size: 14px; color: var(--text-secondary);" id="poolCount">0 Tokens</span>
        </div>
        <div class="token-grid" id="tokenGrid">
            <!-- Dynamic Token Cards will load here -->
        </div>
    </div>

    <!-- Right Column: Launch / Trade Panel -->
    <div>
        <!-- Launch Panel -->
        <div class="card">
            <h3 style="margin-bottom: 15px; font-size: 18px;">🚀 Launch Token</h3>
            <div class="form-group">
                <label for="tokName">Token Name</label>
                <input type="text" id="tokName" placeholder="e.g. Pepe Robinhood">
            </div>
            <div class="form-group">
                <label for="tokSymbol">Token Symbol</label>
                <input type="text" id="tokSymbol" placeholder="e.g. PEPERH">
            </div>
            <div class="form-group">
                <label for="tokSupply">Initial Supply</label>
                <input type="number" id="tokSupply" value="1000000000" readonly>
            </div>
            <button class="submit-btn" id="launchBtn">Deploy Meme Token (0.005 ETH)</button>
        </div>

        <!-- Trade Panel -->
        <div class="card" id="tradeCard" style="display: none;">
            <h3 style="margin-bottom: 8px; font-size: 18px;" id="tradeTitle">Trade Token</h3>
            <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 15px;" id="tradeAddress"></p>
            
            <div class="trade-tabs">
                <button class="tab-btn active buy" id="tabBuy">Buy</button>
                <button class="tab-btn sell" id="tabSell">Sell</button>
            </div>

            <div class="form-group">
                <label id="inputLabel">Amount of ETH to spend</label>
                <input type="number" id="tradeAmount" placeholder="0.05" step="0.01">
            </div>

            <button class="submit-btn" id="tradeBtn" style="background: linear-gradient(135deg, var(--success), #059669); color: #fff;">Execute Swap</button>
            
            <div id="statusBox" class="status-box">
                <div id="statusBody">Processing...</div>
            </div>
        </div>
    </div>
</div>

<script>
    const factoryAddress = "{factory_address}";
    const factoryAbi = {json.dumps(abi)};
    const tokenAbi = {json.dumps(token_abi)};

    let provider;
    let signer;
    let factoryContract;
    let activeTokenAddress = null;
    let tradeMode = "buy"; // "buy" or "sell"

    const connectBtn = document.getElementById("connectBtn");
    const launchBtn = document.getElementById("launchBtn");
    const tokenGrid = document.getElementById("tokenGrid");
    const poolCountText = document.getElementById("poolCount");
    
    const tradeCard = document.getElementById("tradeCard");
    const tradeTitle = document.getElementById("tradeTitle");
    const tradeAddressText = document.getElementById("tradeAddress");
    const tabBuy = document.getElementById("tabBuy");
    const tabSell = document.getElementById("tabSell");
    const inputLabel = document.getElementById("inputLabel");
    const tradeAmountInput = document.getElementById("tradeAmount");
    const tradeBtn = document.getElementById("tradeBtn");
    const statusBox = document.getElementById("statusBox");
    const statusBody = document.getElementById("statusBody");

    async function switchNetwork() {{
        const targetChainId = "0x1237"; // Hex for 4663
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
            alert("Open this page inside Rabby browser.");
            return;
        }}
        try {{
            provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            signer = provider.getSigner();
            const address = await signer.getAddress();
            
            // Auto switch network
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
            connectBtn.style.background = "rgba(16, 185, 129, 0.2)";
            connectBtn.style.color = "var(--success)";
            connectBtn.style.border = "1px solid var(--success)";
            
            await loadPools();
        }} catch (err) {{
            console.error(err);
        }}
    }}

    async function loadPools() {{
        if (!factoryContract) return;
        try {{
            const count = await factoryContract.getMemeCount();
            poolCountText.innerText = `${{count.toString()}} Tokens`;
            tokenGrid.innerHTML = "";

            for (let i = 0; i < count; i++) {{
                const tokenAddr = await factoryContract.allMemeTokens(i);
                const pool = await factoryContract.pools(tokenAddr);
                const tokenContract = new ethers.Contract(tokenAddr, tokenAbi, provider);
                
                const name = await tokenContract.name();
                const symbol = await tokenContract.symbol();
                
                // Calculate progress
                const maxReserve = ethers.utils.parseEther("800000000"); // 800M tokens in pool initially
                const currentReserve = pool.tokenReserves;
                const sold = maxReserve.sub(currentReserve);
                let progress = sold.mul(100).div(maxReserve).toNumber();
                if (progress < 0) progress = 0;
                if (progress > 100) progress = 100;

                const card = document.createElement("div");
                card.className = "token-card";
                card.innerHTML = `
                    <div class="token-header">
                        <span class="token-name">${{name}}</span>
                        <span class="token-symbol">${{symbol}}</span>
                    </div>
                    <div class="token-stat">
                        <span>Address:</span>
                        <span>${{tokenAddr.substring(0, 6)}}...${{tokenAddr.substring(38)}}</span>
                    </div>
                    <div class="token-stat">
                        <span>ETH Reserves:</span>
                        <span>${{ethers.utils.formatEther(pool.ethReserves)}} ETH</span>
                    </div>
                    <div class="token-stat">
                        <span>Bonding Curve:</span>
                        <span>${{progress}}%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: ${{progress}}%"></div>
                    </div>
                `;
                
                card.addEventListener("click", () => selectToken(tokenAddr, symbol));
                tokenGrid.appendChild(card);
            }}
        }} catch (err) {{
            console.error("Error loading pools:", err);
        }}
    }}

    function selectToken(addr, symbol) {{
        activeTokenAddress = addr;
        tradeCard.style.display = "block";
        tradeTitle.innerText = `Trade $${{symbol}}`;
        tradeAddressText.innerText = addr;
        statusBox.style.display = "none";
        
        // Reset inputs
        tradeAmountInput.value = "";
    }}

    // Tab Event Listeners
    tabBuy.addEventListener("click", () => {{
        tradeMode = "buy";
        tabBuy.className = "tab-btn active buy";
        tabSell.className = "tab-btn";
        inputLabel.innerText = "Amount of ETH to spend";
        tradeAmountInput.placeholder = "0.05";
        tradeBtn.style.background = "linear-gradient(135deg, var(--success), #059669)";
    }});

    tabSell.addEventListener("click", () => {{
        tradeMode = "sell";
        tabSell.className = "tab-btn active sell";
        tabBuy.className = "tab-btn";
        inputLabel.innerText = "Amount of tokens to sell";
        tradeAmountInput.placeholder = "100000";
        tradeBtn.style.background = "linear-gradient(135deg, var(--error), #dc2626)";
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
            
            // Deploy charges 0.005 ETH
            const tx = await factoryContract.deployMemeToken(name, symbol, 1000000000, {{
                value: ethers.utils.parseEther("0.005")
            }});
            
            await tx.wait();
            alert("Token deployed successfully!");
            document.getElementById("tokName").value = "";
            document.getElementById("tokSymbol").value = "";
            
            await loadPools();
        }} catch (err) {{
            alert("Deployment failed: " + err.message);
        }} finally {{
            launchBtn.innerText = "Deploy Meme Token (0.005 ETH)";
            launchBtn.disabled = false;
        }}
    }});

    // Trade Token
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
            if (tradeMode === "buy") {{
                const valueWei = ethers.utils.parseEther(amount);
                const tx = await factoryContract.buyMemeToken(activeTokenAddress, {{
                    value: valueWei
                }});
                statusBody.innerText = `Transaction broadcasted!\\nTx Hash: ${{tx.hash}}\\nWaiting for confirmation...`;
                await tx.wait();
                statusBody.innerText = `✅ Success! Tokens purchased successfully.`;
            }} else {{
                // Sell
                const tokenAmount = ethers.utils.parseEther(amount);
                
                // Approve the factory to pull tokens first
                statusBody.innerText = "Approving factory to spend tokens...";
                const tokenContract = new ethers.Contract(activeTokenAddress, tokenAbi, signer);
                const approveTx = await tokenContract.approve(factoryAddress, tokenAmount);
                await approveTx.wait();
                
                statusBody.innerText = "Executing sell swap...";
                const tx = await factoryContract.sellMemeToken(activeTokenAddress, tokenAmount);
                statusBody.innerText = `Transaction broadcasted!\\nTx Hash: ${{tx.hash}}\\nWaiting for confirmation...`;
                await tx.wait();
                statusBody.innerText = `✅ Success! Tokens sold successfully.`;
            }}
            await loadPools();
        }} catch (err) {{
            statusBody.innerText = `❌ Error: ${{err.message}}`;
        }} finally {{
            tradeBtn.disabled = false;
        }}
    }});

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
