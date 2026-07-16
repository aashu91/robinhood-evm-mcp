// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

contract CommunityTrust {
    string public name;
    address public creator;
    
    address[] public directors;
    mapping(address => bool) public isDirector;
    uint256 public requiredSignatures;

    uint256 public totalShares;
    mapping(address => uint256) public shares;

    struct Proposal {
        address destination;
        uint256 value;
        bytes data;
        bool executed;
        uint256 signatureCount;
    }

    Proposal[] public proposals;
    // proposalId => director => hasSigned
    mapping(uint256 => mapping(address => bool)) public proposalSignatures;

    // Dividend tracking
    mapping(address => uint256) public totalDividendPoints; // tokenAddress => points
    mapping(address => mapping(address => uint256)) public lastDividendPoints; // tokenAddress => user => points
    mapping(address => mapping(address => uint256)) public accumulatedDividends; // tokenAddress => user => dividends

    uint256 constant POINT_MULTIPLIER = 1e18;

    event Deposited(address indexed user, uint256 amount);
    event ProposalCreated(uint256 indexed proposalId, address indexed destination, uint256 value, bytes data);
    event ProposalSigned(uint256 indexed proposalId, address indexed director);
    event ProposalExecuted(uint256 indexed proposalId);
    event DividendDistributed(address indexed token, uint256 amount);
    event DividendClaimed(address indexed user, address indexed token, uint256 amount);
    event DirectorAppointed(address indexed director);

    modifier onlyDirector() {
        require(isDirector[msg.sender], "Not a director");
        _;
    }

    constructor(
        string memory _name,
        address _creator,
        address[] memory _directors,
        uint256 _requiredSignatures
    ) {
        require(_directors.length > 0, "Directors required");
        require(_requiredSignatures > 0 && _requiredSignatures <= _directors.length, "Invalid signature threshold");
        name = _name;
        creator = _creator;
        requiredSignatures = _requiredSignatures;

        for (uint256 i = 0; i < _directors.length; i++) {
            address dir = _directors[i];
            require(dir != address(0), "Invalid director address");
            require(!isDirector[dir], "Duplicate director");
            isDirector[dir] = true;
            directors.push(dir);
            emit DirectorAppointed(dir);
        }
    }

    function deposit() external payable {
        require(msg.value > 0, "Must deposit positive amount");
        
        _updateUserDividends(msg.sender, address(0)); // Update native ETH dividends

        shares[msg.sender] += msg.value;
        totalShares += msg.value;

        emit Deposited(msg.sender, msg.value);
    }

    function proposeTransaction(
        address destination,
        uint256 value,
        bytes memory data
    ) external onlyDirector returns (uint256) {
        uint256 proposalId = proposals.length;
        proposals.push(Proposal({
            destination: destination,
            value: value,
            data: data,
            executed: false,
            signatureCount: 0
        }));

        emit ProposalCreated(proposalId, destination, value, data);
        
        signTransaction(proposalId);
        
        return proposalId;
    }

    function signTransaction(uint256 proposalId) public onlyDirector {
        require(proposalId < proposals.length, "Proposal does not exist");
        Proposal storage prop = proposals[proposalId];
        require(!prop.executed, "Proposal already executed");
        require(!proposalSignatures[proposalId][msg.sender], "Already signed");

        proposalSignatures[proposalId][msg.sender] = true;
        prop.signatureCount += 1;

        emit ProposalSigned(proposalId, msg.sender);
    }

    function executeTransaction(uint256 proposalId) external onlyDirector {
        require(proposalId < proposals.length, "Proposal does not exist");
        Proposal storage prop = proposals[proposalId];
        require(!prop.executed, "Proposal already executed");
        require(prop.signatureCount >= requiredSignatures, "Not enough signatures");

        prop.executed = true;
        (bool success, ) = prop.destination.call{value: prop.value}(prop.data);
        require(success, "Transaction execution failed");

        emit ProposalExecuted(proposalId);
    }

    function distributeDividends(address tokenAddress, uint256 amount) external payable {
        require(totalShares > 0, "No depositors to receive dividends");
        
        if (tokenAddress == address(0)) {
            require(msg.value == amount, "ETH amount mismatch");
            totalDividendPoints[address(0)] += (amount * POINT_MULTIPLIER) / totalShares;
            emit DividendDistributed(address(0), amount);
        } else {
            require(IERC20(tokenAddress).transferFrom(msg.sender, address(this), amount), "Transfer failed");
            totalDividendPoints[tokenAddress] += (amount * POINT_MULTIPLIER) / totalShares;
            emit DividendDistributed(tokenAddress, amount);
        }
    }

    function _updateUserDividends(address user, address token) internal {
        uint256 userShares = shares[user];
        if (userShares > 0) {
            uint256 points = totalDividendPoints[token];
            uint256 pending = (userShares * (points - lastDividendPoints[token][user])) / POINT_MULTIPLIER;
            accumulatedDividends[token][user] += pending;
        }
        lastDividendPoints[token][user] = totalDividendPoints[token];
    }

    function claimDividends(address token) external {
        _updateUserDividends(msg.sender, token);
        uint256 reward = accumulatedDividends[token][msg.sender];
        require(reward > 0, "No dividends to claim");

        accumulatedDividends[token][msg.sender] = 0;
        
        if (token == address(0)) {
            payable(msg.sender).transfer(reward);
        } else {
            require(IERC20(token).transfer(msg.sender, reward), "Transfer failed");
        }

        emit DividendClaimed(msg.sender, token, reward);
    }

    function getDirectors() external view returns (address[] memory) {
        return directors;
    }

    receive() external payable {}
}

contract CommunityTrustFactory {
    address[] public allTrusts;
    mapping(address => bool) public isTrust;

    event TrustCreated(address indexed trustAddress, string name, address indexed creator);

    function createTrust(
        string memory name,
        address[] memory directors,
        uint256 requiredSignatures
    ) external returns (address) {
        CommunityTrust newTrust = new CommunityTrust(name, msg.sender, directors, requiredSignatures);
        address trustAddr = address(newTrust);
        allTrusts.push(trustAddr);
        isTrust[trustAddr] = true;

        emit TrustCreated(trustAddr, name, msg.sender);
        return trustAddr;
    }

    function getTrustCount() external view returns (uint256) {
        return allTrusts.length;
    }
}
