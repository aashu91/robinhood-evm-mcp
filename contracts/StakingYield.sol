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
    event RewardsClaimed(address indexed user, uint256 amount);

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
            _claimRewards(msg.sender, pending);
            emit RewardsClaimed(msg.sender, pending);
        }
    }

    function _updatePool() internal {
        if (totalStaked == 0) {
            lastRewardBlock = block.number;
            return;
        }
        uint256 blockReward = (block.number - lastRewardBlock) * rewardRate;
        if (blockReward > 0) {
            accTokenPerShare += blockReward * 1e12 / totalStaked;
        }
        lastRewardBlock = block.number;
    }

    function _stake(address _user, uint256 _amount) internal {
        require(token.transferFrom(_user, address(this), _amount), "Transfer failed");
        stakedAmounts[_user] += _amount;
        totalStaked += _amount;
        rewardDebt[_user] = stakedAmounts[_user] * accTokenPerShare / 1e12;
    }

    function _unstake(address _user, uint256 _amount) internal {
        require(stakedAmounts[_user] >= _amount, "Insufficient staked amount");
        stakedAmounts[_user] -= _amount;
        totalStaked -= _amount;
        require(token.transfer(_user, _amount), "Transfer failed");
        rewardDebt[_user] = stakedAmounts[_user] * accTokenPerShare / 1e12;
    }

    function _claimRewards(address _user, uint256 _pending) internal {
        require(token.transfer(_user, _pending), "Transfer failed");
    }

    function _pendingRewards(address _user) internal view returns (uint256) {
        uint256 _accTokenPerShare = accTokenPerShare;
        uint256 _lpSupply = totalStaked;
        if (block.number > lastRewardBlock && _lpSupply!= 0) {
            uint256 blockReward = (block.number - lastRewardBlock) * rewardRate;
            _accTokenPerShare += blockReward * 1e12 / _lpSupply;
        }
        return stakedAmounts[_user] * _accTokenPerShare / 1e12 - rewardDebt[_user];
    }

    function getStakingInfo(address _user) external view returns (uint256, uint256, uint256) {
        return (
            stakedAmounts[_user],
            _pendingRewards(_user),
            totalStaked
        );
    }
}
