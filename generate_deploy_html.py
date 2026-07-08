# generate_deploy_html.py
# Reads compiled artifacts and generates a premium, single-file HTML deployment page

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
    bytecode = artifact["bytecode"]

    # Prefilled payout recipient
    default_payout = "0xf89e3c5506e8a571618a3f228bde719eac01ef11"

    # 2. HTML Template with premium styling
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robinhood Chain - MemeFactory Deployer</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <!-- Ethers.js v5 CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/5.7.2/ethers.umd.min.js" type="text/javascript"></script>
    <style>
        :root {{
            --bg-color: #0b111e;
            --card-bg: rgba(22, 33, 54, 0.6);
            --border-color: rgba(245, 158, 11, 0.2);
            --gold: #f59e0b;
            --gold-hover: #d97706;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --success: #10b981;
            --error: #ef4444;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
        }}

        body {{
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(245, 158, 11, 0.08) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(22, 33, 54, 0.5) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}

        .container {{
            width: 100%;
            max-width: 480px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            animation: fadeIn 0.6s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .header {{
            text-align: center;
            margin-bottom: 25px;
        }}

        .logo {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--gold), #b45309);
            border-radius: 16px;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            font-size: 28px;
            font-weight: 800;
            color: #000;
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
            margin-bottom: 15px;
        }}

        h1 {{
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 6px;
        }}

        .subtitle {{
            font-size: 14px;
            color: var(--text-secondary);
        }}

        .form-group {{
            margin-bottom: 20px;
        }}

        label {{
            display: block;
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        input {{
            width: 100%;
            background: rgba(11, 17, 30, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 14px;
            font-size: 14px;
            color: var(--text-primary);
            outline: none;
            transition: all 0.3s ease;
        }}

        input:focus {{
            border-color: var(--gold);
            box-shadow: 0 0 8px rgba(245, 158, 11, 0.2);
        }}

        .btn {{
            width: 100%;
            background: linear-gradient(135deg, var(--gold), #d97706);
            border: none;
            border-radius: 14px;
            padding: 16px;
            color: #0b111e;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
        }}

        .btn:hover {{
            background: linear-gradient(135deg, #d97706, #b45309);
            transform: translateY(-1px);
        }}

        .btn:active {{
            transform: translateY(1px);
        }}

        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}

        .status-box {{
            margin-top: 25px;
            background: rgba(11, 17, 30, 0.5);
            border-radius: 12px;
            padding: 16px;
            font-size: 13px;
            display: none;
            border-left: 3px solid var(--gold);
            word-break: break-all;
        }}

        .status-header {{
            font-weight: 600;
            margin-bottom: 5px;
            color: var(--gold);
        }}

        .status-body {{
            color: var(--text-secondary);
            line-height: 1.5;
        }}

        .success-text {{
            color: var(--success) !important;
            font-weight: 600;
        }}

        .error-text {{
            color: var(--error) !important;
            font-weight: 600;
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="logo">R</div>
        <h1>MemeFactory Deployer</h1>
        <div class="subtitle">Deploy Launchpad on Robinhood Chain via Rabby</div>
    </div>

    <div class="form-group">
        <label for="payout">Payout Fee Recipient Address</label>
        <input type="text" id="payout" value="{default_payout}" placeholder="0x...">
    </div>

    <button id="connectBtn" class="btn" style="margin-bottom: 12px;">Connect Wallet</button>
    <button id="deployBtn" class="btn" disabled>Deploy Launchpad</button>

    <div id="statusBox" class="status-box">
        <div id="statusHeader" class="status-header">Status</div>
        <div id="statusBody" class="status-body">Ready...</div>
    </div>
</div>

<script>
    const contractAbi = {json.dumps(abi)};
    const contractBytecode = "0x{bytecode}";

    const connectBtn = document.getElementById("connectBtn");
    const deployBtn = document.getElementById("deployBtn");
    const payoutInput = document.getElementById("payout");
    const statusBox = document.getElementById("statusBox");
    const statusHeader = document.getElementById("statusHeader");
    const statusBody = document.getElementById("statusBody");

    let provider;
    let signer;

    function showStatus(title, message, type = "normal") {{
        statusBox.style.display = "block";
        statusHeader.innerText = title;
        statusBody.innerText = message;
        
        statusHeader.classList.remove("success-text", "error-text");
        if (type === "success") {{
            statusHeader.classList.add("success-text");
            statusBox.style.borderLeftColor = "var(--success)";
        }} else if (type === "error") {{
            statusHeader.classList.add("error-text");
            statusBox.style.borderLeftColor = "var(--error)";
        }} else {{
            statusBox.style.borderLeftColor = "var(--gold)";
        }}
    }}

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
                    showStatus("Error", "Failed to add Robinhood Chain to wallet: " + addError.message, "error");
                    return false;
                }}
            }}
            showStatus("Error", "Failed to switch to Robinhood Chain: " + switchError.message, "error");
            return false;
        }}
    }}

    async function connectWallet() {{
        if (typeof window.ethereum === "undefined") {{
            showStatus("Error", "No Ethereum wallet detected. Open this page inside Rabby mobile browser.", "error");
            return;
        }}

        try {{
            showStatus("Connecting", "Requesting account access...");
            provider = new ethers.providers.Web3Provider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            signer = provider.getSigner();
            const address = await signer.getAddress();
            
            // Switch network automatically if not already on Robinhood Chain Mainnet
            let network = await provider.getNetwork();
            if (network.chainId !== 4663) {{
                showStatus("Switching Network", "Switching wallet network to Robinhood Chain Mainnet...");
                const success = await switchNetwork();
                if (!success) return;
                // Re-initialize provider
                await new Promise(r => setTimeout(r, 1000));
                provider = new ethers.providers.Web3Provider(window.ethereum);
                signer = provider.getSigner();
                network = await provider.getNetwork();
            }}

            if (network.chainId !== 4663) {{
                showStatus("Wrong Network", "Please switch your wallet network to Robinhood Chain Mainnet to deploy.", "error");
                return;
            }}
            
            connectBtn.innerText = `Connected: ${{address.substring(0, 6)}}...${{address.substring(38)}}`;
            connectBtn.style.background = "linear-gradient(135deg, #10b981, #059669)";
            connectBtn.style.color = "#fff";
            
            deployBtn.disabled = false;
            showStatus("Connected", `Ready to deploy. Network: Robinhood Chain Mainnet (Chain ID: 4663)`);
        }} catch (err) {{
            showStatus("Connection Failed", err.message, "error");
        }}
    }}

    async function deployContract() {{
        const payoutAddr = payoutInput.value.trim();
        if (!ethers.utils.isAddress(payoutAddr)) {{
            showStatus("Validation Error", "Please enter a valid payout recipient address.", "error");
            return;
        }}

        try {{
            deployBtn.disabled = true;
            showStatus("Deploying", "Preparing contract factory and transaction... Check your Rabby wallet to sign.");
            
            const factory = new ethers.ContractFactory(contractAbi, contractBytecode, signer);
            
            // Deploy passing the payout recipient parameter
            const contract = await factory.deploy(payoutAddr);
            
            showStatus("Broadcasting", `Transaction hash: ${{contract.deployTransaction.hash}}\\nWaiting for confirmations...`);
            
            await contract.deployed();
            
            showStatus("Success 🎉", `MemeFactory deployed successfully!\\nContract Address: ${{contract.address}}\\n\\nCopy this address and configure it as MEME_FACTORY_ADDRESS in your .env file.`, "success");
        }} catch (err) {{
            deployBtn.disabled = false;
            showStatus("Deployment Failed", err.message, "error");
        }}
    }}

    connectBtn.addEventListener("click", connectWallet);
    deployBtn.addEventListener("click", deployContract);
</script>

</body>
</html>
"""

    # 3. Write HTML file to workspace
    output_path = "deploy_app.html"
    with open(output_path, "w") as f:
        f.write(html_content)

    print(f"✅ Generated {output_path} successfully!")
    print(f"File path: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate()
