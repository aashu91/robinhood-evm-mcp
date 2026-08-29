// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function transfer(address to, uint256 value) external returns (bool);
}

/**
 * @title StakingYield
 * @notice Native token ($ROBIN_MCP) staking and real-time yield distribution contract.
 * @dev Distributes ETH platform fees proportionally to stakers based on their pool share over time.
 */
contract StakingYield {
    IERC20 public immutable stakingToken;

    uint256 public totalStaked;
    mapping(address => uint256) public stakedBalance;

    // Proportional reward distribution index (scaled by 1e18)
    uint256 public rewardIndex;
    mapping(address => uint256) public userRewardIndex;
    mapping(address => uint256) public accumulatedRewards;

    // Reentrancy guard
    uint8 private _unlocked = 1;
    modifier nonReentrant() {
        require(_unlocked == 1, "Reentrant call");
        _unlocked = 0;
        _;
        _unlocked = 1;
    }

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event EmergencyUnstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 reward);
    event RewardDeposited(address indexed sender, uint256 amount, uint256 newRewardIndex);

    constructor(address _stakingToken) {
        require(_stakingToken != address(0), "Invalid staking token address");
        stakingToken = IERC20(_stakingToken);
    }

    // Receive reward ETH directly (e.g. from EcosystemTreasury fee split)
    receive() external payable {
        _depositReward(msg.value);
    }

    // Explicit method to fund reward pool with ETH
    function depositReward() external payable {
        require(msg.value > 0, "Must deposit ETH");
        _depositReward(msg.value);
    }

    function fundRewards() external payable {
        require(msg.value > 0, "Must deposit ETH");
        _depositReward(msg.value);
    }

    function _depositReward(uint256 amount) internal {
        if (amount > 0) {
            if (totalStaked > 0) {
                rewardIndex += (amount * 1e18) / totalStaked;
            }
            emit RewardDeposited(msg.sender, amount, rewardIndex);
        }
    }

    // Calculate earned/pending rewards for an account
    function earned(address account) public view returns (uint256) {
        uint256 pending = 0;
        if (stakedBalance[account] > 0) {
            pending = (stakedBalance[account] * (rewardIndex - userRewardIndex[account])) / 1e18;
        }
        return accumulatedRewards[account] + pending;
    }

    function getPendingReward(address account) external view returns (uint256) {
        return earned(account);
    }

    // Aggregated view for querying full staking profile in a single RPC call
    function getStakingInfo(address account) external view returns (
        uint256 _totalStaked,
        uint256 _userStaked,
        uint256 _pendingReward,
        uint256 _rewardIndex,
        address _stakingToken
    ) {
        return (
            totalStaked,
            stakedBalance[account],
            earned(account),
            rewardIndex,
            address(stakingToken)
        );
    }

    // Internal hook to update user rewards before balance changes
    function _updateUserReward(address account) internal {
        if (stakedBalance[account] > 0) {
            uint256 pending = (stakedBalance[account] * (rewardIndex - userRewardIndex[account])) / 1e18;
            accumulatedRewards[account] += pending;
        }
        userRewardIndex[account] = rewardIndex;
    }

    /**
     * @notice Stakes native $ROBIN_MCP tokens to earn proportional ETH yield.
     * @param amount The token amount to stake (in 18-decimal wei).
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake 0");
        _updateUserReward(msg.sender);

        totalStaked += amount;
        stakedBalance[msg.sender] += amount;

        require(stakingToken.transferFrom(msg.sender, address(this), amount), "Stake transfer failed");
        emit Staked(msg.sender, amount);
    }

    /**
     * @notice Unstakes staked tokens and updates reward accrual.
     * @param amount The token amount to unstake (in 18-decimal wei).
     */
    function unstake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot unstake 0");
        require(stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        _updateUserReward(msg.sender);

        totalStaked -= amount;
        stakedBalance[msg.sender] -= amount;

        require(stakingToken.transfer(msg.sender, amount), "Unstake transfer failed");
        emit Unstaked(msg.sender, amount);
    }

    /**
     * @notice Emergency unstake function allowing stakers to withdraw their principal instantly.
     */
    function emergencyUnstake() external nonReentrant {
        uint256 amount = stakedBalance[msg.sender];
        require(amount > 0, "No staked balance");

        totalStaked -= amount;
        stakedBalance[msg.sender] = 0;
        userRewardIndex[msg.sender] = rewardIndex;

        require(stakingToken.transfer(msg.sender, amount), "Emergency unstake transfer failed");
        emit EmergencyUnstaked(msg.sender, amount);
    }

    /**
     * @notice Claims all accumulated ETH rewards for caller.
     */
    function claimReward() public nonReentrant {
        _updateUserReward(msg.sender);
        uint256 reward = accumulatedRewards[msg.sender];
        require(reward > 0, "No reward to claim");

        accumulatedRewards[msg.sender] = 0;
        (bool success, ) = payable(msg.sender).call{value: reward}("");
        require(success, "Reward transfer failed");

        emit RewardClaimed(msg.sender, reward);
    }

    /**
     * @notice Alias for claimReward().
     */
    function claimRewards() external {
        claimReward();
    }
}
