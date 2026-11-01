// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

/**
 * @title StakingYield
 * @notice Proportional staking & yield distribution contract for $ROBIN_MCP (0xCFD635f82B75ab6c1a6725a54e9146FEe2c5A421)
 */
contract StakingYield {
    IERC20 public immutable stakingToken;
    uint256 public totalStaked;
    uint256 public rewardPerTokenStored;
    uint256 public lastUpdateTime;
    uint256 public rewardRate;

    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 reward);
    event EmergencyUnstaked(address indexed user, uint256 amount);

    constructor(address _stakingToken, uint256 _initialRewardRate) {
        stakingToken = IERC20(_stakingToken);
        rewardRate = _initialRewardRate;
        lastUpdateTime = block.timestamp;
    }

    modifier updateReward(address account) {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;
        if (account != address(0)) {
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = rewardPerTokenStored;
        }
        _;
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (((block.timestamp - lastUpdateTime) * rewardRate * 1e18) / totalStaked);
    }

    function earned(address account) public view returns (uint256) {
        return ((stakedBalance[account] * (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18) + rewards[account];
    }

    function stake(uint256 amount) external updateReward(msg.sender) {
        require(amount > 0, "Cannot stake 0");
        totalStaked += amount;
        stakedBalance[msg.sender] += amount;
        require(stakingToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        emit Staked(msg.sender, amount);
    }

    function unstake(uint256 amount) external updateReward(msg.sender) {
        require(amount > 0 && stakedBalance[msg.sender] >= amount, "Insufficient staked balance");
        totalStaked -= amount;
        stakedBalance[msg.sender] -= amount;
        require(stakingToken.transfer(msg.sender, amount), "Transfer failed");
        emit Unstaked(msg.sender, amount);
    }

    function claimRewards() external updateReward(msg.sender) {
        uint256 reward = rewards[msg.sender];
        require(reward > 0, "No rewards to claim");
        rewards[msg.sender] = 0;
        require(stakingToken.transfer(msg.sender, reward), "Reward transfer failed");
        emit RewardsClaimed(msg.sender, reward);
    }

    function emergencyUnstake() external {
        uint256 amount = stakedBalance[msg.sender];
        require(amount > 0, "Nothing staked");
        totalStaked -= amount;
        stakedBalance[msg.sender] = 0;
        rewards[msg.sender] = 0;
        require(stakingToken.transfer(msg.sender, amount), "Emergency transfer failed");
        emit EmergencyUnstaked(msg.sender, amount);
    }
}
