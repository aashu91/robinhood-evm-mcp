// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function transfer(address to, uint256 value) external returns (bool);
}

contract StakingYield {
    IERC20 public immutable stakingToken;

    uint256 public totalStaked;
    mapping(address => uint256) public stakedBalance;

    // Proportional reward distribution index
    uint256 public rewardIndex;
    mapping(address => uint256) public userRewardIndex;
    mapping(address => uint256) public accumulatedRewards;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 reward);
    event RewardDeposited(uint256 amount);

    constructor(address _stakingToken) {
        stakingToken = IERC20(_stakingToken);
    }

    // Receive reward ETH from EcosystemTreasury and update the rewardIndex
    receive() external payable {
        uint256 amount = msg.value;
        if (amount > 0 && totalStaked > 0) {
            // Scale factor 1e18 to prevent division rounding loss
            rewardIndex += (amount * 1e18) / totalStaked;
            emit RewardDeposited(amount);
        }
    }

    // Update index before stake balance changes
    function _updateUserReward(address account) internal {
        if (stakedBalance[account] > 0) {
            uint256 pending = (stakedBalance[account] * (rewardIndex - userRewardIndex[account])) / 1e18;
            accumulatedRewards[account] += pending;
        }
        userRewardIndex[account] = rewardIndex;
    }

    function stake(uint256 amount) external {
        require(amount > 0, "Cannot stake 0");
        _updateUserReward(msg.sender);

        totalStaked += amount;
        stakedBalance[msg.sender] += amount;

        require(stakingToken.transferFrom(msg.sender, address(this), amount), "Stake transfer failed");
        emit Staked(msg.sender, amount);
    }

    function unstake(uint256 amount) external {
        require(amount > 0, "Cannot unstake 0");
        require(stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        _updateUserReward(msg.sender);

        totalStaked -= amount;
        stakedBalance[msg.sender] -= amount;

        require(stakingToken.transfer(msg.sender, amount), "Unstake transfer failed");
        emit Unstaked(msg.sender, amount);
    }

    function claimReward() external {
        _updateUserReward(msg.sender);
        uint256 reward = accumulatedRewards[msg.sender];
        require(reward > 0, "No reward to claim");

        accumulatedRewards[msg.sender] = 0;
        payable(msg.sender).transfer(reward);

        emit RewardClaimed(msg.sender, reward);
    }
}
