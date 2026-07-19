// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract CommunityTrust {
    // Chainlink Price Feed Contracts
    AggregatorV3Interface internal goldPriceFeed;
    AggregatorV3Interface internal silverPriceFeed;

    // Constructor to set the Chainlink price feed addresses
    constructor(
        address _goldPriceFeed,
        address _silverPriceFeed
    ) {
        goldPriceFeed = AggregatorV3Interface(_goldPriceFeed);
        silverPriceFeed = AggregatorV3Interface(_silverPriceFeed);
    }

    // Function to get the latest Gold price
    function getGoldPrice() public view returns (int256) {
        (, int256 price,,,) = goldPriceFeed.latestRoundData();
        return price;
    }

    // Function to get the latest Silver price
    function getSilverPrice() public view returns (int256) {
        (, int256 price,,,) = silverPriceFeed.latestRoundData();
        return price;
    }

    // Other existing functions...
}