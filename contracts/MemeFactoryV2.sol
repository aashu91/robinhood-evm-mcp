// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MemeToken {
    string public name;
    string public symbol;
    uint8 public constant decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    address public factory;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(string memory _name, string memory _symbol, uint256 _totalSupply, address _creator) {
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply * 10**18;
        factory = msg.sender;

        // 80% is locked in the virtual bonding curve pool
        uint256 poolReserve = (totalSupply * 80) / 100;
        balanceOf[msg.sender] = poolReserve;
        emit Transfer(address(0), msg.sender, poolReserve);

        // 20% is sent to the token creator directly (initial developer allocation)
        uint256 creatorAllocation = totalSupply - poolReserve;
        balanceOf[_creator] = creatorAllocation;
        emit Transfer(address(0), _creator, creatorAllocation);
    }

    function transfer(address to, uint256 value) public returns (bool success) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) public returns (bool success) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) public returns (bool success) {
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Insufficient allowance");
        balanceOf[from] -= value;
        allowance[from][msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(from, to, value);
        return true;
    }

    // Allows factory to transfer tokens to manage bonding curve buy/sells
    function factoryTransfer(address from, address to, uint256 value) public returns (bool success) {
        require(msg.sender == factory, "Only factory can execute this");
        require(balanceOf[from] >= value, "Insufficient balance");
        balanceOf[from] -= value;
        balanceOf[to] += value;
        emit Transfer(from, to, value);
        return true;
    }
}

