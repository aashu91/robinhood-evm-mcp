const { expect } = require('chai');
const { ethers } = require('hardhat');

describe('CommunityTrust', function () {
    let communityTrust, goldOracle, silverOracle;

    beforeEach(async function () {
        const [deployer] = await ethers.getSigners();
        const GoldOracle = await ethers.getContractFactory('MockChainlinkOracle');
        const SilverOracle = await ethers.getContractFactory('MockChainlinkOracle');
        goldOracle = await GoldOracle.deploy(1800 * 1e8); // 1800 USD per gram
        silverOracle = await SilverOracle.deploy(25 * 1e8); // 25 USD per gram
        const CommunityTrust = await ethers.getContractFactory('CommunityTrust');
        communityTrust = await CommunityTrust.deploy(goldOracle.address, silverOracle.address);
    });

    it('should get the latest gold price', async function () {
        const goldPrice = await communityTrust.getLatestGoldPrice();
        expect(goldPrice).to.equal(1800 * 1e8);
    });

    it('should get the latest silver price', async function () {
        const silverPrice = await communityTrust.getLatestSilverPrice();
        expect(silverPrice).to.equal(25 * 1e8);
    });
});