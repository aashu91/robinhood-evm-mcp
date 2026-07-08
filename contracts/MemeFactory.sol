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
    address payable public feeRecipient;
    uint256 public deployFee = 0.005 ether; // Fee sent to recipient on every deploy
    address[] public allMemeTokens;

    event MemeDeployed(address indexed tokenAddress, string name, string symbol, address indexed creator);

    constructor(address payable _feeRecipient) {
        feeRecipient = _feeRecipient;
    }

    function deployMemeToken(string memory name, string memory symbol, uint256 supply) public payable returns (address) {
        require(msg.value >= deployFee, "Insufficient deployment fee");
        
        // Transfer fee to the developer wallet
        feeRecipient.transfer(msg.value);

        // Deploy new MemeToken contract
        MemeToken newToken = new MemeToken(name, symbol, supply, msg.sender);
        address tokenAddr = address(newToken);
        allMemeTokens.push(tokenAddr);

        emit MemeDeployed(tokenAddr, name, symbol, msg.sender);
        return tokenAddr;
    }

    function getMemeCount() public view returns (uint256) {
        return allMemeTokens.length;
    }
}