contract MemeFactoryV2 {
    address payable public feeRecipient;
    uint256 public constant deployFee = 0.005 ether;
    
    // Upgraded V2 Fee Parameters (Total 0.5% trading fee)
    uint256 public constant TRADING_FEE_BPS = 50; // 0.5% (50 basis points)
    uint256 public constant REFERRAL_SHARE_BPS = 2000; // 20% of the trading fee (0.1% of swap value)

    // Virtual pool constants
    uint256 public constant INITIAL_TOKEN_RESERVE = 800000000 * 10**18; // 800M tokens
    uint256 public constant VIRTUAL_ETH_RESERVE = 3 ether; // Virtual $k = 2.4 Billion
    uint256 public constant TARGET_ETH_RESERVE = 15 ether; // Curve finishes when pool has 15 real ETH

    struct TokenPool {
        uint256 tokenReserves;
        uint256 ethReserves;
        bool tradingActive;
        bool finalized;
    }

    mapping(address => TokenPool) public pools;
    address[] public allMemeTokens;

    event MemeDeployed(address indexed tokenAddress, string name, string symbol, address indexed creator);
    event TokenBought(address indexed tokenAddress, address indexed buyer, uint256 ethInput, uint256 tokenOutput, address indexed referrer);
    event TokenSold(address indexed tokenAddress, address indexed seller, uint256 tokenInput, uint256 ethOutput, address indexed referrer);
    event CurveFinalized(address indexed tokenAddress, uint256 totalEthCollected);

    constructor(address payable _feeRecipient) {
        feeRecipient = _feeRecipient;
    }

    function deployMemeToken(string memory name, string memory symbol, uint256 supply) public payable returns (address) {
        require(msg.value >= deployFee, "Insufficient deployment fee");
        feeRecipient.transfer(deployFee);

        // Deploy new Meme Token
        MemeToken newToken = new MemeToken(name, symbol, supply, msg.sender);
        address tokenAddr = address(newToken);

        pools[tokenAddr] = TokenPool({
            tokenReserves: INITIAL_TOKEN_RESERVE,
            ethReserves: VIRTUAL_ETH_RESERVE,
            tradingActive: true,
            finalized: false
        });

        allMemeTokens.push(tokenAddr);

        // Refund excess ETH
        if (msg.value > deployFee) {
            payable(msg.sender).transfer(msg.value - deployFee);
        }

        emit MemeDeployed(tokenAddr, name, symbol, msg.sender);
        return tokenAddr;
    }

    function buyMemeToken(address tokenAddress, address referrer) public payable {
        TokenPool storage pool = pools[tokenAddress];
        require(pool.tradingActive, "Trading is not active");
        require(!pool.finalized, "Bonding curve is already finalized");
        require(msg.value > 0, "Must send ETH");

        uint256 ethInput = msg.value;
        
        // Calculate fees (0.5% total)
        uint256 totalFee = (ethInput * TRADING_FEE_BPS) / 10000;
        uint256 netEthInput = ethInput - totalFee;

        // Process referral payout
        if (referrer != address(0) && referrer != msg.sender) {
            uint256 refPayout = (totalFee * REFERRAL_SHARE_BPS) / 10000;
            payable(referrer).transfer(refPayout);
            feeRecipient.transfer(totalFee - refPayout);
        } else {
            feeRecipient.transfer(totalFee);
        }

        uint256 k = pool.tokenReserves * pool.ethReserves;
        uint256 newEthReserves = pool.ethReserves + netEthInput;
        uint256 newDecimalTokens = k / newEthReserves;
        uint256 tokensToOutput = pool.tokenReserves - newDecimalTokens;

        require(tokensToOutput > 0, "Insufficient output amount");
        
        // Anti-Snipe: Maximum 2% of total supply (20 Million tokens) per transaction before 25% curve progress
        uint256 progress = ((INITIAL_TOKEN_RESERVE - pool.tokenReserves) * 100) / INITIAL_TOKEN_RESERVE;
        if (progress < 25) {
            uint256 maxBuy = 20000000 * 10**18;
            require(tokensToOutput <= maxBuy, "Anti-snipe: Exceeds 2% max buy per tx before 25% curve progress");
        }

        pool.ethReserves = newEthReserves;
        pool.tokenReserves = newDecimalTokens;

        // Transfer tokens to buyer
        MemeToken(tokenAddress).transfer(msg.sender, tokensToOutput);
        emit TokenBought(tokenAddress, msg.sender, netEthInput, tokensToOutput, referrer);

        // Check if curve has reached target reserve to finalize
        if (pool.ethReserves >= VIRTUAL_ETH_RESERVE + TARGET_ETH_RESERVE) {
            finalizePool(tokenAddress);
        }
    }

    function sellMemeToken(address tokenAddress, uint256 tokenAmount, address referrer) public {
        TokenPool storage pool = pools[tokenAddress];
        require(pool.tradingActive, "Trading is not active");
        require(!pool.finalized, "Pool finalized");
        require(tokenAmount > 0, "Must sell positive amount");

        uint256 k = pool.tokenReserves * pool.ethReserves;
        uint256 newTokenReserves = pool.tokenReserves + tokenAmount;
        uint256 newEthReserves = k / newTokenReserves;
        uint256 grossEthOutput = pool.ethReserves - newEthReserves;

        require(grossEthOutput > 0, "Insufficient ETH output");

        // Calculate fees (0.5%)
        uint256 totalFee = (grossEthOutput * TRADING_FEE_BPS) / 10000;
        uint256 netEthOutput = grossEthOutput - totalFee;

        // Process referral payout
        if (referrer != address(0) && referrer != msg.sender) {
            uint256 refPayout = (totalFee * REFERRAL_SHARE_BPS) / 10000;
            payable(referrer).transfer(refPayout);
            feeRecipient.transfer(totalFee - refPayout);
        } else {
            feeRecipient.transfer(totalFee);
        }

        pool.tokenReserves = newTokenReserves;
        pool.ethReserves = newEthReserves;

        // Pull tokens from user to factory
        MemeToken(tokenAddress).factoryTransfer(msg.sender, address(this), tokenAmount);
        
        // Send net ETH back to seller
        payable(msg.sender).transfer(netEthOutput);

        emit TokenSold(tokenAddress, msg.sender, tokenAmount, netEthOutput, referrer);
    }

    function finalizePool(address tokenAddress) internal {
        TokenPool storage pool = pools[tokenAddress];
        pool.finalized = true;
        pool.tradingActive = false;

        uint256 realEthCollected = pool.ethReserves - VIRTUAL_ETH_RESERVE;
        
        // Transfer collected real ETH to feeRecipient to list LP on DEX
        feeRecipient.transfer(realEthCollected);

        emit CurveFinalized(tokenAddress, realEthCollected);
    }

    function getMemeCount() public view returns (uint256) {
        return allMemeTokens.length;
    }
}
