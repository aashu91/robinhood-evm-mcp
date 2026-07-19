const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("StakingYield", function () {
    let stakingYield, token, owner, user1, user2;

    beforeEach(async function () {
        [owner, user1, user2] = await ethers.getSigners();

        const Token = await ethers.getContractFactory("MockToken");
        token = await Token.deploy("MockToken", "MTK", 1000000000000000000000); // 1000 tokens
        await token.deployed();

        const StakingYield = await ethers.getContractFactory("StakingYield");
        stakingYield = await StakingYield.deploy(token.address);
        await stakingYield.deployed();

        await token.transfer(user1.address, 100000000000000000000); // 100 tokens
        await token.transfer(user2.address, 100000000000000000000); // 100 tokens
    });

    describe("Staking", function () {
        it("should allow users to stake tokens", async function () {
            await token.connect(user1).approve(stakingYield.address, 10000000000000000000); // 10 tokens
            await stakingYield.connect(user1).stake(10000000000000000000); // 10 tokens

            const stakedAmount = await stakingYield.stakedAmounts(user1.address);
            expect(stakedAmount).to.equal(10000000000000000000);
        });

        it("should allow users to unstake tokens", async function () {
            await token.connect(user1).approve(stakingYield.address, 10000000000000000000); // 10 tokens
            await stakingYield.connect(user1).stake(10000000000000000000); // 10 tokens

            await stakingYield.connect(user1).unstake(5000000000000000000); // 5 tokens

            const stakedAmount = await stakingYield.stakedAmounts(user1.address);
            expect(stakedAmount).to.equal(5000000000000000000);
        });

        it("should allow users to claim rewards", async function () {
            await token.connect(user1).approve(stakingYield.address, 10000000000000000000); // 10 tokens
            await stakingYield.connect(user1).stake(10000000000000000000); // 10 tokens

            await network.provider.send("evm_increaseTime", [86400]); // Increase time by 1 day
            await network.provider.send("evm_mine");

            await stakingYield.connect(user1).claimRewards();

            const balance = await token.balanceOf(user1.address);
            expect(balance).to.be.greaterThan(10000000000000000000);
        });
    });
});
