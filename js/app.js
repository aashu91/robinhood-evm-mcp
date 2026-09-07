/* js/app.js - Robinhood Chain Sovereign Client Engine & Web3 Integration */
/* ponytail: Client engine relies on native localStorage & Web Audio with zero external UI dependencies */

const ROBINHOOD_CONFIG = {
    chainName: 'Robinhood L2 Testnet',
    chainId: '0x19B8', // 6584 decimal
    rpcMainnet: 'https://rpc.mainnet.chain.robinhood.com',
    rpcTestnet: 'https://rpc.testnet.chain.robinhood.com',
    symbol: 'ETH',
    contracts: {
        memeFactoryV2: '0xAb783574A8B12d580659e86F01dEA310Fb300113',
        robinMcp: '0xB6579E6489afC53Cd3eEb14eEF0EF039c65914bd',
        trustFactory: '0x8849F01A9652aBc2A370A02711F686a34B7630e6'
    }
};

const MEME_FACTORY_ABI = [
    "function deployMemeToken(string name, string symbol, uint256 supply) payable returns (address)",
    "function buyMemeToken(address tokenAddress, address referrer) payable",
    "function sellMemeToken(address tokenAddress, uint256 tokenAmount, address referrer)",
    "function pools(address tokenAddress) view returns (uint256 tokenReserves, uint256 ethReserves, bool tradingActive, bool finalized)",
    "function getMemeCount() view returns (uint256)",
    "function allMemeTokens(uint256 index) view returns (address)",
    "function deployFee() view returns (uint256)"
];

// App Core State
let userAccount = null;
let provider = null;
let signer = null;
let isWeb3Mode = false; // Default false (Paper Trading Simulator mode enabled by default)

// Persistent Data Store Manager
const Storage = {
    getMode() {
        return localStorage.getItem('rh_mode') || 'paper';
    },
    setMode(mode) {
        localStorage.setItem('rh_mode', mode);
    },
    getPaperEth() {
        const val = localStorage.getItem('rh_paper_eth');
        return val !== null ? parseFloat(val) : 10.0;
    },
    setPaperEth(val) {
        localStorage.setItem('rh_paper_eth', val.toFixed(4));
    },
    getTokens() {
        const data = localStorage.getItem('rh_tokens');
        if (data) return JSON.parse(data);

        // Default pre-loaded Robinhood Chain ecosystem tokens
        const defaults = [
            {
                address: '0x1111111111111111111111111111111111111111',
                name: 'TSLAx Tesla Proxy',
                symbol: 'TSLAx',
                type: 'RWA',
                priceEth: 0.054,
                ethReserves: 5.48,
                targetEth: 6.0,
                tokenReserves: 70000000,
                totalSupply: 1000000000,
                progress: 91.4,
                koth: true,
                royalty: 0.50,
                creator: '0x71C...89A'
            },
            {
                address: '0x2222222222222222222222222222222222222222',
                name: 'AAPL Equity Proxy',
                symbol: 'AAPL',
                type: 'RWA',
                priceEth: 0.042,
                ethReserves: 4.68,
                targetEth: 6.0,
                tokenReserves: 220000000,
                totalSupply: 1000000000,
                progress: 78.0,
                koth: false,
                royalty: 0.50,
                creator: '0x89A...311'
            },
            {
                address: '0x3333333333333333333333333333333333333333',
                name: 'NVDAx Nvidia AI Proxy',
                symbol: 'NVDAx',
                type: 'RWA',
                priceEth: 0.031,
                ethReserves: 2.71,
                targetEth: 6.0,
                tokenReserves: 550000000,
                totalSupply: 1000000000,
                progress: 45.2,
                koth: false,
                royalty: 0.50,
                creator: '0x3a4...91f'
            },
            {
                address: '0x4444444444444444444444444444444444444444',
                name: 'USDG Yield Stablecoin',
                symbol: 'USDG',
                type: 'Meme',
                priceEth: 0.00031,
                ethReserves: 6.0,
                targetEth: 6.0,
                tokenReserves: 0,
                totalSupply: 1000000000,
                progress: 100.0,
                graduated: true,
                koth: false,
                royalty: 0.25,
                creator: '0x000...000'
            }
        ];
        localStorage.setItem('rh_tokens', JSON.stringify(defaults));
        return defaults;
    },
    saveTokens(tokens) {
        localStorage.setItem('rh_tokens', JSON.stringify(tokens));
    },
    getHoldings() {
        const data = localStorage.getItem('rh_holdings');
        return data ? JSON.parse(data) : { 'TSLAx': 1420.0, 'AAPL': 500.0 };
    },
    saveHoldings(holdings) {
        localStorage.setItem('rh_holdings', JSON.stringify(holdings));
    },
    getCreatedTokens() {
        const data = localStorage.getItem('rh_my_tokens');
        return data ? JSON.parse(data) : [];
    },
    addCreatedToken(token) {
        const list = this.getCreatedTokens();
        list.push(token);
        localStorage.setItem('rh_my_tokens', JSON.stringify(list));
    },
    getReferralEarnings() {
        return parseFloat(localStorage.getItem('rh_ref_earnings') || '0.0425');
    },
    addReferralEarnings(amt) {
        const curr = this.getReferralEarnings();
        localStorage.setItem('rh_ref_earnings', (curr + amt).toFixed(6));
    },
    getActiveReferrer() {
        return localStorage.getItem('rh_active_referrer') || '0x71C735Cc06e8a571618a3f228bde719eac01ef11';
    },
    setActiveReferrer(ref) {
        localStorage.setItem('rh_active_referrer', ref);
    }
};

