// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract StakingYield is Ownable {
    IERC20 public token;
    uint256 public totalStaked;
    mapping(address => uint256) public stakedAmounts;
    mapping(address => uint256) public rewardDebt;
    uint256 public accTokenPerShare;
    uint256 public lastRewardBlock;
    uint256 public rewardRate = 1 ether; // 1 token per block

    event Staked(address indexed user, uint256 amount);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);

    constructor(IERC20 _token) {
        token = _token;
        lastRewardBlock = block.number;
    }

    function stake(uint256 _amount) external {
        require(_amount > 0, "Amount must be greater than 0");
        _updatePool();
        _stake(msg.sender, _amount);
        emit Staked(msg.sender, _amount);
    }

    function unstake(uint256 _amount) external {
        require(_amount > 0, "Amount must be greater than 0");
        _updatePool();
        _unstake(msg.sender, _amount);
        emit Unstaked(msg.sender, _amount);
    }

    function claimRewards() external {
        _updatePool();
        uint256 pending = _pendingRewards(msg.sender);
        if (pending > 0) {
            _claim(msg.sender, pending);
            emit RewardClaimed(msg.sender, pending);
        }
    }

    function _stake(address _user, uint256 _amount) internal {
        stakedAmounts[_user] += _amount;
        totalStaked += _amount;
        token.transferFrom(_user, address(this), _amount);
        rewardDebt[_user] = _userPendingRewards(_user);
    }

    function _unstake(address _user, uint256 _amount) internal {
        require(stakedAmounts[_user] >= _amount, "Insufficient staked amount");
        stakedAmounts[_user] -= _amount;
        totalStaked -= _amount;
        token.transfer(_user, _amount);
        rewardDebt[_user] = _userPendingRewards(_user);
    }

    function _claim(address _user, uint256 _amount) internal {
        require(token.balanceOf(address(this)) >= _amount, "Insufficient rewards in the contract");
        token.transfer(_user, _amount);
    }

    function _updatePool() internal {
        if (totalStaked == 0) {
            lastRewardBlock = block.number;
            return;
        }
        uint256 blockReward = (block.number - lastRewardBlock) * rewardRate;
        accTokenPerShare += blockReward * 1e12 / totalStaked;
        lastRewardBlock = block.number;
    }

    function _pendingRewards(address _user) internal view returns (uint256) {
        return _userPendingRewards(_user) - rewardDebt[_user];
    }

    function _userPendingRewards(address _user) internal view returns (uint256) {
        return stakedAmounts[_user] * accTokenPerShare / 1e12;
    }

    function getStakingInfo(address _user) external view returns (uint256, uint256, uint256) {
        return (stakedAmounts[_user], _pendingRewards(_user), totalStaked);
    }

    function setRewardRate(uint256 _rate) external onlyOwner {
        rewardRate = _rate;
    }
}
