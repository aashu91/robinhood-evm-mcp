// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MemeToken {
    string public name;
    string public symbol;
    uint8 public decimals = 18;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(string memory _name, string memory _symbol, uint256 _totalSupply, address creator) {
        name = _name;
        symbol = _symbol;
        totalSupply = _totalSupply;
        balanceOf[creator] = _totalSupply;
        emit Transfer(address(0), creator, _totalSupply);
    }

    function transfer(address to, uint256 value) public returns (bool) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) public returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    // Special transfer function allowed only for the factory to manage pools
    function factoryTransfer(address from, address to, uint256 value) public returns (bool) {
        require(balanceOf[from] >= value, "Insufficient balance");
        balanceOf[from] -= value;
        balanceOf[to] += value;
        emit Transfer(from, to, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) public returns (bool) {
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Insufficient allowance");
        allowance[from][msg.sender] -= value;
        balanceOf[from] -= value;
        balanceOf[to] += value;
        emit Transfer(from, to, value);
        return true;
    }
}

contract MemeFactory {
    struct TokenPool {
        address tokenAddress;
        uint256 tokenReserves;
        uint256 ethReserves;
        bool tradingActive;
    }

    address payable public feeRecipient;
    uint256 public deployFee = 0.005 ether;
    
    // Constant product virtual parameters
    uint256 public constant INITIAL_TOKEN_RESERVE = 800_000_000 * 10**18;
    uint256 public constant VIRTUAL_ETH_RESERVE = 5 ether;

    mapping(address => TokenPool) public pools;
    address[] public allMemeTokens;

    event MemeDeployed(address indexed tokenAddress, string name, string symbol, address indexed creator);
    event TokenBought(address indexed tokenAddress, address indexed buyer, uint256 ethAmount, uint256 tokenAmount);
    event TokenSold(address indexed tokenAddress, address indexed seller, uint256 tokenAmount, uint256 ethAmount);

    constructor(address payable _feeRecipient) {
        feeRecipient = _feeRecipient;
    }

    function deployMemeToken(string memory name, string memory symbol, uint256 supply) public payable returns (address) {
        require(msg.value >= deployFee, "Insufficient deployment fee");
        require(supply >= 1000_000, "Supply too low");
        
        // Collect deployment fee
        feeRecipient.transfer(deployFee);

        // Deploy new MemeToken contract
        // Mint entire supply to factory first to manage bonding curve
        MemeToken newToken = new MemeToken(name, symbol, supply * 10**18, address(this));
        address tokenAddr = address(newToken);
        
        allMemeTokens.push(tokenAddr);

        // Setup Virtual constant product pool (x * y = k)
        pools[tokenAddr] = TokenPool({
            tokenAddress: tokenAddr,
            tokenReserves: INITIAL_TOKEN_RESERVE,
            ethReserves: VIRTUAL_ETH_RESERVE,
            tradingActive: true
        });

        // Send remaining 200 Million (or excess supply) tokens to creator
        uint256 excessSupply = (supply * 10**18) - INITIAL_TOKEN_RESERVE;
        if (excessSupply > 0) {
            newToken.transfer(msg.sender, excessSupply);
        }

        emit MemeDeployed(tokenAddr, name, symbol, msg.sender);
        return tokenAddr;
    }

    function buyMemeToken(address tokenAddress) public payable {
        TokenPool storage pool = pools[tokenAddress];
        require(pool.tradingActive, "Trading is not active");
        require(msg.value > 0, "Must send ETH");

        uint256 ethInput = msg.value;
        uint256 k = pool.tokenReserves * pool.ethReserves;
        
        uint256 newEthReserves = pool.ethReserves + ethInput;
        uint256 newDecimalTokens = k / newEthReserves;
        uint256 tokensToOutput = pool.tokenReserves - newDecimalTokens;

        require(tokensToOutput > 0, "Insufficient output amount");
        require(tokensToOutput <= pool.tokenReserves, "Not enough tokens in curve");

        pool.ethReserves = newEthReserves;
        pool.tokenReserves = newDecimalTokens;

        // Transfer tokens from factory to buyer
        MemeToken(tokenAddress).transfer(msg.sender, tokensToOutput);

        emit TokenBought(tokenAddress, msg.sender, ethInput, tokensToOutput);
    }

    function sellMemeToken(address tokenAddress, uint256 tokenAmount) public {
        TokenPool storage pool = pools[tokenAddress];
        require(pool.tradingActive, "Trading is not active");
        require(tokenAmount > 0, "Must sell positive amount");

        // User must approve the factory first or we use factoryTransfer
        uint256 k = pool.tokenReserves * pool.ethReserves;
        
        uint256 newTokenReserves = pool.tokenReserves + tokenAmount;
        uint256 newEthReserves = k / newTokenReserves;
        uint256 ethToOutput = pool.ethReserves - newEthReserves;

        require(ethToOutput > 0, "Insufficient ETH output");
        require(ethToOutput <= address(this).balance, "Contract balance low");

        pool.tokenReserves = newTokenReserves;
        pool.ethReserves = newEthReserves;

        // Pull tokens from user to factory
        MemeToken(tokenAddress).factoryTransfer(msg.sender, address(this), tokenAmount);
        
        // Send ETH back to user
        payable(msg.sender).transfer(ethToOutput);

        emit TokenSold(tokenAddress, msg.sender, tokenAmount, ethToOutput);
    }

    function getMemeCount() public view returns (uint256) {
        return allMemeTokens.length;
    }
}
