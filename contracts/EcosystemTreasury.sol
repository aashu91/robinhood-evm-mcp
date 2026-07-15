// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IMemeFactory {
    function buyMemeToken(address tokenAddress, address referrer) external payable;
}

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
}

contract EcosystemTreasury {
    address public owner;
    address payable public creatorAddress;
    address payable public stakingYieldAddress;
    
    uint256 public devPoolBalance;
    
    event FeesDistributed(uint256 creatorShare, uint256 stakingShare, uint256 devShare);
    event DevPaid(address indexed developer, address indexed tokenAddress, uint256 ethSpent, uint256 tokensReceived);
    event AddressesUpdated(address creator, address staking);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can execute");
        _;
    }

    constructor(address payable _creatorAddress, address payable _stakingYieldAddress) {
        owner = msg.sender;
        creatorAddress = _creatorAddress;
        stakingYieldAddress = _stakingYieldAddress;
    }

    function setAddresses(address payable _creatorAddress, address payable _stakingYieldAddress) external onlyOwner {
        creatorAddress = _creatorAddress;
        stakingYieldAddress = _stakingYieldAddress;
        emit AddressesUpdated(_creatorAddress, _stakingYieldAddress);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid owner address");
        owner = newOwner;
    }

    // fallback to receive ETH fee splits from MemeFactory
    receive() external payable {
        uint256 amount = msg.value;
        if (amount > 0) {
            uint256 creatorShare = (amount * 40) / 100;
            uint256 stakingShare = (amount * 40) / 100;
            uint256 devShare = amount - creatorShare - stakingShare;

            devPoolBalance += devShare;

            // Route creator and staking shares immediately
            if (creatorAddress != address(0)) {
                creatorAddress.transfer(creatorShare);
            } else {
                devPoolBalance += creatorShare; // fallback if address not set
            }

            if (stakingYieldAddress != address(0)) {
                stakingYieldAddress.transfer(stakingShare);
            } else {
                devPoolBalance += stakingShare; // fallback if address not set
            }

            emit FeesDistributed(creatorShare, stakingShare, devShare);
        }
    }

    // Buyback native tokens using Dev pool ETH and transfer them to the developer
    function payoutDeveloperToken(
        address factoryAddress, 
        address tokenAddress, 
        address payable developer, 
        uint256 ethAmount
    ) external onlyOwner {
        require(ethAmount <= devPoolBalance, "Insufficient developer pool balance");
        require(developer != address(0), "Invalid developer address");

        devPoolBalance -= ethAmount;

        // Fetch initial token balance of treasury
        uint256 initialBalance = IERC20(tokenAddress).balanceOf(address(this));

        // Call buyMemeToken on MemeFactory using Dev Pool ETH (passing address(0) as referrer)
        IMemeFactory(factoryAddress).buyMemeToken{value: ethAmount}(tokenAddress, address(0));

        // Calculate purchased token quantity
        uint256 finalBalance = IERC20(tokenAddress).balanceOf(address(this));
        uint256 purchasedAmount = finalBalance - initialBalance;
        require(purchasedAmount > 0, "No tokens purchased");

        // Transfer tokens to the developer
        require(IERC20(tokenAddress).transfer(developer, purchasedAmount), "Token transfer failed");

        emit DevPaid(developer, tokenAddress, ethAmount, purchasedAmount);
    }
    
    // Emergency withdraw logic
    function emergencyWithdrawEth() external onlyOwner {
        uint256 balance = address(this).balance;
        payable(owner).transfer(balance);
        devPoolBalance = 0;
    }
}
