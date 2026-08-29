// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 value) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 value) external returns (bool);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract StakingYield {
    IERC20 public immutable stakingToken;

    uint256 public totalStaked;
    mapping(address => uint256) public stakedBalance;

    // Proportional reward distribution index (scaled by 1e18)
    uint256 public rewardIndex;
    mapping(address => uint256) public userRewardIndex;
    mapping(address => uint256) public accumulatedRewards;

    // Track total historical rewards deposited and claimed
    uint256 public totalRewardsDeposited;
    uint256 public totalRewardsClaimed;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 reward);
    event RewardDeposited(address indexed sender, uint256 amount);
    event EmergencyUnstaked(address indexed user, uint256 amount);

    constructor(address _stakingToken) {
        require(_stakingToken != address(0), "Invalid staking token address");
        stakingToken = IERC20(_stakingToken);
    }

    // Receive reward ETH from EcosystemTreasury or external sources and update the rewardIndex
    receive() external payable {
        depositRewards();
    }

    function depositRewards() public payable {
        uint256 amount = msg.value;
        if (amount > 0) {
            totalRewardsDeposited += amount;
            if (totalStaked > 0) {
                // Scale factor 1e18 to prevent division rounding loss
                rewardIndex += (amount * 1e18) / totalStaked;
            }
            emit RewardDeposited(msg.sender, amount);
        }
    }

    // View helper to calculate pending rewards for an account
    function getPendingReward(address account) public view returns (uint256) {
        uint256 pending = 0;
        if (stakedBalance[account] > 0 && rewardIndex > userRewardIndex[account]) {
            pending = (stakedBalance[account] * (rewardIndex - userRewardIndex[account])) / 1e18;
        }
        return accumulatedRewards[account] + pending;
    }

    // Full staking info helper
    function getStakingInfo(address account) external view returns (
        uint256 userStaked,
        uint256 userPendingReward,
        uint256 poolTotalStaked,
        uint256 totalPoolRewards
    ) {
        return (
            stakedBalance[account],
            getPendingReward(account),
            totalStaked,
            totalRewardsDeposited
        );
    }

    // Update index before stake balance changes
    function _updateUserReward(address account) internal {
        accumulatedRewards[account] = getPendingReward(account);
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

    function claimRewards() public {
        _updateUserReward(msg.sender);
        uint256 reward = accumulatedRewards[msg.sender];
        require(reward > 0, "No reward to claim");

        accumulatedRewards[msg.sender] = 0;
        totalRewardsClaimed += reward;

        (bool success, ) = payable(msg.sender).call{value: reward}("");
        require(success, "Reward transfer failed");

        emit RewardClaimed(msg.sender, reward);
    }

    // Alias for claimRewards()
    function claimReward() external {
        claimRewards();
    }

    // Emergency unstake: allows staker to withdraw full deposited principal without claiming rewards
    function emergencyUnstake() external {
        uint256 amount = stakedBalance[msg.sender];
        require(amount > 0, "No staked balance");

        totalStaked -= amount;
        stakedBalance[msg.sender] = 0;
        accumulatedRewards[msg.sender] = 0;
        userRewardIndex[msg.sender] = rewardIndex;

        require(stakingToken.transfer(msg.sender, amount), "Emergency unstake transfer failed");
        emit EmergencyUnstaked(msg.sender, amount);
    }
}