// Application Lifecycle Entrypoint
document.addEventListener('DOMContentLoaded', async () => {
    initParticleBg();
    setupActiveNav();
    parseReferralParam();
    injectWalletDrawerHTML();
    
    // Initialize Web3 / Paper Mode
    const savedMode = Storage.getMode();
    isWeb3Mode = (savedMode === 'web3');
    updateModeSwitchUI();

    await checkWalletConnection();
    initPageComponents();
});

// Parse ?ref= from URL
function parseReferralParam() {
    const params = new URLSearchParams(window.location.search);
    const ref = params.get('ref');
    if (ref && ref.startsWith('0x')) {
        Storage.setActiveReferrer(ref);
    }
}

// Particle Canvas Background Renderer
function initParticleBg() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    
    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = Array.from({ length: 40 }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        size: Math.random() * 2 + 1,
        color: Math.random() > 0.5 ? 'rgba(251, 191, 36, ' : 'rgba(0, 255, 136, ',
        alpha: Math.random() * 0.4 + 0.1
    }));

    function animate() {
        ctx.clearRect(0, 0, width, height);
        particles.forEach(p => {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < 0) p.x = width;
            if (p.x > width) p.x = 0;
            if (p.y < 0) p.y = height;
            if (p.y > height) p.y = 0;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color + p.alpha + ')';
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

// Highlight current page navigation link
function setupActiveNav() {
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-item a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Add Mode Switch Pill into Navbar Controls if absent
    const nav = document.querySelector('.navbar');
    if (nav && !document.getElementById('mode-switch-container')) {
        const controls = document.createElement('div');
        controls.className = 'nav-controls';
        controls.id = 'mode-switch-container';
        controls.innerHTML = `
            <div class="mode-switch-pill" onclick="toggleModeSwitch()" title="Toggle Web3 Testnet vs Paper Trading Simulator">
                <span id="badge-web3" class="mode-badge">🌐 Web3</span>
                <span id="badge-paper" class="mode-badge">🎮 Simulator</span>
            </div>
            <button class="btn-wallet" onclick="openWalletDrawer()">Connect Wallet</button>
        `;

        // Remove old wallet button if present
        const oldWalletBtn = nav.querySelector('.btn-wallet');
        if (oldWalletBtn) oldWalletBtn.remove();
        nav.appendChild(controls);
    }
}

// Toggle Web3 Mode vs Paper Simulator
function toggleModeSwitch() {
    isWeb3Mode = !isWeb3Mode;
    Storage.setMode(isWeb3Mode ? 'web3' : 'paper');
    updateModeSwitchUI();
    playAudioChime('chime');
    
    if (isWeb3Mode) {
        connectWallet();
    } else {
        showToast("Switched to 🎮 Paper Trading Simulator (10.0 Virtual ETH)", "success");
        updateWalletUI();
        renderWalletDrawer();
    }
}

function updateModeSwitchUI() {
    const bWeb3 = document.getElementById('badge-web3');
    const bPaper = document.getElementById('badge-paper');
    if (!bWeb3 || !bPaper) return;

    if (isWeb3Mode) {
        bWeb3.className = 'mode-badge active-web3';
        bPaper.className = 'mode-badge';
    } else {
        bWeb3.className = 'mode-badge';
        bPaper.className = 'mode-badge active-paper';
    }
}

// Wallet Connection Manager (Web3 + Fallback Paper Mode)
async function checkWalletConnection() {
    if (isWeb3Mode && typeof window.ethereum !== 'undefined') {
        try {
            provider = new ethers.providers.Web3Provider(window.ethereum);
            const accounts = await provider.listAccounts();
            if (accounts.length > 0) {
                userAccount = accounts[0];
                signer = provider.getSigner();
                updateWalletUI();
                return;
            }
        } catch (e) {
            console.log("Wallet detection error:", e);
        }
    }
    
    // Default Fallback Account
    if (!userAccount) {
        userAccount = '0x71C735Cc06e8a571618a3f228bde719eac01ef11';
    }
    updateWalletUI();
}

async function connectWallet() {
    if (isWeb3Mode) {
        if (typeof window.ethereum === 'undefined') {
            showToast("No Web3 wallet detected. Falling back to Paper Simulator.", "error");
            isWeb3Mode = false;
            Storage.setMode('paper');
            updateModeSwitchUI();
            updateWalletUI();
            return;
        }
        try {
            provider = new ethers.providers.Web3Provider(window.ethereum);
            const accounts = await provider.send("eth_requestAccounts", []);
            userAccount = accounts[0];
            signer = provider.getSigner();
            updateWalletUI();
            showToast(`Web3 Connected: ${userAccount.substring(0, 6)}...${userAccount.substring(38)}`, "success");
            playAudioChime('chime');
        } catch (err) {
            showToast("Wallet connection cancelled.", "error");
        }
    } else {
        openWalletDrawer();
    }
}

function updateWalletUI() {
    const walletBtns = document.querySelectorAll('.btn-wallet');
    walletBtns.forEach(btn => {
        const modeLabel = isWeb3Mode ? '[WEB3]' : '[SIMULATOR]';
        const displayAddr = userAccount ? `${userAccount.substring(0, 6)}...${userAccount.substring(38)}` : '0x71C...89A';
        btn.innerHTML = `${modeLabel} ${displayAddr}`;
        if (isWeb3Mode) {
            btn.style.background = 'rgba(0, 240, 255, 0.15)';
            btn.style.border = '1px solid #00f0ff';
            btn.style.color = '#00f0ff';
        } else {
            btn.style.background = 'rgba(0, 255, 136, 0.15)';
            btn.style.border = '1px solid #00ff88';
            btn.style.color = '#00ff88';
        }
    });
}

/* ==========================================================================
   👛 WALLET PROFILE DRAWER CONTROLLER
   ========================================================================== */

function injectWalletDrawerHTML() {
    if (document.getElementById('wallet-drawer-backdrop')) return;
    
    const backdrop = document.createElement('div');
    backdrop.className = 'drawer-backdrop';
    backdrop.id = 'wallet-drawer-backdrop';
    backdrop.onclick = (e) => {
        if (e.target === backdrop) closeWalletDrawer();
    };

    backdrop.innerHTML = `
        <div class="wallet-drawer">
            <div class="drawer-header">
                <div class="drawer-title">
                    <span style="color: var(--gold);">⚡</span> Wallet Profile
                </div>
                <button class="btn-close-drawer" onclick="closeWalletDrawer()">&times;</button>
            </div>
            <div class="drawer-body" id="drawer-body-content">
                <!-- Rendered dynamically -->
            </div>
        </div>
    `;
    document.body.appendChild(backdrop);
}

function openWalletDrawer() {
    renderWalletDrawer();
    const backdrop = document.getElementById('wallet-drawer-backdrop');
    if (backdrop) backdrop.classList.add('open');
}

function closeWalletDrawer() {
    const backdrop = document.getElementById('wallet-drawer-backdrop');
    if (backdrop) backdrop.classList.remove('open');
}

function renderWalletDrawer() {
    const body = document.getElementById('drawer-body-content');
    if (!body) return;

    const paperEth = Storage.getPaperEth();
    const holdings = Storage.getHoldings();
    const createdTokens = Storage.getCreatedTokens();
    const refEarnings = Storage.getReferralEarnings();
    const activeRef = Storage.getActiveReferrer();

    let holdingsHTML = '';
    let totalPortfolioEth = isWeb3Mode ? 1.45 : paperEth;

    const tokens = Storage.getTokens();
    Object.keys(holdings).forEach(ticker => {
        const qty = holdings[ticker];
        const tokenObj = tokens.find(t => t.symbol === ticker) || { priceEth: 0.001 };
        const valEth = qty * tokenObj.priceEth;
        totalPortfolioEth += valEth;

        holdingsHTML += `
            <div class="portfolio-item">
                <div>
                    <div class="sym">${ticker}</div>
                    <div style="font-size: 11px; color: var(--text-muted);">${qty.toLocaleString()} Tokens</div>
                </div>
                <div class="bal">${valEth.toFixed(4)} ETH</div>
            </div>
        `;
    });

    let createdHTML = '';
    if (createdTokens.length === 0) {
        createdHTML = `<div style="font-size: 12px; color: var(--text-sub); font-style: italic;">No tokens created yet.</div>`;
    } else {
        createdTokens.forEach(t => {
            createdHTML += `
                <div class="portfolio-item">
                    <div>
                        <div class="sym">$${t.symbol}</div>
                        <div style="font-size: 11px; color: var(--text-muted);">${t.name}</div>
                    </div>
                    <div style="color: var(--gold); font-weight: 700; font-size: 11px;">${t.royalty}% Royalty</div>
                </div>
            `;
        });
    }

    body.innerHTML = `
        <div class="drawer-section" style="background: rgba(3, 7, 18, 0.8); border: 1px solid var(--border-gold); padding: 16px; border-radius: 14px;">
            <div style="font-size: 11px; color: var(--text-muted); font-family: var(--font-mono); margin-bottom: 4px;">ACTIVE ADDRESS (${isWeb3Mode ? 'Testnet Web3' : 'Paper Simulator'})</div>
            <div style="font-family: var(--font-mono); font-size: 13px; font-weight: 700; color: var(--gold); word-break: break-all;">
                ${userAccount}
            </div>
            <div style="display: flex; gap: 8px; margin-top: 10px;">
                <button class="btn-secondary" style="font-size: 11px; padding: 4px 10px;" onclick="copyToClipboard('${userAccount}', 'Address copied!')">Copy Address</button>
                <button class="btn-secondary" style="font-size: 11px; padding: 4px 10px;" onclick="toggleModeSwitch()">${isWeb3Mode ? 'Switch to Paper Mode' : 'Switch to Web3'}</button>
            </div>
        </div>

        <div class="drawer-section">
            <div class="drawer-section-title">Portfolio Balance & Net Worth</div>
            <div style="font-family: var(--font-mono); font-size: 28px; font-weight: 900; color: var(--emerald);">
                ${isWeb3Mode ? '1.4500 ETH' : `${paperEth.toFixed(4)} ETH`}
            </div>
            <div style="font-size: 12px; color: var(--text-muted);">Est. Total Value: ~${totalPortfolioEth.toFixed(4)} ETH</div>
            ${!isWeb3Mode ? `<button class="btn-secondary" style="font-size: 11px; padding: 4px 10px; margin-top: 8px;" onclick="resetPaperBalance()">Reset to 10.0 ETH</button>` : ''}
        </div>

        <div class="drawer-section">
            <div class="drawer-section-title">Token Holdings</div>
            <div class="portfolio-list">${holdingsHTML || '<div style="font-size: 12px; color: var(--text-sub);">No token holdings.</div>'}</div>
        </div>

        <div class="drawer-section">
            <div class="drawer-section-title">Tokens You Created</div>
            <div class="created-tokens-list">${createdHTML}</div>
        </div>

        <div class="drawer-section" style="background: rgba(0, 255, 136, 0.08); border: 1px solid var(--border-emerald); padding: 14px; border-radius: 14px;">
            <div class="drawer-section-title" style="color: var(--emerald);">Referral Earnings (0.25% Revenue Share)</div>
            <div style="font-family: var(--font-mono); font-size: 20px; font-weight: 800; color: var(--gold);">${refEarnings.toFixed(4)} ETH</div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Active Sponsor: ${activeRef.substring(0, 6)}...${activeRef.substring(38)}</div>
            <button class="btn-primary" style="font-size: 12px; padding: 6px 14px; margin-top: 8px; width: 100%; justify-content: center;" onclick="copyReferralLink()">Copy Your Referral Link &rarr;</button>
        </div>
    `;
}

function resetPaperBalance() {
    Storage.setPaperEth(10.0);
    showToast("Paper wallet balance reset to 10.0 ETH!", "success");
    renderWalletDrawer();
    playAudioChime('chime');
}

/* ==========================================================================
   📈 INTERACTIVE LIVE OHLC TRADING CHART ENGINE (CANVAS BASED)
   ========================================================================== */

// Synthetic OHLC Generator & Renderer
function renderOhlcChart(canvasId, ticker = 'TSLAx', timeframe = '1H', chartType = 'line') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // High-DPI Scaling
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    const width = rect.width;
    const height = rect.height;

    // Generate Synthetic Data Points based on ticker & timeframe
    const tokens = Storage.getTokens();
    const tokenObj = tokens.find(t => t.symbol === ticker) || { priceEth: 0.054 };
    const basePrice = tokenObj.priceEth;

    const pointCount = timeframe === '1M' ? 30 : timeframe === '5M' ? 45 : timeframe === '1H' ? 60 : 80;
    const points = [];
    let currPrice = basePrice * 0.75;
    
    for (let i = 0; i < pointCount; i++) {
        const volatility = basePrice * 0.03;
        const change = (Math.random() - 0.48) * volatility;
        const open = currPrice;
        const close = Math.max(basePrice * 0.1, open + change);
        const high = Math.max(open, close) + Math.random() * volatility * 0.5;
        const low = Math.min(open, close) - Math.random() * volatility * 0.5;
        currPrice = close;
        points.push({ open, high, low, close });
    }
    // Set last point to current price
    points[points.length - 1].close = basePrice;

    // Clear Canvas
    ctx.clearRect(0, 0, width, height);

    // Padding
    const pTop = 20, pBottom = 30, pLeft = 10, pRight = 65;
    const chartW = width - pLeft - pRight;
    const chartH = height - pTop - pBottom;

    // Min & Max Price Calculation
    let minP = Math.min(...points.map(p => p.low));
    let maxP = Math.max(...points.map(p => p.high));
    const rangeP = (maxP - minP) || 0.001;
    minP -= rangeP * 0.05;
    maxP += rangeP * 0.05;

    // Draw Grid Lines & Price Axis Labels
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#64748b';
    ctx.font = '11px JetBrains Mono';
    ctx.textAlign = 'left';

    const gridRows = 4;
    for (let i = 0; i <= gridRows; i++) {
        const y = pTop + (chartH / gridRows) * i;
        const priceVal = maxP - ((maxP - minP) / gridRows) * i;
        
        ctx.beginPath();
        ctx.moveTo(pLeft, y);
        ctx.lineTo(width - pRight, y);
        ctx.stroke();

        ctx.fillText(priceVal.toFixed(5), width - pRight + 8, y + 4);
    }

    // Draw Series (Candlestick vs Line)
    const stepX = chartW / (points.length - 1);

    if (chartType === 'line') {
        ctx.beginPath();
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 2;

        points.forEach((p, i) => {
            const x = pLeft + i * stepX;
            const y = pTop + chartH - ((p.close - minP) / (maxP - minP)) * chartH;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Area Gradient Fill
        const gradient = ctx.createLinearGradient(0, pTop, 0, height - pBottom);
        gradient.addColorStop(0, 'rgba(0, 255, 136, 0.25)');
        gradient.addColorStop(1, 'rgba(0, 255, 136, 0.0)');

        ctx.lineTo(pLeft + (points.length - 1) * stepX, height - pBottom);
        ctx.lineTo(pLeft, height - pBottom);
        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();
    } else {
        // Candlestick Rendering
        const candleW = Math.max(2, stepX * 0.6);

        points.forEach((p, i) => {
            const x = pLeft + i * stepX;
            const yOpen = pTop + chartH - ((p.open - minP) / (maxP - minP)) * chartH;
            const yClose = pTop + chartH - ((p.close - minP) / (maxP - minP)) * chartH;
            const yHigh = pTop + chartH - ((p.high - minP) / (maxP - minP)) * chartH;
            const yLow = pTop + chartH - ((p.low - minP) / (maxP - minP)) * chartH;

            const isUp = p.close >= p.open;
            const color = isUp ? '#00ff88' : '#ff0066';

            // Wick
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, yHigh);
            ctx.lineTo(x, yLow);
            ctx.stroke();

            // Candle Body
            ctx.fillStyle = color;
            const bodyY = Math.min(yOpen, yClose);
            const bodyH = Math.max(2, Math.abs(yClose - yOpen));
            ctx.fillRect(x - candleW / 2, bodyY, candleW, bodyH);
        });
    }
}

/* ==========================================================================
   🚀 MEME & RWA TOKEN LAUNCH & SWAP CONTRACT INTEROPERABILITY
   ========================================================================== */

// Deploy Token Form Handler
async function deployMemeToken() {
    const nameInput = document.getElementById('token-name');
    const symbolInput = document.getElementById('token-symbol');
    const royaltyInput = document.getElementById('token-royalty');
    
    if (!nameInput || !symbolInput) return;

    const name = nameInput.value.trim();
    const symbol = symbolInput.value.trim().toUpperCase();
    const royalty = parseFloat(royaltyInput ? royaltyInput.value : '0.50') || 0.50;

    if (!name || !symbol) {
        showToast("Please specify both Token Name and Symbol!", "error");
        return;
    }

    const currentTab = window.currentLaunchTab || 'meme';
    const typeStr = currentTab === 'rwa' ? 'Stock-Backed RWA Proxy' : 'Fair-Launch Meme Token';

    showToast(`Deploying ${typeStr} $${symbol} on Robinhood Chain L2...`, "info");

    if (isWeb3Mode && signer) {
        try {
            const factory = new ethers.Contract(ROBINHOOD_CONFIG.contracts.memeFactoryV2, MEME_FACTORY_ABI, signer);
            const tx = await factory.deployMemeToken(name, symbol, ethers.utils.parseEther("1000000000"), {
                value: ethers.utils.parseEther("0.0001")
            });
            showToast(`Tx Broadcasted: ${tx.hash.substring(0, 10)}... Waiting confirmation`, "info");
            await tx.wait();
            showToast(`Token $${symbol} deployed on-chain!`, "success");
        } catch (err) {
            console.log("Web3 Deploy Error:", err);
            showToast("Web3 tx rejected/failed. Falling back to Paper Trading deployment.", "error");
            executePaperDeploy(name, symbol, royalty, typeStr);
            return;
        }
    } else {
        setTimeout(() => {
            executePaperDeploy(name, symbol, royalty, typeStr);
        }, 1200);
    }
}

function executePaperDeploy(name, symbol, royalty, typeStr) {
    const mockAddr = '0x' + Array.from({length: 40}, () => Math.floor(Math.random()*16).toString(16)).join('');
    
    const newToken = {
        address: mockAddr,
        name: name,
        symbol: symbol,
        type: typeStr.includes('RWA') ? 'RWA' : 'Meme',
        priceEth: 0.0001,
        ethReserves: 0.0001,
        targetEth: 6.0,
        tokenReserves: 800000000,
        totalSupply: 1000000000,
        progress: 0.1,
        koth: false,
        royalty: royalty,
        creator: userAccount ? `${userAccount.substring(0, 6)}...${userAccount.substring(38)}` : '0x71C...89A'
    };

    const tokens = Storage.getTokens();
    tokens.unshift(newToken);
    Storage.saveTokens(tokens);

    Storage.addCreatedToken(newToken);
    playAudioChime('launch');
    showToast(`Token $${symbol} deployed successfully! Bonding curve active.`, "success");

    // Add activity feed item if feed exists
    addFeedItem(`🔥 User deployed <strong style="color: var(--gold);">$${symbol}</strong> (${typeStr}) with ${royalty}% Royalty`, 'Just Now');

    // Refresh Token Grid UI
    renderTokenGrid();
}

// Execute Buy / Sell Swap Transaction
async function executeMemeTrade() {
    const amountInput = document.getElementById('trade-amount');
    const tickerSelect = document.getElementById('trade-ticker');
    if (!amountInput || !tickerSelect) return;

    const ethAmt = parseFloat(amountInput.value) || 0;
    const ticker = tickerSelect.value;
    const tradeMode = window.currentTradeMode || 'buy';

    if (ethAmt <= 0) {
        showToast("Please enter a valid amount!", "error");
        return;
    }

    const referrer = Storage.getActiveReferrer();
    showToast(`Executing ${tradeMode.toUpperCase()} order for ${ethAmt} ETH of $${ticker}...`, "info");

    if (isWeb3Mode && signer) {
        try {
            const factory = new ethers.Contract(ROBINHOOD_CONFIG.contracts.memeFactoryV2, MEME_FACTORY_ABI, signer);
            const tokens = Storage.getTokens();
            const tokenObj = tokens.find(t => t.symbol === ticker) || tokens[0];

            if (tradeMode === 'buy') {
                const tx = await factory.buyMemeToken(tokenObj.address, referrer, {
                    value: ethers.utils.parseEther(ethAmt.toString())
                });
                showToast(`Buy Tx Broadcasted: ${tx.hash.substring(0, 10)}...`, "info");
                await tx.wait();
            } else {
                const tokenAmt = ethers.utils.parseEther((ethAmt * 6857).toString());
                const tx = await factory.sellMemeToken(tokenObj.address, tokenAmt, referrer);
                showToast(`Sell Tx Broadcasted: ${tx.hash.substring(0, 10)}...`, "info");
                await tx.wait();
            }
            showToast(`On-chain swap executed cleanly!`, "success");
        } catch (err) {
            console.log("Web3 Swap Error:", err);
            showToast("Web3 Swap error. Executing via Paper Simulator.", "error");
            executePaperTrade(ticker, tradeMode, ethAmt, referrer);
            return;
        }
    } else {
        setTimeout(() => {
            executePaperTrade(ticker, tradeMode, ethAmt, referrer);
        }, 1000);
    }
}

function executePaperTrade(ticker, tradeMode, ethAmt, referrer) {
    let paperEth = Storage.getPaperEth();
    
    if (tradeMode === 'buy' && paperEth < ethAmt) {
        showToast("Insufficient ETH balance in Paper Wallet!", "error");
        return;
    }

    // Update Token Bonding Curve State
    const tokens = Storage.getTokens();
    const tokenIdx = tokens.findIndex(t => t.symbol === ticker);
    if (tokenIdx === -1) return;

    const token = tokens[tokenIdx];

    if (tradeMode === 'buy') {
        paperEth -= ethAmt;
        token.ethReserves += ethAmt;
        const tokensPurchased = ethAmt * (800000000 / (token.ethReserves + 6.0));
        token.tokenReserves = Math.max(0, token.tokenReserves - tokensPurchased);
        token.progress = Math.min(100.0, (token.ethReserves / token.targetEth) * 100.0);
        token.priceEth = (token.ethReserves / Math.max(1, token.tokenReserves)) * 1000;

        // Update User Holdings
        const holdings = Storage.getHoldings();
        holdings[ticker] = (holdings[ticker] || 0) + tokensPurchased;
        Storage.saveHoldings(holdings);

        // Add 0.25% Referral Share to sponsor
        Storage.addReferralEarnings(ethAmt * 0.0025);

        playAudioChime('buy');
        showToast(`Bought ${tokensPurchased.toFixed(2)} $${ticker} for ${ethAmt} ETH!`, "success");
        addFeedItem(`⚡ User BOUGHT ${tokensPurchased.toFixed(1)} <strong style="color: var(--cyan);">$${ticker}</strong>`, 'Just Now');
    } else {
        const holdings = Storage.getHoldings();
        const userTokenBal = holdings[ticker] || 0;
        if (userTokenBal <= 0) {
            showToast(`You have 0 $${ticker} to sell!`, "error");
            return;
        }

        const sellTokens = Math.min(userTokenBal, ethAmt * 6857.0);
        const returnEth = ethAmt;
        paperEth += returnEth;
        holdings[ticker] = userTokenBal - sellTokens;
        Storage.saveHoldings(holdings);

        token.ethReserves = Math.max(0.0001, token.ethReserves - returnEth);
        token.tokenReserves += sellTokens;
        token.progress = Math.min(100.0, (token.ethReserves / token.targetEth) * 100.0);

        playAudioChime('sell');
        showToast(`Sold ${sellTokens.toFixed(2)} $${ticker} for ${returnEth} ETH!`, "success");
        addFeedItem(`🔴 User SOLD ${sellTokens.toFixed(1)} <strong style="color: var(--pink);">$${ticker}</strong>`, 'Just Now');
    }

    // Check KOTH recalculation
    tokens.forEach(t => t.koth = false);
    let highestProgressToken = tokens.reduce((prev, current) => (prev.progress > current.progress) ? prev : current);
    highestProgressToken.koth = true;

    Storage.setPaperEth(paperEth);
    Storage.saveTokens(tokens);

    // Refresh UI
    renderTokenGrid();
    renderOhlcChart('ohlc-canvas', ticker, '1H', 'line');
    if (document.getElementById('wallet-drawer-backdrop')?.classList.contains('open')) {
        renderWalletDrawer();
    }
}

// Render Dynamic Token Grid on Launchpad / Index
function renderTokenGrid() {
    const grid = document.getElementById('token-grid');
    if (!grid) return;

    const tokens = Storage.getTokens();
    grid.innerHTML = '';

    tokens.forEach(t => {
        const isKoth = t.koth;
        const card = document.createElement('div');
        card.className = 'glass-card';
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                <div>
                    <h4 style="font-size: 19px; font-weight: 800;">${t.name}</h4>
                    <span style="font-family: var(--font-mono); font-size: 12px; color: var(--gold);">$${t.symbol}</span>
                    <span class="rwa-badge" style="margin-left: 6px;">${t.type}</span>
                </div>
                ${isKoth ? `<span style="background: rgba(251,191,36,0.15); color: var(--gold); font-family: var(--font-mono); font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 700;">👑 KOTH #1</span>` : `<span style="background: rgba(0,240,255,0.15); color: var(--cyan); font-family: var(--font-mono); font-size: 11px; padding: 2px 8px; border-radius: 4px;">BONDING ${t.progress.toFixed(1)}%</span>`}
            </div>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">Creator Royalty: ${t.royalty}% • Creator: ${t.creator}</p>
            <div style="font-family: var(--font-mono); font-size: 12px; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span>Price: ${t.priceEth.toFixed(5)} ETH</span>
                    <span style="color: var(--gold);">Raised: ${t.ethReserves.toFixed(2)} ETH</span>
                </div>
                <div class="bonding-progress-track">
                    <div class="bonding-progress-fill" style="width: ${t.progress.toFixed(1)}%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                    <span>Progress: ${t.progress.toFixed(1)}%</span>
                    <span>Target: 6.00 ETH</span>
                </div>
            </div>
            <button class="btn-secondary" style="width: 100%; justify-content: center; font-size: 13px;" onclick="selectToken('${t.symbol}')">Trade ${t.symbol}</button>
        `;
        grid.appendChild(card);
    });
}

function selectToken(ticker) {
    const tradeSelect = document.getElementById('trade-ticker');
    if (tradeSelect) {
        tradeSelect.value = ticker;
        if (typeof calculateTradeOutput === 'function') calculateTradeOutput();
    }
    renderOhlcChart('ohlc-canvas', ticker, '1H', 'line');
    showToast(`Loaded ${ticker} price chart & trade terminal.`, "info");
    window.scrollTo({ top: 350, behavior: 'smooth' });
}

// Activity Stream Injector
function addFeedItem(htmlContent, timeStr) {
    const feed = document.getElementById('live-feed-container');
    if (!feed) return;
    const item = document.createElement('div');
    item.className = 'live-feed-item';
    item.innerHTML = `<div>${htmlContent}</div><div style="color: var(--text-muted);">${timeStr}</div>`;
    feed.insertBefore(item, feed.firstChild);
}

// Referral Link Copy Utility
function copyReferralLink() {
    const myAddr = userAccount || '0x71C735Cc06e8a571618a3f228bde719eac01ef11';
    const link = `https://launchpad.chain.robinhood.com?ref=${myAddr}`;
    copyToClipboard(link, "Referral link copied! Share to earn 0.25% revenue share.");
    playAudioChime('chime');
}

function copyToClipboard(text, successMsg) {
    navigator.clipboard.writeText(text);
    showToast(successMsg, "success");
}

// Web Audio API Synthesizer Chimes
function playAudioChime(type = 'chime') {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        const now = ctx.currentTime;

        if (type === 'buy') {
            osc.frequency.setValueAtTime(440, now); // A4
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.15); // A5
        } else if (type === 'sell') {
            osc.frequency.setValueAtTime(659.25, now); // E5
            osc.frequency.exponentialRampToValueAtTime(329.63, now + 0.15); // E4
        } else if (type === 'launch') {
            osc.frequency.setValueAtTime(523.25, now); // C5
            osc.frequency.exponentialRampToValueAtTime(1046.50, now + 0.25); // C6
        } else {
            osc.frequency.setValueAtTime(587.33, now); // D5
            osc.frequency.exponentialRampToValueAtTime(783.99, now + 0.12); // G5
        }

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(now + 0.25);
    } catch (e) {
        // Ignored if audio context unallowed
    }
}

// Global Toast System
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast';
    const tag = type === 'error' ? '[ERROR]' : type === 'success' ? '[SUCCESS]' : '[INFO]';
    const tagColor = type === 'error' ? 'var(--pink)' : type === 'success' ? 'var(--emerald)' : 'var(--gold)';
    
    toast.innerHTML = `<span style="font-family: var(--font-mono); font-size: 11px; font-weight: 700; color: ${tagColor};">${tag}</span> <div>${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3800);
}

// Page Components Initializer
function initPageComponents() {
    renderTokenGrid();
    if (document.getElementById('ohlc-canvas')) {
        renderOhlcChart('ohlc-canvas', 'TSLAx', '1H', 'line');
    }
}
