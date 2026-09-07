/* js/app.js - Robinhood Chain Sovereign Client Engine */

const ROBINHOOD_CONFIG = {
    chainName: 'Robinhood L2 Mainnet',
    chainId: '0x19B8', // 6584 in hex (example Robinhood Orbit ID)
    rpcUrl: 'https://rpc.mainnet.chain.robinhood.com',
    symbol: 'ETH',
    contracts: {
        memeFactory: '0xAb783574A8B12d580659e86F01dEA310Fb300113',
        robinMcp: '0xB6579E6489afC53Cd3eEb14eEF0EF039c65914bd',
        trustFactory: '0x8849F01A9652aBc2A370A02711F686a34B7630e6'
    }
};

let userAccount = null;
let provider = null;
let signer = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initCanvasBg();
    setupActiveNav();
    checkWalletConnection();
});

// Canvas Particle Effect
function initCanvasBg() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    
    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = Array.from({ length: 45 }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        size: Math.random() * 2 + 1,
        color: Math.random() > 0.5 ? 'rgba(251, 191, 36, ' : 'rgba(0, 255, 136, ',
        alpha: Math.random() * 0.5 + 0.1
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

// Highlight active page link
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
}

// Check & Connect Wallet
async function checkWalletConnection() {
    if (typeof window.ethereum !== 'undefined') {
        try {
            provider = new ethers.providers.Web3Provider(window.ethereum);
            const accounts = await provider.listAccounts();
            if (accounts.length > 0) {
                userAccount = accounts[0];
                signer = provider.getSigner();
                updateWalletUI();
            }
        } catch (e) {
            console.log("Wallet check error:", e);
        }
    }
}

async function connectWallet() {
    if (typeof window.ethereum === 'undefined') {
        showToast("No Web3 wallet detected! Install MetaMask or OKX Wallet.", "error");
        return;
    }
    try {
        provider = new ethers.providers.Web3Provider(window.ethereum);
        const accounts = await provider.send("eth_requestAccounts", []);
        userAccount = accounts[0];
        signer = provider.getSigner();
        updateWalletUI();
        showToast(`Connected: ${userAccount.substring(0, 6)}...${userAccount.substring(38)}`, "success");
    } catch (err) {
        showToast("Wallet connection cancelled.", "error");
    }
}

function updateWalletUI() {
    const walletBtns = document.querySelectorAll('.btn-wallet');
    walletBtns.forEach(btn => {
        btn.innerHTML = `🟢 ${userAccount.substring(0, 6)}...${userAccount.substring(38)}`;
        btn.style.background = 'rgba(0, 255, 136, 0.15)';
        btn.style.border = '1px solid #00ff88';
        btn.style.color = '#00ff88';
    });
}

// Toast System
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000);
}
