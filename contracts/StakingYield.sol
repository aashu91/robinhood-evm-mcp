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

/**
 * @title StakingYield
 * @notice Proportional staking and yield distribution contract for $ROBIN_MCP.
 */
contract StakingYield {
    IERC20 public immutable stakingToken;
    uint256 public totalStaked;
    mapping(address => uint256) public stakedBalance;

    uint256 public rewardIndex;
    mapping(address => uint256) public userRewardIndex;
    mapping(address => uint256) public accumulatedRewards;

    uint256 public totalRewardsDeposited;
    uint256 public totalRewardsClaimed;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 reward);
    event RewardsClaimed(address indexed user, uint256 reward);
    event RewardDeposited(address indexed sender, uint256 amount);
    event EmergencyUnstaked(address indexed user, uint256 amount);

    /**
     * @notice Initializes the staking contract with the target ERC20 token address.
     * @param _stakingToken Address of the ERC20 token eligible for staking.
     */
    constructor(address _stakingToken) {
        require(_stakingToken != address(0), "Invalid staking token address");
        stakingToken = IERC20(_stakingToken);
    }

    /**
     * @notice Fallback function to accept platform fees from EcosystemTreasury or external sources.
     */
    receive() external payable {
        depositRewards();
    }

    /**
     * @notice Ingests platform fees into the proportional reward index.
     */
    function depositRewards() public payable {
        uint256 amount = msg.value;
        if (amount > 0) {
            totalRewardsDeposited += amount;
            if (totalStaked > 0) {
                rewardIndex += (amount * 1e18) / totalStaked;
            }
            emit RewardDeposited(msg.sender, amount);
        }
    }

    /**
     * @notice Calculates the total pending yield rewards for a given account.
     * @param account Address of the staker to query.
     * @return Total unclaimed reward amount in Wei.
     */
    function getPendingReward(address account) public view returns (uint256) {
        uint256 pending = 0;
        if (stakedBalance[account] > 0 && rewardIndex > userRewardIndex[account]) {
            pending = (stakedBalance[account] * (rewardIndex - userRewardIndex[account])) / 1e18;
        }
        return accumulatedRewards[account] + pending;
    }

    /**
     * @notice Alias for getPendingReward to support standard staking interface.
     * @param account Address of the staker.
     * @return Total earned rewards in Wei.
     */
    function earned(address account) external view returns (uint256) {
        return getPendingReward(account);
    }

    /**
     * @notice Provides aggregated statistics for the pool and specific user account.
     * @param account Address of the user to query.
     * @return userStaked Amount of tokens staked by the user.
     * @return userPendingReward Pending ETH reward available for claim.
     * @return poolTotalStaked Aggregate staked token balance across all users.
     * @return totalPoolRewards Cumulative platform fees deposited into pool.
     */
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

    /**
     * @notice Synchronizes accumulated yield before any stake balance mutation.
     * @param account Address of the user undergoing state change.
     */
    function _updateUserReward(address account) internal {
        accumulatedRewards[account] = getPendingReward(account);
        userRewardIndex[account] = rewardIndex;
    }

    /**
     * @notice Stakes a specified amount of tokens into the yield pool.
     * @param amount Token amount to deposit.
     */
    function stake(uint256 amount) external {
        require(amount > 0, "Cannot stake 0");
        _updateUserReward(msg.sender);

        totalStaked += amount;
        stakedBalance[msg.sender] += amount;

        require(stakingToken.transferFrom(msg.sender, address(this), amount), "Stake transfer failed");
        emit Staked(msg.sender, amount);
    }

    /**
     * @notice Unstakes a specified amount of tokens from the yield pool.
     * @param amount Token amount to withdraw.
     */
    function unstake(uint256 amount) external {
        require(amount > 0, "Cannot unstake 0");
        require(stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        _updateUserReward(msg.sender);

        totalStaked -= amount;
        stakedBalance[msg.sender] -= amount;

        require(stakingToken.transfer(msg.sender, amount), "Unstake transfer failed");
        emit Unstaked(msg.sender, amount);
    }

    /**
     * @notice Claims accumulated yield rewards and transfers them to the caller.
     */
    function claimRewards() public {
        _updateUserReward(msg.sender);
        uint256 reward = accumulatedRewards[msg.sender];
        require(reward > 0, "No reward to claim");

        accumulatedRewards[msg.sender] = 0;
        totalRewardsClaimed += reward;

        (bool success, ) = payable(msg.sender).call{value: reward}("");
        require(success, "Reward transfer failed");

        emit RewardClaimed(msg.sender, reward);
        emit RewardsClaimed(msg.sender, reward);
    }

    /**
     * @notice Alias for claimRewards to satisfy multiple calling conventions.
     */
    function claimReward() external {
        claimRewards();
    }

    /**
     * @notice Emergency withdrawal of principal tokens without calculating or claiming rewards.
     */
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
