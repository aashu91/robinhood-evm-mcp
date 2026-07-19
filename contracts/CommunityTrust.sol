// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract CommunityTrust {
    // Chainlink Oracle addresses for XAU/USD and XAG/USD
    AggregatorV3Interface internal goldOracle;
    AggregatorV3Interface internal silverOracle;

    // Constructor to set the oracle addresses
    constructor(address _goldOracle, address _silverOracle) {
        goldOracle = AggregatorV3Interface(_goldOracle);
        silverOracle = AggregatorV3Interface(_silverOracle);
    }

    // Function to get the latest Gold price
    function getLatestGoldPrice() public view returns (int256) {
        (, int256 price,,, ) = goldOracle.latestRoundData();
        return price; // Price is in USD with 8 decimals
    }

    // Function to get the latest Silver price
    function getLatestSilverPrice() public view returns (int256) {
        (, int256 price,,, ) = silverOracle.latestRoundData();
        return price; // Price is in USD with 8 decimals
    }

    // Other functions and state variables...
}