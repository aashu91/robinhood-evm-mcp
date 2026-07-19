// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title StakingYield
 * @dev Native Token Staking Contract with Oracle-based Yield Calculation
 * @author Robinhood Chain EVM MCP Server
 */
contract StakingYield {
    // ========== State Variables ==========

    address public owner;
    uint256 public totalStaked;
    uint256 public totalRewards;
    uint256 public lastRewardUpdateTime;
    uint256 public rewardRate = 100; // 1% daily reward rate (100 = 1%)
    uint256 public constant DURATION = 1 days;

    mapping(address => uint256) public userStakedAmount;
    mapping(address => uint256) public userRewardDebt;
    mapping(address => bool) public isStaked;

    // Oracle addresses
    address public pythOracle;
    address public chainlinkOracle;

    // Ticker symbols for price feeds
    string public constant GOLD_TICKER = "GOLD";
    string public constant SILVER_TICKER = "SILVER";

    // Events
    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);
    event RewardRateUpdated(uint256 newRate);
    event OracleAddressesUpdated(address pythOracle, address chainlinkOracle);

    // ========== Modifiers ==========

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyStaked() {
        require(isStaked[msg.sender], "Not staked");
        _;
    }

    // ========== Constructor ==========

    constructor(
        address _pythOracle,
        address _chainlinkOracle
    ) {
        owner = msg.sender;
        pythOracle = _pythOracle;
        chainlinkOracle = _chainlinkOracle;
        lastRewardUpdateTime = block.timestamp;
    }

    // ========== External Functions ==========

    /**
     * @dev Stake native tokens (ETH/USDG)
     * @param amount Amount of tokens to stake
     */
    function stake(uint256 amount) external payable {
        require(amount > 0, "Amount must be > 0");

        // Update reward debt before staking
        _updateRewardDebt(msg.sender);

        // Update state
        userStakedAmount[msg.sender] += amount;
        totalStaked += amount;

        isStaked[msg.sender] = true;

        emit Staked(msg.sender, amount);
    }

    /**
     * @dev Unstake tokens and claim rewards
     * @param amount Amount of tokens to unstake
     */
    function unstake(uint256 amount) external onlyStaked {
        require(amount > 0, "Amount must be > 0");
        require(userStakedAmount[msg.sender] >= amount, "Insufficient staked amount");

        // Update reward debt before unstaking
        _updateRewardDebt(msg.sender);

        // Calculate rewards to claim
        uint256 pendingRewards = _calculatePendingRewards(msg.sender);

        // Update state
        userStakedAmount[msg.sender] -= amount;
        totalStaked -= amount;

        // Transfer tokens
        payable(msg.sender).transfer(amount + pendingRewards);

        emit Unstaked(msg.sender, amount);
        emit RewardsClaimed(msg.sender, pendingRewards);
    }

    /**
     * @dev Claim rewards without unstaking
     */
    function claimRewards() external onlyStaked {
        // Update reward debt
        _updateRewardDebt(msg.sender);

        // Calculate pending rewards
        uint256 pendingRewards = _calculatePendingRewards(msg.sender);

        require(pendingRewards > 0, "No pending rewards");

        // Update state
        totalRewards += pendingRewards;

        // Transfer rewards
        payable(msg.sender).transfer(pendingRewards);

        emit RewardsClaimed(msg.sender, pendingRewards);
    }

    /**
     * @dev Get current price from Pyth Network
     */
    function getGoldPrice() external view returns (uint256 price) {
        // TODO: Call Pyth Oracle contract
        return 2000 * 10**18; // Default: $2000/oz
    }

    /**
     * @dev Get current price from Chainlink Oracle
     */
    function getSilverPrice() external view returns (uint256 price) {
        // TODO: Call Chainlink Oracle contract
        return 25 * 10**18; // Default: $25/oz
    }

    /**
     * @dev Calculate reward for a user
     * @param user Address of the user
     * @return reward Amount of rewards
     */
    function calculateReward(address user) external view returns (uint256 reward) {
        return _calculatePendingRewards(user);
    }

    /**
     * @dev Get user staking information
     * @param user Address of the user
     * @return stakedAmount Amount staked
     * @return pendingRewards Pending rewards
     */
    function getUserStakingInfo(address user) external view returns (
        uint256 stakedAmount,
        uint256 pendingRewards
    ) {
        stakedAmount = userStakedAmount[user];
        pendingRewards = _calculatePendingRewards(user);
    }

    // ========== Internal Functions ==========

    /**
     * @dev Update reward debt for a user
     */
    function _updateRewardDebt(address user) internal {
        uint256 userAmount = userStakedAmount[user];
        userRewardDebt[user] = userAmount * rewardRate / 100;
    }

    /**
     * @dev Calculate pending rewards for a user
     * @param user Address of the user
     * @return pendingRewards Pending rewards
     */
    function _calculatePendingRewards(address user) internal view returns (uint256 pendingRewards) {
        uint256 userAmount = userStakedAmount[user];
        if (userAmount == 0) {
            return 0;
        }

        uint256 currentRewardDebt = userAmount * rewardRate / 100;
        pendingRewards = currentRewardDebt - userRewardDebt[user];
    }

    /**
     * @dev Update reward rate (only owner)
     * @param newRate New reward rate (100 = 1%)
     */
    function updateRewardRate(uint256 newRate) external onlyOwner {
        require(newRate <= 100, "Reward rate cannot exceed 100%");
        rewardRate = newRate;
        emit RewardRateUpdated(newRate);
    }

    /**
     * @dev Update oracle addresses (only owner)
     * @param _pythOracle New Pyth Oracle address
     * @param _chainlinkOracle New Chainlink Oracle address
     */
    function updateOracleAddresses(
        address _pythOracle,
        address _chainlinkOracle
    ) external onlyOwner {
        pythOracle = _pythOracle;
        chainlinkOracle = _chainlinkOracle;
        emit OracleAddressesUpdated(_pythOracle, _chainlinkOracle);
    }

    /**
     * @dev Withdraw all tokens (emergency only)
     */
    function emergencyWithdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    /**
     * @dev Get contract balance
     */
    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }

    /**
     * @dev Get total rewards distributed
     */
    function getTotalRewards() external view returns (uint256) {
        return totalRewards;
    }

    /**
     * @dev Get reward rate
     */
    function getRewardRate() external view returns (uint256) {
        return rewardRate;
    }

    /**
     * @dev Get user reward debt
     */
    function getUserRewardDebt(address user) external view returns (uint256) {
        return userRewardDebt[user];
    }

    // ========== Fallback Function ==========

    receive() external payable {}
}
